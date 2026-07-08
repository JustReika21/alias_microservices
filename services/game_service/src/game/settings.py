import os
from pathlib import Path

from pydantic.v1 import BaseSettings


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int


settings = Settings()
