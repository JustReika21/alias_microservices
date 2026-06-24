import time
from typing import List

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig
from game.schemas.schemas import Player


class GamePlayerRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def add_player(self, game_id: str, player: Player) -> None:
        player_key = self._player_key(game_id, player.id)

        player_in_team_key = self._team_players_key(game_id, player.team_id)
        teams_key = self._teams_key(game_id)

        now = time.time()

        async with self.redis_client.pipeline() as pipe:
            pipe.hset(
                player_key,
                mapping=Player.model_dump(player)
            )

            pipe.zadd(
                player_in_team_key,
                {str(player.id): now}
            )

            pipe.zadd(
                teams_key,
                {str(player.team_id): player.team_id}
            )

            pipe.expire(player_in_team_key, self.EXPIRE_TIME)
            pipe.expire(player_key, self.EXPIRE_TIME)
            pipe.expire(teams_key, self.EXPIRE_TIME)

            await pipe.execute()

    async def get_players(self, game_id: str, player_ids: List[str]) -> List[dict]:
        if not player_ids:
            return []

        async with self.redis_client.pipeline() as pipe:
            for pid in player_ids:
                pipe.hgetall(self._player_key(game_id, int(pid)))

            players = await pipe.execute()

        return players

    async def get_player(self, game_id: str, player_id: str) -> dict:
        player_key = self._player_key(game_id, int(player_id))
        player = await self.redis_client.hgetall(player_key)
        return player

    async def get_player_team_id(self, game_id: str, player_id: int) -> int:
        player_key = self._player_key(game_id, player_id)
        team_id = await self.redis_client.hget(player_key, 'team_id')
        return int(team_id)

    async def is_player_exists(self, game_id: str, player_id: int) -> bool:
        player_key = self._player_key(game_id, player_id)
        player_exists = await self.redis_client.exists(player_key)
        return player_exists

    async def remove_player(self, game_id: str, player_id: str) -> None:
        player_key = self._player_key(game_id, int(player_id))
        await self.redis_client.delete(player_key)

    async def disconnect_player(self, game_id: str, player_id: str) -> None:
        player_key = self._player_key(game_id, int(player_id))
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(player_key, 'connected', '0')
            pipe.expire(player_key, self.EXPIRE_TIME)
            await pipe.execute()

    async def connect_player(self, game_id: str, player_id: str) -> None:
        player_key = self._player_key(game_id, int(player_id))
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(player_key, 'connected', '1')
            pipe.expire(player_key, self.EXPIRE_TIME)
            await pipe.execute()
