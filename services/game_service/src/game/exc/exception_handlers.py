from fastapi import Request, status
from fastapi.responses import JSONResponse
from game.exc.exceptions import (GameClosedError, GameCreationError,
                                 GameNotFoundError, TeamNotFoundError,
                                 GameAlreadyStartedError)


async def handle_game_creation_error(request: Request, exc: GameCreationError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_game_not_found_error(request: Request, exc: GameNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_game_closed_error(request: Request, exc: GameClosedError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_team_not_found_error(request: Request, exc: TeamNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_game_already_started_error(request: Request, exc: GameAlreadyStartedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={'detail': str(exc)},
    )


def register_game_exception_handlers(app):
    app.add_exception_handler(GameCreationError, handle_game_creation_error)
    app.add_exception_handler(GameNotFoundError, handle_game_not_found_error)
    app.add_exception_handler(TeamNotFoundError, handle_team_not_found_error)
    app.add_exception_handler(GameClosedError, handle_game_closed_error)
    app.add_exception_handler(GameAlreadyStartedError, handle_game_already_started_error)
