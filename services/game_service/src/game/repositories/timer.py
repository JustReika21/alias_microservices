from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameTimerRepository(RedisConfig):
    def __init__(
            self,
            redis_client: Redis
    ):
        self.redis_client = redis_client

    async def set_timer(self, game_id: str, end_time: int) -> None:
        timer_key = self._timer_key(game_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.set(timer_key, str(end_time))
            pipe.expire(timer_key, self.EXPIRE_TIME)
            await pipe.execute()

    async def get_timer(self, game_id: str) -> int:
        timer_key = self._timer_key(game_id)
        end_time = await self.redis_client.get(timer_key)
        return int(end_time)
