from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameRoundRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def cleanup_round(self, game_id: str) -> None:
        cards_key = self._cards_key(game_id)
        cursor_key = self._card_cursor_key(game_id)
        played_cards_key = self._played_cards_key(game_id)
        guessed_cards_key = self._guessed_cards_key(game_id)
        timer_key = self._timer_key(game_id)

        async with self.redis_client.pipeline() as pipe:
            pipe.delete(cards_key)
            pipe.delete(cursor_key)
            pipe.delete(played_cards_key)
            pipe.delete(guessed_cards_key)
            pipe.delete(timer_key)

            await pipe.execute()

    async def get_total_rounds(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        total_rounds = await self.redis_client.hget(game_key, 'rounds')
        return int(total_rounds)

    async def get_current_round(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        current_round = await self.redis_client.hget(game_key, 'current_round')
        return int(current_round)

    async def increment_current_round(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.hincrby(game_key, 'current_round', 1)
            pipe.expire(game_key, self.EXPIRE_TIME)
            result = await pipe.execute()
        return int(result[0])

    async def reset_rounds(self, game_id: str) -> None:
        game_key = self._game_key(game_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(game_key, 'current_round', '0')
            pipe.expire(game_key, self.EXPIRE_TIME)
            await pipe.execute()
