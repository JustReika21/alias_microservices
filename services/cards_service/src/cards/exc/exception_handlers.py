from fastapi import Request, status
from fastapi.responses import JSONResponse

from cards.exc.exceptions import CardCreationError


async def handle_card_creation_error(request: Request, exc: CardCreationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )

def register_card_exception_handlers(app):
    app.add_exception_handler(CardCreationError, handle_card_creation_error)
