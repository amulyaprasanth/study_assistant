import sys
from src.study_assistant import logger,CustomException
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY"," ")


class LLM:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.model_name = model_name
        
    def get_llm(self):
        try:
            logger.info("initializing llm...")
            return ChatGroq(model=self.model_name)
        except Exception as e:
            raise CustomException(f"error initializing model:{e}",sys)

if __name__ == "__main__":
    llm_obj = LLM()
    llm = llm_obj.get_llm()
    print(llm.invoke("What is the capital of India"))
    
