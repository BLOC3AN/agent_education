from src.RAG.qdrant_vectordb import QdrantVectorDB
from src.utils.logger import Logger
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
logger = Logger(__name__)

class EmmbededData:
    def __init__(self):
        self.vector_size = 384
        self.data = []

    def read_docx(self, filepath):
        doc = Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
        file_name = filepath.split("/")[-1].replace(" ","_").replace(".docx","")
        return text, file_name
    
    def split_text(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        return splitter.split_text(text)
    
    def emmbeded(self, filepath:str, collection_name:str):
        if not QdrantVectorDB().check_collection(collection_name):
            logger.info(f"Creating collection {collection_name}")
            QdrantVectorDB().create_collection(collection_name, vector_size=self.vector_size)
            logger.info(f"Created collection {collection_name}")
        try:
            text, file_name = self.read_docx(filepath)
            document = self.split_text(text)
            logger.info(f"Loaded {len(document)} documents from {filepath}")

            QdrantVectorDB().upsert(collection_name, document,file_name)
            logger.info(f"Upserted {len(document)} documents to collection {collection_name}")
        
        except Exception as e:
            logger.error(f"Failed to embedded data: {e}")

def emmbeded_data_folder(folder_path:str, collection_name:str):
    from glob import glob
    for filepath in glob(folder_path + "/*.docx"):
        logger.info(f"Emmbeding data from {filepath} to collection {collection_name}")
        emmbedd = EmmbededData()
        emmbedd.emmbeded(filepath, collection_name)
    logger.info(f"Emmbeded all data in {folder_path} to collection {collection_name}")
