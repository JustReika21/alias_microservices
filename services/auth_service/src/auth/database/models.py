from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column
from auth.database.db import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    password: Mapped[bytes] = mapped_column(nullable=False)
