from pydantic import BaseModel

class CardBase(BaseModel):
    pass


class CardCreate(CardBase):
    word: str
    pack_id: int


class CardRead(CardBase):
    id: int
    word: str

    class Config:
        from_attributes = True
