from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from game.api.repository import create_game_in_db


async def create_game(password: Optional[str], db: AsyncSession):
    return await create_game_in_db(password, db)
