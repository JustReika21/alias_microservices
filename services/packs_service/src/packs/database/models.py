from packs.database.db import Base
from sqlalchemy import CheckConstraint, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class Pack(Base):
    __tablename__ = 'pack'
    __table_args__ = (
        CheckConstraint('total >= 0 AND total <= 5000', name='total_range_check'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(127), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    total: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    creator: Mapped[int] = mapped_column(SmallInteger, nullable=False)
