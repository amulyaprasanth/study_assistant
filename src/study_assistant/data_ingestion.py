import os
import sys
from src.study_assistant import logger, CustomException
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader, Docx2txtLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.study_assistant import CustomException

class DataIngestion:
    def __init__(self, chunksize: int = 500, chunk_overlap: int = 50) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunksize, chunk_overlap=chunk_overlap)

    def load_doc(self, filepath: str):

        # Create temporary file
        _, suffix = os.path.splitext(filepath)

        # Choose loader
        if suffix == ".pdf":
            loader = PyPDFLoader(filepath)

        elif suffix == ".docx":
            loader = Docx2txtLoader(filepath)

        elif suffix.lower() in [".png", ".jpg", ".jpeg"]:
            loader = UnstructuredImageLoader(filepath)

        else:
            raise FileNotFoundError(
                "Invalid File type, Please use pdf, doc, png, jpeg and jpg files")
            
        try:
            logger.info(f"Loading docs from {filepath}")
            docs = loader.load()
            splits = self.text_splitter.split_documents(docs)
        except Exception as e:
            raise CustomException(f"Error loading docs:{e}", sys)
        
        return splits

        