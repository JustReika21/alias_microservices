from cards.settings import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(settings.CARDS_DATABASE_USER_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
