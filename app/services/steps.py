import time
from app.models.jobs import Job
from app.services.text_utils import extract_text,chunk_text
from app.services.embedding_steps import get_embeddings, store_embeddings
from app.services.cache_service import get_step_data, set_step_data, delete_step_data
from app.services.retrieval import query_summarize


def execute_step(step_name:str, job:Job):
    if step_name == "extract_text":
        text = extract_text(job)
        set_step_data(str(job.id), step_name, text)

    elif step_name == "summarize":
        text = get_step_data(str(job.id), "extract_text")
        print("Summarizing...")
        summary = query_summarize(job=job, context=text)
        if not summary:
            print(f"Summarization failed or was cancelled for job ID {job.id}")
            return
        job.result = summary

    elif step_name == "chunk":
        text = get_step_data(str(job.id), "extract_text")
        chunks = chunk_text(job, text)
        if not chunks:
            print(f"Chunking failed or was cancelled for job ID {job.id}")
            return
        set_step_data(str(job.id), step_name, chunks)
        delete_step_data(str(job.id), "extract_text")

    elif step_name == "embed_and_store":
        chunks = get_step_data(str(job.id), "chunk")
        embeddings = get_embeddings(job, chunks)
        if not embeddings:
            print(f"Embedding failed or was cancelled for job ID {job.id}")
            return
        print("Got embeddings, now storing...")
        stored = store_embeddings(job, chunks, embeddings)
        if not stored:
            print(f"Embedding stored failed or was cancelled for job ID {job.id}")
            return
        print("Embeddings stored successfully")
        delete_step_data(str(job.id), "chunk")

    elif step_name == "query":
        print("Querying...")
        job.result = "Answer from RAG"

    else:
        raise Exception("Unknown step")
