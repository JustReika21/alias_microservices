from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameTimerRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def set_timer(self, game_id: str, end_time: int) -> None:
        timer_key = self._timer_key(game_id)
        await self.redis_client.set(timer_key, str(end_time))

    async def get_timer(self, game_id: str) -> int:
        timer_key = self._timer_key(game_id)
        end_time = await self.redis_client.get(timer_key)
        return int(end_time)
