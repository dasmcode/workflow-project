import fitz
from app.models.jobs import Job
from app.models.files import Files
from app.core.database import SessionLocal
from app.core.openai_client import client
import tiktoken


def extract_text(job: Job):
    try:
        db = SessionLocal()
        file = db.query(Files).filter(Files.id == job.file_id).first()
        file_path = file.filepath

    except Exception as e:
        raise Exception(f"Error occurred while extracting text: {str(e)}")
    finally:
        db.close()

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def chunk_text(text:str,chunk_size = 500, overlap = 80):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

