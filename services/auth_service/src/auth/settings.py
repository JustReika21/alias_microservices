import os
from pathlib import Path

from auth.schemas.schemas import AuthBase
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

ACCESS_TOKEN_TTL = 15
REFRESH_TOKEN_TTL = 60 * 24 * 30


class AuthJWT(AuthBase):
    private_key_path: Path = BASE_DIR / 'certs/jwt-private.pem'
    public_key_path: Path = BASE_DIR / 'certs/jwt-public.pem'
    algorithm: str = 'RS256'
    access_token_expire_minutes: int = ACCESS_TOKEN_TTL
    refresh_token_expire_minutes: int = REFRESH_TOKEN_TTL


class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    db_schema: str = os.getenv('DB_SCHEMA')

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
