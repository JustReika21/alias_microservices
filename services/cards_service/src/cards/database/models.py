from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column

from cards.database.db import Base


class Card(Base):
    __tablename__ = 'card'
    __table_args__ = (
        UniqueConstraint('word', 'pack_id', name='uix_word_collection'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(127), nullable=False)
    pack_id: Mapped[int] = mapped_column(nullable=False)
