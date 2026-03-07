import random
import string
from datetime import datetime
from typing import List

from game.database.db import Base
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

CHARS = string.ascii_letters + string.digits

def generate_id():
    return ''.join(random.choice(CHARS) for _ in range(6))
