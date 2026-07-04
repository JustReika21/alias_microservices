import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    redis_password: str = os.getenv('REDIS_PASSWORD')
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: int = os.getenv('REDIS_PORT')


settings = Settings()
