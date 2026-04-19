from typing import Optional

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
    description: Optional[str]
    creator: int

    model_config = ConfigDict(
        from_attributes=True
    )


class PackUpdate(PackBase):
    name: NAME
    description: Optional[DESCRIPTION] = None
