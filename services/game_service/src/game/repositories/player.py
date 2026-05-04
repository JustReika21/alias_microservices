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

        team_key = self._team_key(game_id, player.team_id)
        player_in_team_key = self._team_players_key(game_id, player.team_id)
        teams_key = self._teams_key(game_id)

        async with self.redis_client.pipeline() as pipe:
            await pipe.hset(
                player_key,
                mapping=Player.model_dump(player)
            )

            await pipe.rpush(player_in_team_key, player.id)

            await pipe.hincrby(team_key, 'total_players', 1)

            await pipe.zadd(teams_key, {str(player.team_id): player.team_id})

            await pipe.expire(player_in_team_key, self.EXPIRE_TIME)
            await pipe.expire(player_key, self.EXPIRE_TIME)

            await pipe.execute()

    async def get_players(self, game_id: str, player_ids: List[str]) -> List[dict]:
        async with self.redis_client.pipeline() as pipe:
            for pid in player_ids:
                await pipe.hgetall(self._player_key(game_id, int(pid)))

            players = await pipe.execute()

        return players

    async def get_player_team_id(self, game_id: str, player_id: int) -> int:
        player_key = self._player_key(game_id, player_id)
        team_id = await self.redis_client.hget(player_key, 'team_id')
        return int(team_id)

    async def is_player_exists(self, game_id: str, player_id: int) -> bool:
        player_key = self._player_key(game_id, player_id)
        player_exists = await self.redis_client.exists(player_key)
        return player_exists

