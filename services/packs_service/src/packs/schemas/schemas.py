from typing import Optional

from pydantic import BaseModel


class PackBase(BaseModel):
    pass


class PackCreate(PackBase):
    name: str
    description: Optional[str] = None


class PackRead(PackBase):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True
