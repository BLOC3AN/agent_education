from qdrant_client import QdrantClient, models
import os
from src.utils.logger import Logger
from typing import Any, List
logger = Logger(__name__)


class QdrantVectorDB:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=self.url)
        self.vector_name = "dense"
        self.model_emmbedding = "BAAI/bge-small-en"

        logger.info(f"""
            QdrantVectorDB initialized with:
            - URL: {self.url}
            - Vector name: {self.vector_name}
            - Model embedding: {self.model_emmbedding}
        """)
    # Check if collection exists
    def  check_collection(self,collection_name:str):
        try:
            collections = self.client.get_collections().model_dump().get("collections")
            if {'name':collection_name} in collections: #type:ignore
                logger.info(f"Collection `{collection_name}` already exists")
                return True
            logger.warning(f"Collection `{collection_name}` does not exist")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to check collection: {e}")
            return False

    def create_collection(self, collection_name:str, vector_size:int=128) -> Any:
        """Create a collection"""
        if self.check_collection(collection_name):
            logger.error(f"❌ Collection {collection_name} already exists")
            return False
        
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
            dense_documents = [
                models.Document(text=doc, model="BAAI/bge-small-en")
                for doc in documents
            ]
            points = [
                models.PointStruct(
                    id=i,
                    vector={
                        self.vector_name : dense_documents[i],
                    },
                    payload={"text": documents[i]}
                ) for i in range(len(documents))
            ]
            self.client.upsert(collection_name=collection_name, points=points)
            logger.info(f"✅ Upserted {len(points)} points to collection {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to upsert: {e}")


    def query(self, collection_name: str, query_text: str, limit: int = 3) -> Any:
        """Query a collection"""
        if not self.check_collection(collection_name):
            logger.error(f"❌ Collection {collection_name} does not exist")
            return False
        
        try:
            dense_query = models.Document(text=query_text, model=self.model_emmbedding)
            results = self.client.query_points(
                collection_name=collection_name,
                prefetch=models.Prefetch(
                    query=dense_query,
                    using="dense",
                ),
                query=dense_query,
                using="dense",
                limit=limit,
                with_payload=True
            ).model_dump().get("points")
            logger.info(f"✅ Retrieved results from collection {collection_name}")
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