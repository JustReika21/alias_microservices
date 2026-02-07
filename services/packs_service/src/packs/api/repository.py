from packs.database.dependencies import get_session
from packs.database.models import Pack
from packs.exc.exceptions import PackCreationError
from packs.schemas.schemas import PackCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists, select


async def save_pack(
        pack: PackCreate,
        db: AsyncSession
) -> Pack:

    pack = Pack(name=pack.name, description=pack.description)

    try:
        db.add(pack)
        await db.commit()
        await db.refresh(pack)

        return pack
    except IntegrityError:
        await db.rollback()
        raise PackCreationError('Pack creation error')

async def is_pack_exist(
        pack_id: int,
        db: AsyncSession
) -> bool:
    stmt = select(exists().where(Pack.id == pack_id))
    pack_exists = await db.scalar(stmt)
    return pack_exists

async def get_total_cards_in_pack(
        pack_id: int,
        db: AsyncSession
) -> int:
    stmt = select(Pack.total).where(Pack.id == pack_id)
    total_cards = await db.scalar(stmt)
    return total_cards
