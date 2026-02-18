from typing import Optional

from game.api.repository import create_game_in_db
from sqlalchemy.ext.asyncio import AsyncSession


async def create_game(password: Optional[str], db: AsyncSession):
    return await create_game_in_db(password, db)
