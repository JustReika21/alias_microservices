from cards.exc.exceptions import (CardCreationError, CardDeletionError,
                                  CardDoesNotExistError, CardError)
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def handle_card_creation_error(request: Request, exc: CardCreationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )

async def handle_card_error(request: Request, exc: CardError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def handle_card_does_not_exist(request: Request, exc: CardDoesNotExistError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


async def handle_card_deletion_error(request: Request, exc: CardDeletionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


def register_card_exception_handlers(app):
    app.add_exception_handler(CardCreationError, handle_card_creation_error)
    app.add_exception_handler(CardError, handle_card_error)
    app.add_exception_handler(CardDoesNotExistError, handle_card_does_not_exist)
    app.add_exception_handler(CardDeletionError, handle_card_deletion_error)
