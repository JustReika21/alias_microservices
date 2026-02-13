import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    db_schema: str = os.getenv('DB_SCHEMA')


settings = Settings()
