from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from packs.settings import settings


engine = create_async_engine(settings.database_url)

async_session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass

class AliasBase(BaseModel):
    pass
