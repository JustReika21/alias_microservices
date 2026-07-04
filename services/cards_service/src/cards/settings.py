from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CARDS_DATABASE_URL: str


settings = Settings()
