import os
from pydantic import SecretStr
from dotenv import load_dotenv

from langchain_groq import ChatGroq

load_dotenv()

class Config:
    def __init__(self):
        self.URL = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        
    def get_oss_llm(self) -> ChatGroq:
        llm = ChatGroq(
            api_key = SecretStr(self.GROQ_API_KEY), # type: ignore
            model = 'openai/gpt-oss-120b', 
            temperature = 0.4
        )

        return llm
    
