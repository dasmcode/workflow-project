from app.core.openai_client import client
from app.core.qdrant_client import client as qdrant_client, QDRANT_COLLECTION
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
import uuid, os
from app.models.jobs import Job
from app.models.chunks import Chunks
from app.core.database import SessionLocal
from app.services.cancel_service import check_cancel
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

CHUNKS_TABLE = os.getenv("CHUNKS_TABLE", "chunks")


def get_embeddings(job_id: str, chunks: list[str]):
    try:
        embeddings = []
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        for chunk in chunks:
            if check_cancel(db, job):
                logger.info(
                    f"Job with id {job.id} has been cancelled",
                    extra={"job_id": str(job.id), "step_name": "embed_and_store"},
                )
                return False
            response = client.embeddings.create(
                input=chunk, model="text-embedding-3-small", dimensions=1024
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        return embeddings
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error getting embeddings for job ID {job.id}: {str(e)}",
            extra={"job_id": str(job.id), "step_name": "embed_and_store"},
        )
        raise Exception(f"Error occurred while getting embeddings: {str(e)}")
    finally:
        db.close()


def delete_existing_vectors(job_id: str):
    logger.info(
        f"Deleting existing vectors for job ID: {job_id}",
        extra={"job_id": job_id, "step_name": "embed_and_store"},
    )
    qdrant_client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="job_id", match=MatchValue(value=job_id))]
        ),
    )


def store_embeddings(job_id: str, chunks: list[str], embeddings: list[list[float]]):
    try:
        delete_existing_vectors(job_id)
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        points = []
        index_name = f"idx_{str(job.id).replace('-', '_')}"
        query = text(f"""
        CREATE INDEX IF NOT EXISTS "{index_name}" ON "{CHUNKS_TABLE}" USING bm25(content) WITH (text_config='english') WHERE job_id=:job_id;
        """)
        db.execute(query, {"job_id": str(job.id)})
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            if check_cancel(db, job):
                logger.info(
                    f"Job with id {job.id} has been cancelled",
                    extra={"job_id": str(job.id), "step_name": "embed_and_store"},
                )
                return False
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{job.id}_{i}"))
            db_chunk = Chunks(id=point_id, content=chunk, job_id=str(job.id))
            db.add(db_chunk)
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={"text": chunk, "job_id": str(job.id)},
            )
            points.append(point)
        db.commit()
        qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=points)
        return True
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error occurred while storing embeddings for job ID {job.id}: {str(e)}",
            extra={"job_id": str(job.id), "step_name": "embed_and_store"},
        )
        raise Exception(f"Error occurred while storing embeddings: {str(e)}")
    finally:
        db.close()


def search_similar(
    job: Job,
    query_embedding: list[float],
    top_k: int = 5,
    SCORE_THRESHOLD: float = 0.50,
):
    search_result = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="job_id", match=MatchValue(value=str(job.id)))]
        ),
        limit=top_k,
    )
    return [
        {"id": hit.id, "text": hit.payload["text"], "score": hit.score}
        for hit in search_result.points
        if hit.score >= SCORE_THRESHOLD
    ]
