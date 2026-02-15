from packs.repository import save_pack
from packs.schemas.schemas import PackCreate, PackRead
from sqlalchemy.ext.asyncio import AsyncSession


async def create_pack(card: PackCreate, db: AsyncSession) -> PackRead:
    created_card = await save_pack(card, db)

    return PackRead.model_validate(created_card)