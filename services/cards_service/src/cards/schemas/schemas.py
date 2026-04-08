from typing import List

from cards.schemas.validators import WORD, LIMIT
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
    position: int

    model_config = ConfigDict(
        from_attributes = True
    )


class RandomCardRead(CardBase):
    word: str

    model_config = ConfigDict(
        from_attributes=True
    )

class RandomCardsRequest(CardBase):
    pack_id: int
    limit: LIMIT


class CardDelete(CardBase):
    id: int


class CardsDelete(CardBase):
    ids: List[int]
