import time
from typing import List

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameTeamRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db
        self.redis_client = redis_client

    async def create_team(self, game_id: str, team_id: int) -> None:
        async with self.redis_client.pipeline() as pipe:
            team_key = self._team_key(game_id, team_id)
            teams_key = self._teams_key(game_id)

            await pipe.hset(
                team_key,
                mapping={
                    'id': team_id,
                    'score': 0
                }
            )

            await pipe.zadd(teams_key, {str(team_id): team_id})

            await pipe.expire(teams_key, self.EXPIRE_TIME)
            await pipe.expire(team_key, self.EXPIRE_TIME)

            await pipe.execute()

    async def move_player(
            self,
            game_id: str,
            player_id: int,
            old_team_id: int,
            new_team_id: int,
    ) -> None:
        old_team_players = self._team_players_key(game_id, old_team_id)
        new_team_players = self._team_players_key(game_id, new_team_id)

        player_key = self._player_key(game_id, player_id)

        now = time.time()

        async with self.redis_client.pipeline() as pipe:
            await pipe.zrem(old_team_players, str(player_id))

            await pipe.zadd(
                new_team_players,
                {str(player_id): now}
            )

            await pipe.hset(player_key, "team_id", str(new_team_id))

            await pipe.execute()

        await self._update_team_metadata(game_id, old_team_id, new_team_id)

    async def _update_team_metadata(
            self,
            game_id: str,
            old_team_id: int,
            new_team_id: int,
    ) -> None:
        teams_key = self._teams_key(game_id)

        old_team_players = self._team_players_key(game_id, old_team_id)
        new_team_players = self._team_players_key(game_id, new_team_id)

        old_size = await self.redis_client.zcard(old_team_players)
        new_size = await self.redis_client.zcard(new_team_players)

        async with self.redis_client.pipeline() as pipe:

            if new_size == 1:
                await pipe.zadd(teams_key, {str(new_team_id): new_team_id})

            if old_size == 0:
                await pipe.delete(self._team_key(game_id, old_team_id))
                await pipe.zrem(teams_key, str(old_team_id))

            await pipe.execute()

    async def get_teams(self, game_id: str) -> List[dict]:
        teams_key = self._teams_key(game_id)
        team_ids = await self.redis_client.zrange(teams_key, 0, -1)

        async with self.redis_client.pipeline() as pipe:
            for team_id in team_ids:
                team_key = self._team_key(game_id, team_id)
                await pipe.hgetall(team_key)

            teams = await pipe.execute()

        return teams

    async def get_team_ids(self, game_id: str) -> List[str]:
        teams_key = self._teams_key(game_id)
        team_ids = await self.redis_client.zrange(teams_key, 0, -1)
        return team_ids

    async def get_current_team_id(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        async with self.redis_client.pipeline() as pipe:
            await pipe.zrange(teams_key, 0, -1)
            await pipe.hget(game_key, 'team_offset')

            team_ids, team_offset = await pipe.execute()

        total_teams = len(team_ids)
        idx = int(team_offset) % int(total_teams)

        current_team_id = team_ids[idx]
        return int(current_team_id)

    async def get_team_player_ids(self, game_id: str, team_id: str | int) -> List[str]:
        team_players_key = self._team_players_key(game_id, int(team_id))

        players = await self.redis_client.zrange(team_players_key, 0, -1)
        return players

    async def get_every_team_player_ids(
            self,
            game_id: str,
            team_ids: List[str]
    ) -> List[List[str]]:
        async with self.redis_client.pipeline() as pipe:
            for team_id in team_ids:
                team_players_key = self._team_players_key(game_id, int(team_id))
                await pipe.zrange(team_players_key, 0, -1)

            team_player_ids = await pipe.execute()

        return team_player_ids

    async def increment_team_offset(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        team_offset = await self.redis_client.hincrby(game_key, 'team_offset', 1)
        return team_offset

    async def is_team_exists(self, game_id: str, team_id: int) -> bool:
        team_key = self._team_key(game_id, team_id)
        team_exists = await self.redis_client.exists(team_key)
        return team_exists
