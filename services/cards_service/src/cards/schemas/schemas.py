from typing import List

from cards.schemas.validators import WORD
from pydantic import BaseModel


class CardBase(BaseModel):
    pass


class CardCreate(CardBase):
    word: WORD
    pack_id: int


class CardsCreate(CardBase):
    words: List[WORD]
    pack_id: int


class CardRead(CardBase):
    id: int
    word: WORD
    pack_id: int

    class Config:
        from_attributes = True
