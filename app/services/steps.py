import time
from app.models.jobs import Job
from app.models.files import Files
from app.core.database import SessionLocal


def execute_step(step_name:str, job:Job):
    if step_name == "extract_text":
        print("Extracting text...")
        time.sleep(2)

    elif step_name == "summarize":
        print("Summarizing...")
        job.result = "This is a summary"

    elif step_name == "chunk":
        print("Chunking...")
        time.sleep(1)

    elif step_name == "embed":
        print("Generating embeddings...")
        time.sleep(1)

    elif step_name == "store":
        print("Storing vectors...")
        time.sleep(1)

    elif step_name == "query":
        print("Querying...")
        job.result = "Answer from RAG"

    else:
        raise Exception("Unknown step")
