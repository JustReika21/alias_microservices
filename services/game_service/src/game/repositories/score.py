from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.redis_keys import RedisConfig


class GameScoreRepository(RedisConfig):
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis
    ):
        self.db = db

        self.redis_client = redis_client

    async def update_player_score(self, game_id: str, player_id: int, points: int) -> int:
        player_key = self._player_key(game_id, player_id)
        return await self.redis_client.hincrby(player_key, 'score', points)

    async def update_team_score(self, game_id: str, team_id: int, points: int) -> int:
        team_key = self._team_key(game_id, team_id)
        return await self.redis_client.hincrby(team_key, 'score', points)
