from typing import Optional

from game.database.models import Game
from sqlalchemy.ext.asyncio import AsyncSession


async def create_game_in_db(password: Optional[str], db: AsyncSession):
    game = Game(password=password)
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game.id
