from typing import List

from fastapi import APIRouter, status, Query, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packs.dependencies import get_pack_service
from packs.schemas.schemas import PackCreate, PackRead, PackUpdate
from packs.services.service import PackService

pack_router = APIRouter(tags=['Packs'])


@pack_router.post(
    '/packs',
    status_code=status.HTTP_201_CREATED,
    response_model=PackRead,
)
async def pack_create_api(
        pack: PackCreate,
        pack_service: PackService = Depends(get_pack_service)
):
    return await pack_service.create_pack(pack)


@pack_router.get(
    '/packs/my',
    status_code=status.HTTP_200_OK,
    response_model=List[PackRead],
)
async def get_my_packs_api(
        offset: int = Query(0, ge=0),
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        pack_service: PackService = Depends(get_pack_service)
):
    access_token = credentials.credentials
    return await pack_service.get_my_packs(access_token, offset)


@pack_router.get(
    '/packs',
    status_code=status.HTTP_200_OK,
    response_model=List[PackRead],
)
async def get_packs_api(
        offset: int = Query(0, ge=0),
        pack_service: PackService = Depends(get_pack_service)
):
    return await pack_service.get_packs(offset)


@pack_router.get(
    '/packs/{pack_id}',
    status_code=status.HTTP_200_OK,
    response_model=PackRead,
)
async def get_pack_api(
        pack_id: int,
        pack_service: PackService = Depends(get_pack_service)
):
    return await pack_service.get_pack(pack_id)


@pack_router.delete('/packs/{pack_id}', status_code=status.HTTP_204_NO_CONTENT)
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
    '/packs/{pack_id}',
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
