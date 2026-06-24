from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig
from game.schemas.schemas import Game


class GameCoreRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def create_game(self, game: Game) -> None:
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(
                self._game_key(game.id),
                mapping=Game.model_dump(game)
            )
            pipe.expire(self._game_key(game.id), self.EXPIRE_TIME)
            await pipe.execute()

    async def is_game_exist(self, game_id: str) -> bool:
        game_key = self._game_key(game_id)
        return await self.redis_client.exists(game_key)

    async def get_round_time(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        round_time = await self.redis_client.hget(game_key, 'time')
        return int(round_time)

    async def get_game_status(self, game_id: str) -> str:
        game_key = self._game_key(game_id)
        status = await self.redis_client.hget(game_key, 'status')
        return status

    async def set_game_status(self, game_id: str, status: str) -> None:
        game_key = self._game_key(game_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(game_key, 'status', status)
            pipe.expire(game_key, self.EXPIRE_TIME)
            await pipe.execute()

    async def get_pack_id(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        pack_id = await self.redis_client.hget(game_key, 'pack')
        return int(pack_id)

    async def get_host_id(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        host = await self.redis_client.hget(game_key, 'host')
        return int(host)
