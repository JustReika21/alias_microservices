from fastapi import APIRouter
from fastapi.params import Depends
from packs.services.service import PackService
from packs.dependencies import get_pack_service
from packs.schemas.schemas import PackCreate, PackRead

pack_router = APIRouter(tags=['Packs'])

@pack_router.post('/packs')
async def pack_create_api(
        pack: PackCreate,
        pack_service: PackService = Depends(get_pack_service)
) -> PackRead:
    return await pack_service.create_pack(pack)
