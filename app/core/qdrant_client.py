from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os

client = QdrantClient(host=os.getenv("QDRANT_SERVER", "localhost"), port=6333)

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 1024))

def create_collection(collection_name: str = QDRANT_COLLECTION, vector_size: int = VECTOR_SIZE):
    if client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' already exists.")
    else:
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            print(f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            print(f"Error occurred while creating collection '{collection_name}': {e}")
