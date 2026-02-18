import random
import string
from datetime import datetime

from game.database.db import Base
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

CHARS = string.ascii_letters + string.digits

def generate_id():
    return ''.join(random.choice(CHARS) for _ in range(6))



class Game(Base):
    __tablename__ = 'game'

    id: Mapped[str] = mapped_column(String(6), primary_key=True, default=generate_id)
    password: Mapped[str] = mapped_column(String(12), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
