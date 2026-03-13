import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.URL = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
 
    
