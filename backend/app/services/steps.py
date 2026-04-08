from app.models.jobs import Job
from app.services.text_utils import extract_text,chunk_text
from app.services.embedding_steps import get_embeddings, store_embeddings
from app.services.cache_service import get_step_data, set_step_data, delete_step_data
from app.services.retrieval import query_summarize
from app.workers.retry_handler import run_with_retry
import logging
logger = logging.getLogger(__name__)


def execute_step(step_name:str, job:Job):
    if step_name == "extract_text":
        logger.info(f"Extracting text for job ID {job.id}")
        text = run_with_retry(lambda: extract_text(job), job, step_name)
        set_step_data(str(job.id), step_name, text)

    elif step_name == "summarize":
        text = get_step_data(str(job.id), "extract_text")
        logger.info(f"Summarizing for job ID {job.id}")
        try:
            summary = run_with_retry(lambda: query_summarize(job, context=text), job, step_name)
            job.result = summary    
        except Exception as e:
            logger.error(f"Error occurred while summarizing for job ID {job.id}: {str(e)}")
            return

    elif step_name == "chunk":
        text = get_step_data(str(job.id), "extract_text")
        chunks = run_with_retry(lambda: chunk_text(job, text), job, step_name)
        if not chunks:
            logger.info(f"Chunking failed or was cancelled for job ID {job.id}")
            return
        set_step_data(str(job.id), step_name, chunks)
        delete_step_data(str(job.id), "extract_text")

    elif step_name == "embed_and_store":
        chunks = get_step_data(str(job.id), "chunk")
        embeddings = run_with_retry(lambda: get_embeddings(job, chunks), job, step_name)
        if not embeddings:
            logger.info(f"Embedding failed or was cancelled for job ID {job.id}")
            return
        logger.info(f"Got embeddings for job ID {job.id}, now storing...")
        stored = run_with_retry(lambda: store_embeddings(job, chunks, embeddings), job, step_name)
        if not stored:
            logger.info(f"Embedding stored failed or was cancelled for job ID {job.id}")
            return
        logger.info(f"Embeddings stored successfully for job ID {job.id}")
        delete_step_data(str(job.id), "chunk")

    elif step_name == "query":
        logger.info(f"Querying for job ID {job.id}")
        job.result = "Answer from RAG"

    else:
        raise Exception("Unknown step")
