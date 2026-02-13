import string
from datetime import datetime
import random

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped

from game.database.db import Base

CHARS = string.ascii_letters + string.digits

def generate_id():
    return ''.join(random.choice(CHARS) for _ in range(6))



class Game(Base):
    __tablename__ = 'game'

    id: Mapped[str] = mapped_column(String(6), primary_key=True, default=generate_id)
    password: Mapped[str] = mapped_column(String(12), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
