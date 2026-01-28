from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column

from packs.database.db import Base


class Pack(Base):
    __tablename__ = 'pack'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(127), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    #reverse for cards