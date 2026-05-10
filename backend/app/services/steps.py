from app.models.jobs import Job
from app.services.text_utils import extract_text, chunk_text
from app.services.embedding_steps import get_embeddings, store_embeddings
from app.services.cache_service import get_step_data, set_step_data, delete_step_data
from app.services.retrieval import query_summarize
from app.workers.retry_handler import run_with_retry
import logging
from app.core.metrics import (
    STEP_DURATION,
    STEP_FAILURES,
    LLM_REQUESTS,
    LLM_LATENCY,
)
import time

logger = logging.getLogger(__name__)


async def execute_step(step_name: str, job: Job):
    try:
        with STEP_DURATION.labels(step_name).time():
            if step_name == "extract_text":
                logger.info(
                    f"Extracting text for job ID {job.id}",
                    extra={"job_id": str(job.id), "step_name": step_name},
                )
                text = run_with_retry(lambda: extract_text(job), str(job.id), step_name)
                await set_step_data(str(job.id), step_name, text)

            elif step_name == "summarize":
                text = await get_step_data(str(job.id), "extract_text")
                logger.info(
                    f"Summarizing for job ID {job.id}",
                    extra={"job_id": str(job.id), "step_name": step_name},
                )
                try:
                    LLM_REQUESTS.inc()
                    start = time.time()
                    summary = run_with_retry(
                        lambda: query_summarize(str(job.id), context=text),
                        str(job.id),
                        step_name,
                    )
                    LLM_LATENCY.observe(time.time() - start)
                    if not summary:
                        job.result = "Summarization failed or was cancelled"
                        return
                    job.result = summary
                except Exception as e:
                    logger.error(
                        f"Error occurred while summarizing for job ID {job.id}: {str(e)}",
                        extra={"job_id": str(job.id), "step_name": step_name},
                    )
                    return

            elif step_name == "chunk":
                text = await get_step_data(str(job.id), "extract_text")
                chunks = run_with_retry(
                    lambda: chunk_text(job, text), str(job.id), step_name
                )
                if not chunks:
                    logger.info(
                        f"Chunking failed or was cancelled for job ID {job.id}",
                        extra={"job_id": str(job.id), "step_name": step_name},
                    )
                    return
                await set_step_data(str(job.id), step_name, chunks)
                await delete_step_data(str(job.id), "extract_text")

            elif step_name == "embed_and_store":
                chunks = await get_step_data(str(job.id), "chunk")
                embeddings = run_with_retry(
                    lambda: get_embeddings(str(job.id), chunks), str(job.id), step_name
                )
                if not embeddings:
                    logger.info(
                        f"Embedding failed or was cancelled for job ID {job.id}",
                        extra={"job_id": str(job.id), "step_name": step_name},
                    )
                    return
                logger.info(
                    f"Got embeddings for job ID {job.id}, now storing...",
                    extra={"job_id": str(job.id), "step_name": step_name},
                )
                stored = run_with_retry(
                    lambda: store_embeddings(str(job.id), chunks, embeddings),
                    str(job.id),
                    step_name,
                )
                if not stored:
                    logger.info(
                        f"Embedding stored failed or was cancelled for job ID {job.id}",
                        extra={"job_id": str(job.id), "step_name": step_name},
                    )
                    return
                logger.info(
                    f"Embeddings stored successfully for job ID {job.id}",
                    extra={"job_id": str(job.id), "step_name": step_name},
                )
                await delete_step_data(str(job.id), "chunk")

            elif step_name == "query":
                logger.info(
                    f"Querying for job ID {job.id}",
                    extra={"job_id": str(job.id), "step_name": step_name},
                )
                job.result = "Answer from RAG"

            else:
                raise Exception("Unknown step")
    except Exception as e:
        STEP_FAILURES.labels(step_name).inc()

        logger.error(
            f"Step {step_name} failed for job ID {job.id}: {str(e)}",
            extra={"job_id": str(job.id), "step_name": step_name},
        )
