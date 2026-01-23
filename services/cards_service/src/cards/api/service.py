from sqlalchemy.ext.asyncio import AsyncSession

from cards.api.repository import save_card
from cards.schemas.schemas import CardCreate, CardRead


async def create_card(card: CardCreate, db: AsyncSession) -> CardRead:
    created_card = await save_card(card, db)

    return CardRead.model_validate(created_card)

#
# async def get_random_cards(
#         collection_id: int,
#         limit: int,
#         db: AsyncSession
# ) -> List[CardRead]:
#     cards = await get_random_cards_from_db(collection_id, limit, db)
#     validated_cards = [CardRead.model_validate(card) for card in cards]
#     shuffle(validated_cards)
#     return validated_cards
