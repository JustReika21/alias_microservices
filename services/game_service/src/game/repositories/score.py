from typing import List

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameScoreRepository(RedisConfig):
    def __init__(
            self,
            redis_client: Redis
    ):
        self.redis_client = redis_client

    async def update_player_score(self, game_id: str, player_id: int, points: int) -> int:
        player_key = self._player_key(game_id, player_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.hincrby(player_key, 'score', points)
            pipe.expire(player_key, self.EXPIRE_TIME)
            result = await pipe.execute()
        return int(result[0])

    async def update_team_score(self, game_id: str, team_id: int, points: int) -> int:
        team_key = self._team_key(game_id, team_id)
        async with self.redis_client.pipeline() as pipe:
            pipe.hincrby(team_key, 'score', points)
            pipe.expire(team_key, self.EXPIRE_TIME)
            result = await pipe.execute()
        return int(result[0])

    async def reset_scores(self, game_id: str, players: List[str], teams: List[str]):
        async with self.redis_client.pipeline() as pipe:
            for player in players:
                player_key = self._player_key(game_id, int(player))
                pipe.hset(player_key, 'score', '0')
                pipe.expire(player_key, self.EXPIRE_TIME)

            for team in teams:
                team_key = self._team_key(game_id, int(team))
                pipe.hset(team_key, 'score', '0')
                pipe.expire(team_key, self.EXPIRE_TIME)

            await pipe.execute()