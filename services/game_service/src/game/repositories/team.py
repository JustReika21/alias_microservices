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
                    'total_players': 0,
                    'score': 0
                }
            )

            await pipe.zadd(teams_key,{str(team_id): team_id})

            await pipe.expire(teams_key, self.EXPIRE_TIME)
            await pipe.expire(team_key, self.EXPIRE_TIME)

            await pipe.execute()

    async def move_player(
            self,
            game_id: str,
            player_id: int,
            old_team_id: int,
            new_team_id: int,
    ) -> dict:
        old_team_key = self._team_key(game_id, old_team_id)
        new_team_key = self._team_key(game_id, new_team_id)

        old_team_players = self._team_players_key(game_id, old_team_id)
        new_team_players = self._team_players_key(game_id, new_team_id)

        player_key = self._player_key(game_id, player_id)

        async with self.redis_client.pipeline() as pipe:
            await pipe.lrem(old_team_players, 0, str(player_id))
            await pipe.hincrby(old_team_key, "total_players", -1)

            await pipe.rpush(new_team_players, str(player_id))
            await pipe.hincrby(new_team_key, "total_players", 1)

            await pipe.hset(player_key, 'team_id', str(new_team_id))

            _, old_count, _, new_count, _ = await pipe.execute()

        old_team_players_count = int(old_count)
        new_team_players_count = int(new_count)

        return {
            'old_team_players_count': old_team_players_count,
            'new_team_players_count': new_team_players_count
        }

    async def update_team_metadata(
            self,
            game_id: str,
            old_team_id: int,
            new_team_id: int,
            old_team_players_count,
            new_team_players_count
    ) -> None:
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        old_team_key = self._team_key(game_id, old_team_id)

        updates = 0

        async with self.redis_client.pipeline() as pipe:
            if new_team_players_count == 1:
                updates += 1
                await pipe.zadd(teams_key, {str(new_team_id): new_team_id})

            if old_team_players_count == 0:
                updates -= 1
                await pipe.delete(old_team_key)
                await pipe.zrem(teams_key, str(old_team_id))

            if updates != 0:
                await pipe.hincrby(game_key, 'total_teams', updates)

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
        players = await self.redis_client.lrange(team_players_key, 0, -1)
        return players

    async def get_every_team_player_ids(
            self,
            game_id: str,
            team_ids: List[str]
    ) ->List[List[str]]:
        async with self.redis_client.pipeline() as pipe:
            for team_id in team_ids:
                team_players_key = self._team_players_key(game_id, int(team_id))
                await pipe.lrange(team_players_key, 0, -1)

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
