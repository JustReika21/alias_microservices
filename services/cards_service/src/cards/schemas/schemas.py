from typing import List

from cards.schemas.validators import WORD
from pydantic import BaseModel, ConfigDict


class CardBase(BaseModel):
    pass


class CardsCreate(CardBase):
    words: List[WORD]
    pack_id: int


class CardRead(CardBase):
    id: int
    word: str
    pack_id: int

    model_config = ConfigDict(
        from_attributes = True
    )


class RandomCardsRequest(CardBase):
    pack_id: int
    limit: int


class CardDelete(CardBase):
    id: int


class CardsDelete(CardBase):
    ids: List[int]
