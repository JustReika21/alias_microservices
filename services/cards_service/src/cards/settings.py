from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CARDS_DATABASE_ADMIN_URL: str
    CARDS_DATABASE_USER_URL: str


settings = Settings()
