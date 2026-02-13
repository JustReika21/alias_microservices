from fastapi import APIRouter
from fastapi.params import Depends
from packs.api.service import create_pack
from packs.dependencies import get_session
from packs.schemas.schemas import PackCreate, PackRead
from sqlalchemy.ext.asyncio import AsyncSession

pack_router = APIRouter(tags=['Packs'])

@pack_router.post('/pack')
async def pack_create_api(
        pack: PackCreate,
        db: AsyncSession = Depends(get_session)
) -> PackRead:
    return await create_pack(pack, db)
