import json
from typing import List

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameCardRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def set_game_cards(self, game_id: str, cards: List[dict]) -> None:
        cards_key = self._cards_key(game_id)
        async with self.redis_client.pipeline() as pipe:
            for card in cards:
                await pipe.rpush(cards_key, json.dumps(card))

            await pipe.expire(cards_key, self.EXPIRE_TIME)
            await pipe.execute()

    async def get_players_cards(self, game_id: str, cursor: int) -> dict:
        cards_key = self._cards_key(game_id)

        prev_index = cursor - 1 if cursor > 0 else None

        async with self.redis_client.pipeline() as pipe:
            await pipe.lindex(cards_key, cursor)

            if prev_index is not None:
                await pipe.lindex(cards_key, prev_index)

            results = await pipe.execute()

        current = results[0]
        previous = results[1] if prev_index is not None else None

        cards = {
            'current': json.loads(current) if current else None,
            'previous': json.loads(previous) if previous else None
        }
        return cards

    async def commit_card(self, game_id: str, card: dict) -> None:
        async with self.redis_client.pipeline() as pipe:
            await pipe.rpush(self._played_cards_key(game_id), json.dumps(card))
            await pipe.hincrby(self._card_cursor_key(game_id), 'cursor', 1)
            await pipe.execute()

    async def get_played_cards(self, game_id: str) -> List[dict]:
        played_cards_key = self._played_cards_key(game_id)
        raw = await self.redis_client.lrange(played_cards_key, 0, -1)
        cards = [json.loads(card) for card in raw]
        return cards

    async def set_guessed_cards(self, game_id: str) -> None:
        guessed_cards_key = self._guessed_cards_key(game_id)
        cards = await self.get_played_cards(game_id)

        async with self.redis_client.pipeline() as pipe:
            for card in cards:
                await pipe.sadd(guessed_cards_key, card['id'])

            await pipe.expire(guessed_cards_key, self.EXPIRE_TIME)
            await pipe.execute()

    async def get_guessed_cards(self, game_id: str) -> set[str]:
        guessed_cards_key = self._guessed_cards_key(game_id)
        card_ids = await self.redis_client.smembers(guessed_cards_key)
        return card_ids

    async def guess_card(self, game_id: str, card_id: int, guessed: bool) -> None:
        guessed_cards_key = self._guessed_cards_key(game_id)

        if guessed:
            await self.redis_client.sadd(guessed_cards_key, card_id)
        else:
            await self.redis_client.srem(guessed_cards_key, card_id)

    async def set_card_cursor(self, game_id: str) -> None:
        cursor_key = self._card_cursor_key(game_id)
        await self.redis_client.hset(cursor_key, 'cursor', str(0))
        await self.redis_client.expire(cursor_key, self.EXPIRE_TIME)

    async def get_card_cursor(self, game_id: str) -> int:
        cursor_key = self._card_cursor_key(game_id)
        cursor = await self.redis_client.hget(cursor_key, 'cursor')
        return int(cursor)
