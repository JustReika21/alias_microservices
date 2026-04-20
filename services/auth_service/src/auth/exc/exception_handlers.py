from auth.exc.exceptions import (InvalidToken, TokenExpired, TokenNotFound,
                                 UserCreationError, UserLoginError,
                                 UserNotFound)
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def handle_user_creation_error(request: Request, exc: UserCreationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def handle_user_login_error(request: Request, exc: UserLoginError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def handle_user_does_not_found(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_invalid_token(request: Request, exc: InvalidToken):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': str(exc)},
    )


async def handle_token_not_found(request: Request, exc: TokenNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def hande_token_expired(request: Request, exc: TokenExpired):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': str(exc)},
    )


def register_auth_exception_handlers(app):
    app.add_exception_handler(UserLoginError, handle_user_login_error)
    app.add_exception_handler(UserCreationError, handle_user_creation_error)
    app.add_exception_handler(UserNotFound, handle_user_does_not_found)
    app.add_exception_handler(InvalidToken, handle_user_does_not_found)
    app.add_exception_handler(TokenNotFound, handle_token_not_found)
    app.add_exception_handler(TokenExpired, hande_token_expired)
