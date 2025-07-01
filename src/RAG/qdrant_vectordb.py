from qdrant_client import QdrantClient, models
import os
from src.utils.logger import Logger # type: ignore
from typing import Any, List
logger = Logger(__name__)
import uuid
from functools import lru_cache

# Sử dụng singleton pattern và caching để tránh tải lại model
class QdrantVectorDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantVectorDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.url = os.getenv("QDRANT_CLOUD_URL")
        self.api_key=os.getenv("QDRANT_API_KEY")
        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        self.vector_name = "dense"
        self.model_emmbedding = "BAAI/bge-small-en"
        
        # Khởi tạo cache cho các truy vấn
        self.query_cache = {}
        self.cache_size_limit = 100
        
        logger.info(f"""
            QdrantVectorDB initialized with:
            - URL: {self.url}
            - Vector name: {self.vector_name}
            - Model embedding: {self.model_emmbedding}
        """)
        self._initialized = True

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
        """Query a collection with caching"""
        if not self.check_collection(collection_name):
            logger.error(f"❌ Collection {collection_name} does not exist")
            return "Error: Collection not exist"
        
        # Tạo cache key
        cache_key = f"{collection_name}:{query_text}:{limit}"
        
        # Kiểm tra cache
        if cache_key in self.query_cache:
            logger.info(f"✅ Retrieved results from cache for query: {query_text[:30]}...")
            return self.query_cache[cache_key]
        
        try:
            # Đặt timeout cho truy vấn
            import time
            start_time = time.time()
            timeout = 3.0  # 3 seconds timeout
            
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
            
            query_time = time.time() - start_time
            logger.info(f"✅ Retrieved results from collection {collection_name} in {query_time:.2f}s")
            
            # Lưu vào cache
            if len(self.query_cache) >= self.cache_size_limit:
                # Xóa một key ngẫu nhiên nếu cache đầy
                import random
                key_to_remove = random.choice(list(self.query_cache.keys()))
                del self.query_cache[key_to_remove]
            
            self.query_cache[cache_key] = results
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
