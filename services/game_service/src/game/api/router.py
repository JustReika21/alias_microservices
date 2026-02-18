from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from game.api.service import create_game
from game.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession

game_router = APIRouter(tags=['Games'])


@game_router.post('/game')
async def game_create_api(
        password: Optional[str] = None,
        db: AsyncSession = Depends(get_session),
):
    return await create_game(password, db)
