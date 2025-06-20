from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import os
from src.utils.logger import Logger
from typing import Any
logger = Logger(__name__)


class QdrantVectorDB:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.client = QdrantClient(url=self.url)
        self.vector_name = "default"
    
    def _check_collection(self):
        try:
            collections = self.client.get_collections().model_dump().get("collections")
            logger.info(f"Collections: {collections}")
            return True
        except Exception as e:
            print(f"❌ Failed to check collection: {e}")
            return False

    def create_collection(self, collection_name:str, vector_size:int=128) -> Any:
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    self.vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                        ),
                }
            )
            logger.info(f"Created collection {collection_name}")
        except FileExistsError:
            logger.warning(f"Collection {collection_name} already exists")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")

    def upsert(self, collection_name: str, documents: list[str]) -> Any:
        try:
            vectors = self.embedding_model.encode(documents).tolist()
            points = [
                models.PointStruct(
                    id=i,
                    vector={self.vector_name: vectors[i]},
                    payload={"text": documents[i]}
                ) for i in range(len(documents))
            ]
            self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True
            )
            logger.info(f"✅ Upserted {len(points)} points to collection {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to upsert: {e}")


    def query(self, collection_name: str, query_text: str, limit: int = 3) -> Any:
        try:
            vector = self.embedding_model.encode(query_text).tolist()
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                with_payload=True
            )
            logger.info(f"✅ Retrieved {len(results)} results from collection {collection_name}")
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query: {e}")
            return None

    def delete_collection(self, collection_name: str) -> Any:
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted collection {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")