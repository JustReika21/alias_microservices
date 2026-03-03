from typing import Optional

from game.database.models import Game
from sqlalchemy.ext.asyncio import AsyncSession


class GameRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, password: Optional[str]) -> Game:
        game = Game(password=password)
        self.db.add(game)
        return game
