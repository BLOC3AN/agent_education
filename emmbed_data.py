from dotenv import load_dotenv  
load_dotenv()
import os 
from src.RAG.embedded_data import emmbeded_data_folder
from src.RAG.qdrant_vectordb import QdrantVectorDB
from src.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger(__name__)
    folder = os.getenv("FOLDER_PATH_DOCUMENT", "../data/RAG")
    collection_name = os.getenv("COLLECTION_NAME_DOCUMENT", "collection_name")

    qdrant = QdrantVectorDB()
    if not qdrant.check_collection(collection_name):
        logger.info(f"Creating collection {collection_name}")
        qdrant.create_collection(collection_name, vector_size=384)
        logger.info(f"Created collection {collection_name}")
    else:
        logger.info(f"Collection {collection_name} already exists")
    logger.info(f"Emmbeding data from {folder} to collection {collection_name}")
    emmbeded_data_folder(folder, collection_name)
