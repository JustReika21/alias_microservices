from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packs.database.models import Pack
from packs.exc.exceptions import PackCreationError
from packs.schemas.schemas import PackCreate


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