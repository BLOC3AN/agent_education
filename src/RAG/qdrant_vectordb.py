from qdrant_client import QdrantClient, models
import os
from src.utils.logger import Logger
from typing import Any, List
logger = Logger(__name__)
import uuid

class QdrantVectorDB:
    def __init__(self):
        self.url = os.getenv("QDRANT_CLOUD_URL", "https://7d15f4c4-01e3-4591-9106-b0705066ced5.us-east4-0.gcp.cloud.qdrant.io:6333")
        self.api_key=os.getenv("QDRANT_API_KEY","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.PYruiZBuq5YU8QlT92Bs0snsnrgZmth2vekIqiPYK50")
        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        self.vector_name = "dense"
        self.model_emmbedding = "BAAI/bge-small-en"

        logger.info(f"""
            QdrantVectorDB initialized with:
            - URL: {self.url}
            - Vector name: {self.vector_name}
            - Model embedding: {self.model_emmbedding}
        """)

    def get_all_collections(self) -> List|Any:
        """Get list collections in vectordb"""
        try:
            collections_name = [coll_name['name'] for coll_name in self.client.get_collections().model_dump().get("collections")] #type:ignore
            return collections_name
        except Exception as e:
            logger.error(f"Error in getting collections {str(e)}")
            return []

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
        except FileExistsError as e:
            logger.warning(f"Collection {collection_name} already exists")
            return str(e)
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return str(e)

    def upsert(self, collection_name: str, documents: list[str], file_name:str="default") -> Any:
        try:
            dense_documents = [
                models.Document(text=doc, model="BAAI/bge-small-en")
                for doc in documents
            ]
            points = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        self.vector_name : dense_documents[i],
                    },
                    payload={"text": documents[i], "file": file_name}
                ) for i in range(len(documents))
            ]
            self.client.upsert(collection_name=collection_name, points=points)
            logger.info(f"✅ Upserted {len(points)} points to collection {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to upsert: {e}")
            return str(e)


    def query(self, collection_name: str, query_text: str, limit: int = 3) -> Any:
        """Query a collection"""
        if not self.check_collection(collection_name):
            logger.error(f"❌ Collection {collection_name} does not exist")
            return "Error: Collection not exist"
        
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
            return str(e)

    def delete_collection(self, collection_name: str) -> Any:
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted collection {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")
            return str(e)