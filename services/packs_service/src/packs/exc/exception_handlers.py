from fastapi import Request, status
from fastapi.responses import JSONResponse

from packs.exc.exceptions import PackCreationError


async def handle_pack_creation_error(request: Request, exc: PackCreationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )

def register_pack_exception_handlers(app):
    app.add_exception_handler(PackCreationError, handle_pack_creation_error)
