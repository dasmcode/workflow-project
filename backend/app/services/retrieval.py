from app.models.jobs import Job
from app.services.embedding_steps import search_similar
from app.core.openai_client import client
from app.services.cancel_service import check_cancel
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
import logging, asyncio, time
from app.utils.retrieval_utils import HybridRetriever
from app.core.metrics import (
    RAG_RETRIEVAL_COUNT,
    RAG_RERANK_INPUT,
    RAG_RERANK_OUTPUT,
    LLM_TTFT,
    LLM_STREAM_DURATION,
    LLM_REQUESTS,
)

logger = logging.getLogger(__name__)


def rerank_chunks(query: str, chunks: list[str]):
    joined_chunks = "\n\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(chunks)])

    prompt = f"""
You are a ranking assistant.

Given a query and list of document chunks,
rank the chunks from most relevant to least relevant.

Return ONLY the indices in order (example: 3,1,2).

Query:
{query}

Chunks:
{joined_chunks}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )

    ranking = response.choices[0].message.content.strip()

    try:
        indices = [int(x.strip()) - 1 for x in ranking.split(",")]
    except Exception as e:
        logger.info(
            f"Failed to rerank chunks for query: {e}\nFalling back to first 5 chunks"
        )
        return chunks[:5]

    reranked = [chunks[i] for i in indices if i < len(chunks)]

    return reranked[:5]


def call_llm_with_context(user_prompt: str, system_prompt: str):
    start_time = time.time()
    first_token_time = None
    LLM_REQUESTS.inc()
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def call_llm_with_context_streaming(user_prompt: str, system_prompt: str):
    start_time = time.time()
    first_token_time = None
    LLM_REQUESTS.inc()
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            if first_token_time is None:
                first_token_time = time.time()
                LLM_TTFT.observe(first_token_time - start_time)
            yield chunk.choices[0].delta.content
    LLM_STREAM_DURATION.observe(time.time() - start_time)


async def stream_response_async(db: Session, job: Job, query: str = ""):
    retriever = HybridRetriever()
    try:
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return

        semantic_results, bm25_results = await asyncio.gather(
            retriever.get_semantic_results(query, str(job.id), 25),
            retriever.get_bm25_results(query, str(job.id), 25),
        )
        if not semantic_results or not bm25_results:
            raise ValueError(
                f"Either semantic or bm25 results not found: {semantic_results}, {bm25_results}"
            )
        logger.info(
            f"Retrieval completed for job ID {job.id}. Semantic results: {len(semantic_results)}, BM25 results: {len(bm25_results)}",
            extra={
                "job_id": str(job.id),
                "step_name": "query",
            },
        )
        rrf_fused_results = retriever.fuse_results(
            semantic_results, bm25_results, alpha=0.5
        )
        if not rrf_fused_results:
            raise ValueError("No rrf fused results found")
        logger.info(
            f"Fusion completed for job ID {job.id}. Input chunks: {len(rrf_fused_results)}",
            extra={
                "job_id": str(job.id),
                "step_name": "query",
            },
        )
        RAG_RETRIEVAL_COUNT.observe(len(rrf_fused_results))
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return
        RAG_RERANK_INPUT.observe(len(rrf_fused_results))
        top_chunks = rerank_chunks(query, rrf_fused_results[:10])
        logging.info(
            f"Reranking completed for job ID {job.id}. Input chunks: {len(rrf_fused_results)}, Output chunks: {len(top_chunks)}",
            extra={
                "job_id": str(job.id),
                "step_name": "rerank",
            },
        )
        RAG_RERANK_OUTPUT.observe(len(top_chunks))
        context = "\n".join(top_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        system_prompt = "You are a helpful assistant that answers questions based on the provided context."
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return
        for chunk in call_llm_with_context_streaming(prompt, system_prompt):
            yield chunk
    except Exception as e:
        job_id = str(job.id) if hasattr(job, "id") else "unknown"
        logger.error(
            f"Streaming error: {str(e)}",
            extra={"job_id": job_id, "step_name": "query"},
        )
        yield f"[ERROR]"


def stream_response(db: Session, job: Job, query: str = ""):
    try:
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return False
        response = client.embeddings.create(model="text-embedding-3-small", input=query)
        query_embedding = response.data[0].embedding
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return False
        relevant_chunks = search_similar((job.id), query_embedding)
        context = "\n".join(relevant_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        system_prompt = "You are a helpful assistant that answers questions based on the provided context."
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return False
        for chunk in call_llm_with_context_streaming(prompt, system_prompt):
            yield chunk
    except Exception as e:
        job_id = str(job.id) if hasattr(job, "id") else "unknown"
        logger.error(
            f"Streaming error: {str(e)}",
            extra={"job_id": job_id, "step_name": "query"},
        )
        yield f"[ERROR: {str(e)}]"


def query_summarize(
    job_id: str, query: str = "Summarize this document", context: str = ""
):
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(
                f"Job with id {job_id} not found",
                extra={"job_id": job_id, "step_name": "summarize"},
            )
            raise ValueError("Job not found")
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "summarize"},
            )
            return False
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        system_prompt = "You are a helpful assistant that answers questions based on the provided context."
        answer = call_llm_with_context(prompt, system_prompt)
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "summarize"},
            )
            return False
        return answer
    except Exception as e:
        logger.error(
            f"Error during summarize query for job ID {job.id}: {str(e)}",
            extra={"job_id": str(job.id), "step_name": "summarize"},
        )
        raise Exception(f"Error occurred during summarization: {str(e)}")
