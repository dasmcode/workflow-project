import numpy as np
from typing import List, Dict, Any
from app.core.qdrant_client import client as qdrant_client, QDRANT_COLLECTION
from app.core.database import SessionLocal
from app.core.openai_client import client
from app.services.embedding_steps import search_similar
import os
from sqlalchemy import text

CHUNKS_TABLE = os.getenv("CHUNKS_TABLE")


class HybridRetriever:
    def __init__(self):
        self.qdrant = qdrant_client

    async def get_semantic_results(self, query: str, job_id: str, limit: int = 20):
        response = client.embeddings.create(
            model="text-embedding-3-small", input=query, dimensions=1024
        )
        query_embedding = response.data[0].embedding
        relevant_chunks = search_similar(job_id, query_embedding, limit)
        return relevant_chunks

    async def get_bm25_results(self, query: str, job_id: str, limit: int = 20):
        db = SessionLocal()
        query = text(
            f"""SELECT * FROM "{CHUNKS_TABLE}" WHERE job_id=:job_id ORDER BY content <@> :query LIMIT :limit;"""
        )
        row = db.execute(query, {"job_id": job_id, "query": query, "limit": limit})
        response = client.embeddings.create(
            model="text-embedding-3-small", input=query, dimensions=1024
        )
        query_embedding = response.data[0].embedding
        relevant_chunks = search_similar(job_id, query_embedding, limit)
        return relevant_chunks
