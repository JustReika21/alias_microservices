from typing import Optional, List

from packs.schemas.validators import DESCRIPTION, NAME
from pydantic import BaseModel, ConfigDict


class PackBase(BaseModel):
    pass


class PackCreate(PackBase):
    name: NAME
    description: Optional[DESCRIPTION] = None


class PackRead(PackBase):
    id: int
    name: str
    total: int
    description: Optional[str]
    creator: int

    model_config = ConfigDict(
        from_attributes=True
    )


class PackPreview(PackBase):
    id: int
    name: str
    total: int

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedPacksPreview(PackBase):
    items: List[PackPreview]
    total: int
    page: int
    limit: int
    pages: int


class PaginatedInfiniteScroll(PackBase):
    items: List[PackPreview]
    page: int

class PackUpdate(PackBase):
    name: NAME
    description: Optional[DESCRIPTION] = None
