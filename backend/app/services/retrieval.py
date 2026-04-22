from app.models.jobs import Job
from app.services.embedding_steps import search_similar
from app.core.openai_client import client
from app.services.cancel_service import check_cancel
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
import logging

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
    except:
        return chunks[:5]

    reranked = [chunks[i] for i in indices if i < len(chunks)]

    return reranked[:5]


def call_llm_with_context(user_prompt: str, system_prompt: str):
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def call_llm_with_context_streaming(user_prompt: str, system_prompt: str):
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
            yield chunk.choices[0].delta.content


async def stream_response_async(db: Session, job: Job, query: str = ""):
    try:
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return
        response = client.embeddings.create(
            model="text-embedding-3-small", input=query, dimensions=1024
        )
        query_embedding = response.data[0].embedding
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "query"},
            )
            return
        relevant_chunks = search_similar(job, query_embedding, 20, 0.40)
        top_chunks = rerank_chunks(query, relevant_chunks)
        logging.info(
            f"Reranking completed for job ID {job.id}. Input chunks: {len(relevant_chunks)}, Output chunks: {len(top_chunks)}",
            extra={
                "job_id": str(job.id),
                "step_name": "rerank",
            },
        )
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
        yield f"[ERROR: {str(e)}]"


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
        relevant_chunks = search_similar(job, query_embedding)
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
