import os
from pathlib import Path

from pydantic.v1 import BaseSettings


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    PACKS_DATABASE_URL: str


settings = Settings()

