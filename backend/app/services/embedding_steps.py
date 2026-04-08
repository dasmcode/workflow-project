from app.core.openai_client import client
from app.core.qdrant_client import client as qdrant_client, QDRANT_COLLECTION
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
import uuid
from app.models.jobs import Job
from app.core.database import SessionLocal
from app.services.cancel_service import check_cancel
import logging
logger = logging.getLogger(__name__)

def get_embeddings(job:Job,chunks:list[str]):
    embeddings = []
    db = SessionLocal()
    try:
        for chunk in chunks:
            if check_cancel(db, job):
                logger.info(f"Job with id {job.id} has been cancelled")
                return False
            response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        return embeddings
    except Exception as e:
        logger.error(f"Error getting embeddings for job ID {job.id}: {str(e)}")
        return False
    finally:
        db.close()

def store_embeddings(job:Job, chunks:list[str], embeddings:list[list[float]]):
    points = []
    db = SessionLocal()
    for chunk, embedding in zip(chunks, embeddings):
        if check_cancel(db, job):
            logger.info(f"Job with id {job.id} has been cancelled")
            return False
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk, "job_id": job.id}
        )
        points.append(point)
    qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    return True
    
def search_similar(job:Job, query_embedding:list[float], top_k:int = 5):
    search_result = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="job_id",
                    match=MatchValue(value=str(job.id))
                )
            ]
        ),
        limit=top_k
    )
    return [hit.payload["text"] for hit in search_result.points]