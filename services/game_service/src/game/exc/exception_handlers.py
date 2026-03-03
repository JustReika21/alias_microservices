from fastapi import Request, status
from fastapi.responses import JSONResponse

from game.exc.exceptions import GameCreationError


async def handle_game_creation_error(request: Request, exc: GameCreationError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


def register_game_exception_handlers(app):
    app.add_exception_handler(GameCreationError, handle_game_creation_error)
