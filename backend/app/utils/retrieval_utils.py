from typing import List, Dict
from app.core.database import SessionLocal
from app.core.openai_client import client
from app.services.embedding_steps import search_similar
import os
from sqlalchemy import text
import logging

CHUNKS_TABLE = os.getenv("CHUNKS_TABLE")
logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self, k_constant: int = 60):
        self.k = k_constant

    async def get_semantic_results(self, query: str, job_id: str, limit: int = 20):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small", input=query, dimensions=1024
            )
            query_embedding = response.data[0].embedding
            relevant_chunks = search_similar(job_id, query_embedding, limit, 0.40)
            return relevant_chunks
        except Exception as e:
            logger.error(f"Error getting semantic results: {str(e)}")
            return False

    async def get_bm25_results(self, query: str, job_id: str, limit: int = 20):
        try:
            db = SessionLocal()
            index_name = f"idx_{job_id.replace('-', '_')}"
            sql_query = text(
                f"""SELECT id,content,(content <@> to_bm25query(:query,:index_name)) AS score FROM "{CHUNKS_TABLE}" 
                WHERE job_id=:job_id 
                ORDER BY score 
                LIMIT :limit;
                """
            )
            rows = db.execute(
                sql_query,
                {
                    "query": query,
                    "index_name": index_name,
                    "job_id": job_id,
                    "limit": limit,
                },
            )

            return [
                {"id": str(r["id"]), "text": r["content"], "score": float(r["score"])}
                for r in rows.mappings()
            ]
        except Exception as e:
            logger.error(f"Error getting bm25 results: {str(e)}")
            return False
        finally:
            db.close()

    def fuse_results(
        self, semantic_list: List[Dict], bm25_list: List[Dict], alpha: int = 0.5
    ):
        """
        Hybrid Search Fusion using a single weight 'w' (0.0 to 1.0).
        alpha -> 1.0: Purely Semantic (Qdrant)
        alpha -> 0.0: Purely Keyword (Postgres BM25)
        """
        fused_scores = {}
        doc_map = {}
        try:
            for rank, doc in enumerate(semantic_list):
                doc_id = doc["id"]
                score = alpha * (1 / (self.k + rank + 1))
                fused_scores[doc_id] = fused_scores.get(doc_id, 0) + score
                doc_map[doc_id] = doc["text"]

            for rank, doc in enumerate(bm25_list):
                doc_id = doc["id"]
                score = (1 - alpha) * (1 / (self.k + rank + 1))
                fused_scores[doc_id] = fused_scores.get(doc_id, 0) + score
                if doc_id not in doc_map:
                    doc_map[doc_id] = doc["text"]

            sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
            return [doc_map[doc_id] for doc_id, _ in sorted_docs]
        except Exception as e:
            logger.error(f"Error fusing results: {str(e)}")
            return False
