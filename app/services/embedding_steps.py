from app.core.openai_client import client
from app.core.qdrant_client import client as qdrant_client, QDRANT_COLLECTION
from qdrant_client.models import PointStruct
import uuid
from app.models.jobs import Job

def get_embeddings(chunks:list[str]):
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        embeddings.append(embedding)
    return embeddings

def store_embeddings(job:Job, chunks:list[str], embeddings:list[list[float]]):
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk, "job_id": job.id}
        )
        points.append(point)
    qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    
def search_similar(query_embedding:list[float], top_k:int = 5):
    search_result = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=top_k
    )
    return [hit.payload["text"] for hit in search_result]