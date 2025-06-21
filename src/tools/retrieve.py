from src.RAG.qdrant_vectordb import QdrantVectorDB
from src.utils.logger import Logger
logger = Logger(__name__)
from langchain_core.tools import tool


class RetrieveData:
    def __init__(self):
        self.qdrant = QdrantVectorDB()
        
    def retrieve(self, collection_name:str, query_text:str, limit:int=3):
        try:
            results = self.qdrant.query(collection_name, query_text, limit)
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve: {e}")
            return None

@tool
def retrieve_data(query_text: str,collection_name:str = "document",  limit: int = 3):
   """Retrieve data from a collection"""
   retrieve_data = RetrieveData()
   results = retrieve_data.retrieve(collection_name, query_text, limit)
   logger.info(f"Retrieved results from collection {collection_name}")
   return results
