import sqlite3
import requests
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Config

from langchain_community.utilities.sql_database import SQLDatabase

config = Config()

def get_engine_chinook_db():
     url = Config().URL
     response =  requests.get(url)
     sql_script = response.text

     connection = sqlite3.connect(':memory:', check_same_thread=False)

     connection.executescript(sql_script)

     return create_engine(
          "sqlite://",
          creator = lambda : connection,
          poolclass = StaticPool,
          connect_args = {"check_same_thread": False} 
     )

engine = get_engine_chinook_db()

db = SQLDatabase(engine)


