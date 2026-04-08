import fitz
from app.models.jobs import Job
from app.models.files import Files
from app.core.database import SessionLocal
import tiktoken
from app.services.cancel_service import check_cancel
import logging
logger = logging.getLogger(__name__)

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


def chunk_text(job:Job,text:str,chunk_size = 500, overlap = 80):
    try:
        db = SessionLocal()
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap):
            if check_cancel(db, job):
                logger.info(f"Job with id {job.id} has been cancelled")
                return False
            chunk_tokens = tokens[i : i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks
    except Exception as e:
        logger.error(f"Error occurred while chunking text for job ID {job.id}: {str(e)}")
        return False
    finally:
        db.close()



