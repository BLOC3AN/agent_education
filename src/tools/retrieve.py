from src.RAG.qdrant_vectordb import QdrantVectorDB
from src.utils.logger import Logger
logger = Logger(__name__)
from langchain_core.tools import tool, Tool
from sentence_transformers import CrossEncoder
import os
import time
from functools import lru_cache

# Tải model reranker một lần duy nhất
@lru_cache(maxsize=1)
def get_reranker():
    logger.info("Loading reranker model...")
    start_time = time.time()
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    logger.info(f"Reranker model loaded in {time.time() - start_time:.2f}s")
    return reranker

class RetrieveData:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RetrieveData, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.qdrant = QdrantVectorDB()
        # Lazy loading reranker - chỉ tải khi cần
        self._reranker = None
        self.use_reranking = True
        # Cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 giờ (tính bằng giây)
        self.cache_size_limit = 100  # Giảm kích thước cache
        self._initialized = True
    
    @property
    def reranker(self):
        if self._reranker is None and self.use_reranking:
            self._reranker = get_reranker()
        return self._reranker
            
    def retrieve(self, collection_name:str, query_text:str, limit:int=5, final_limit:int=3):
        try:
            # Kiểm tra cache trước
            cache_key = f"{collection_name}:{query_text}:{limit}:{final_limit}"
            current_time = time.time()
            
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if current_time - cache_entry["timestamp"] < self.cache_ttl:
                    logger.info("Retrieved from cache")
                    return cache_entry["results"]
            
            # Đặt timeout
            start_time = time.time()
            max_time = 2.0  # Tối đa 2 giây
            
            # Truy vấn Qdrant với số lượng kết quả giảm xuống
            results = self.qdrant.query(collection_name, query_text, limit)
            
            # Kiểm tra thời gian và kết quả
            if time.time() - start_time > max_time or not results or isinstance(results, str):
                logger.warning(f"Retrieval took too long or failed: {time.time() - start_time:.2f}s")
                if not isinstance(results, str) and results:
                    formatted_results = [{"content": item["payload"]["text"], "source": item["payload"].get("file", "Unknown")} 
                                        for item in results[:final_limit]]
                    # Lưu vào cache
                    self.cache[cache_key] = {"results": formatted_results, "timestamp": current_time}
                    return formatted_results
                return []
            
            # Reranking nếu có thời gian và kết quả
            if self.use_reranking and self.reranker and not isinstance(results, str) and results:
                # Chỉ rerank nếu có nhiều hơn final_limit kết quả
                if len(results) > final_limit:
                    passages = [point["payload"]["text"] for point in results]
                    pairs = [[query_text, passage] for passage in passages]
                    
                    # Rerank
                    scores = self.reranker.predict(pairs)
                    reranked_results = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
                    
                    # Format kết quả
                    formatted_results = []
                    for item, score in reranked_results[:final_limit]:
                        source = item["payload"].get("file", "Unknown source")
                        formatted_results.append({
                            "content": item["payload"]["text"],
                            "source": source,
                            "relevance_score": float(score)
                        })
                else:
                    # Không đủ kết quả để rerank
                    formatted_results = []
                    for item in results[:final_limit]:
                        source = item["payload"].get("file", "Unknown source")
                        formatted_results.append({
                            "content": item["payload"]["text"],
                            "source": source
                        })
            else:
                # Không rerank
                formatted_results = []
                for item in results[:final_limit]:
                    source = item["payload"].get("file", "Unknown source")
                    formatted_results.append({
                        "content": item["payload"]["text"],
                        "source": source
                    })
            
            # Lưu vào cache
            if len(self.cache) >= self.cache_size_limit:
                # Xóa entry cũ nhất
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
                del self.cache[oldest_key]
                
            self.cache[cache_key] = {"results": formatted_results, "timestamp": current_time}
            
            return formatted_results
        except Exception as e:
            logger.error(f"Failed to retrieve: {e}")
            return []

@tool
def retrieve_data_giao_an(query_text: str, limit: int = 3):
   """
    Retrieves relevant data based on a query from a specified collection in the vector database.
    """
   collection_name=os.getenv("COLLECTION_GIAO_AN","giao_an_collection")
   retrieve_data = RetrieveData()
   
   # Giảm số lượng kết quả ban đầu và final_limit
   results = retrieve_data.retrieve(collection_name, query_text, limit=3, final_limit=limit)
   
   # Nếu không có kết quả, trả về thông báo
   if not results:
       return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
       
   logger.info(f"Retrieved {len(results)} results from collection {collection_name}")
   return results

@tool
def get_all_collections():
    """Get list names of collections in database"""
    return RetrieveData().qdrant.get_all_collections()

