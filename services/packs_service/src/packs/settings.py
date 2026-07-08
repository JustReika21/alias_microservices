import os
from pathlib import Path

from pydantic.v1 import BaseSettings


BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    PACKS_DATABASE_ADMIN_URL: str
    PACKS_DATABASE_USER_URL: str


settings = Settings()

