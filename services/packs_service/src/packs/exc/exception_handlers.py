from fastapi import Request, status
from fastapi.responses import JSONResponse
from packs.exc.exceptions import PackCreationError, PackUpdateError, \
    PackDoesNotExist, PermissionDenied, PackDeletionError


async def handle_pack_creation_error(request: Request, exc: PackCreationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def handle_pack_update_error(request: Request, exc: PackUpdateError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def handle_pack_does_not_exist(request: Request, exc: PackDoesNotExist):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )

async def handle_permission_denied(request: Request, exc: PermissionDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={'detail': str(exc)},
    )

async def handle_pack_deletion_error(request: Request, exc: PackDeletionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


def register_pack_exception_handlers(app):
    app.add_exception_handler(PackCreationError, handle_pack_creation_error)
    app.add_exception_handler(PackUpdateError, handle_pack_update_error)
    app.add_exception_handler(PackDoesNotExist, handle_pack_does_not_exist)
    app.add_exception_handler(PermissionDenied, handle_permission_denied)
    app.add_exception_handler(PackDeletionError, handle_pack_deletion_error)
