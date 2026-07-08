from typing import List

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from packs.dependencies import get_pack_service
from packs.schemas.schemas import PackCreate, PackRead, PackUpdate, \
    PackPreview, PaginatedPacksPreview, PaginatedInfiniteScroll
from packs.services.service import PackService

pack_router = APIRouter(tags=['Packs'], prefix='/packs')


@pack_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=PackRead,
)
async def pack_create_api(
        pack: PackCreate,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
):
    access_token = credentials.credentials
    user = await pack_service.auth_client.get_user(access_token)
    return await pack_service.create_pack(pack, user.user_id)


@pack_router.get(
    '/my',
    status_code=status.HTTP_200_OK,
    response_model=PaginatedPacksPreview,
)
async def get_my_packs_api(
        page: int = Query(1, ge=1),
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
):
    access_token = credentials.credentials
    return await pack_service.get_my_packs(access_token, page)


@pack_router.get(
    '/edit/{pack_id}',
    status_code=status.HTTP_200_OK,
    response_model=PackRead,
)
async def get_pack_for_update(
        pack_id: int,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
):
    access_token = credentials.credentials
    await pack_service.is_creator(pack_id, access_token)
    return await pack_service.get_pack(pack_id)

@pack_router.get(
    '/{pack_id}',
    status_code=status.HTTP_200_OK,
    response_model=PackRead,
)
async def get_pack_api(
        pack_id: int,
        pack_service: PackService = Depends(get_pack_service)
):
    return await pack_service.get_pack(pack_id)


@pack_router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=PaginatedInfiniteScroll,
)
async def get_packs_by_name(
        pack_name: str = Query(default=None, max_length=127),
        page: int = Query(1, ge=1),
        pack_service: PackService = Depends(get_pack_service)
):
    return await pack_service.get_packs_by_name(pack_name, page)


@pack_router.delete('/{pack_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_pack_api(
        pack_id: int,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
) -> None:
    access_token = credentials.credentials
    await pack_service.is_creator(pack_id, access_token)

    deleted = await pack_service.cards_client.delete_all_cards_in_pack(pack_id)
    if deleted:
        await pack_service.delete_pack(pack_id)


@pack_router.put(
    '/{pack_id}',
    status_code=status.HTTP_200_OK,
    response_model=PackRead,
)
async def update_pack_api(
        pack_id: int,
        payload: PackUpdate,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
):
    access_token = credentials.credentials
    await pack_service.is_creator(pack_id, access_token)
    return await pack_service.update_pack(pack_id, payload)
