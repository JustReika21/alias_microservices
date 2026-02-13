from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from game.database.models import Game


async def create_game_in_db(password: Optional[str], db: AsyncSession):
    game = Game(password=password)
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game.id
