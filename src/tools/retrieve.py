from src.RAG.qdrant_vectordb import QdrantVectorDB
from src.utils.logger import Logger
logger = Logger(__name__)
from langchain_core.tools import tool, Tool
from sentence_transformers import CrossEncoder

class RetrieveData:
    def __init__(self):
        self.qdrant = QdrantVectorDB()
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.use_reranking = True
            
    def retrieve(self, collection_name:str, query_text:str, limit:int=10, final_limit:int=3):
        try:
            # Get more results than needed for reranking
            results = self.qdrant.query(collection_name, query_text, limit)
            
            if self.use_reranking and results and not isinstance(results, str):
                # Prepare passages for reranking
                passages = [point["payload"]["text"] for point in results]
                pairs = [[query_text, passage] for passage in passages]
                
                # Rerank with cross-encoder
                scores = self.reranker.predict(pairs)
                
                # Sort by reranker scores
                reranked_results = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
                return [item[0] for item in reranked_results[:final_limit]]
            
            return results[:final_limit] if not isinstance(results, str) else results
        except Exception as e:
            logger.error(f"Failed to retrieve: {e}")
            return None

@tool
def retrieve_data_giao_an(query_text: str,limit: int = 3):
   """
    Retrieves relevant data based on a query from a specified collection in the vector database.
    If collection_name is not provided, the tool will attempt to infer the best collection
    from the available ones.
    """
   collection_name="giao_an_collection"
   retrieve_data = RetrieveData()
   results = retrieve_data.retrieve(collection_name, query_text, limit)
   logger.info(f"Retrieved results from collection {collection_name}")
   return results

@tool
def get_all_collections():
    """Get list names of collections in database"""
    return RetrieveData().qdrant.get_all_collections()

