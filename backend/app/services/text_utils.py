from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from docling_core.types.doc.document import DoclingDocument
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
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "extract_text"},
            )
            return False
        pipeline_options = PdfPipelineOptions()
        pipeline_options.ocr_options = TesseractOcrOptions()
        pipeline_options.do_table_structure = True
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(file_path)
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "extract_text"},
            )
            return False
        extracted_dict = result.document.export_to_dict()
        extracted_text = result.document.export_to_markdown()
        if job.workflow_type == "summarization":
            return extracted_text
        return extracted_dict

    except Exception as e:
        raise Exception(f"Error occurred while extracting text: {str(e)}")
    finally:
        db.close()


def chunk_text(job: Job, extracted_dict: dict, chunk_size=500, overlap=80):
    try:
        db = SessionLocal()
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "chunk"},
            )
            return False
        doc = DoclingDocument.model_validate(extracted_dict)
        tokenizer = OpenAITokenizer(
            tokenizer=tiktoken.encoding_for_model("text-embedding-3-small"),
            max_tokens=chunk_size,
        )
        chunker = HybridChunker(
            tokenizer=tokenizer,
            max_tokens=chunk_size,
            repeat_table_header=True,
            omit_header_on_overflow=True,
        )
        if check_cancel(db, job):
            logger.info(
                f"Job with id {job.id} has been cancelled",
                extra={"job_id": str(job.id), "step_name": "chunk"},
            )
            return False
        doc_chunks = chunker.chunk(dl_doc=doc)
        chunks = []
        for i, chunk in enumerate(doc_chunks):
            if check_cancel(db, job):
                logger.info(
                    f"Job with id {job.id} has been cancelled",
                    extra={"job_id": str(job.id), "step_name": "chunk"},
                )
                return False
            enriched_text = chunker.contextualize(chunk)
            chunks.append(enriched_text)
        return chunks
    except Exception as e:
        logger.error(
            f"Error occurred while chunking text for job ID {job.id}: {str(e)}",
            extra={"job_id": str(job.id), "step_name": "chunk"},
        )
        raise Exception(f"Error occurred while chunking text: {str(e)}")
    finally:
        db.close()
