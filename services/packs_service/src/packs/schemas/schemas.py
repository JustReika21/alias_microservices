from typing import Optional

from pydantic import BaseModel

from packs.schemas.validators import NAME, DESCRIPTION


class PackBase(BaseModel):
    pass


class PackCreate(PackBase):
    name: NAME
    description: Optional[DESCRIPTION] = None


class PackRead(PackBase):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True
