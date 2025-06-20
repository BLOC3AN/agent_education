from dotenv import load_dotenv  
load_dotenv()
import os 
from src.RAG.embedded_data import emmbeded_data_folder
from src.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger(__name__)
    folder = os.getenv("FOLDER_PATH", "/data/RAG")
    collection_name = os.getenv("COLLECTION_NAME", "document")
    logger.info(f"Emmbeding data from {folder} to collection {collection_name}")
    emmbeded_data_folder(folder, collection_name)
