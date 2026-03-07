from typing import Optional

from redis.asyncio import Redis

from game.schemas.schemas import Game, Player
from sqlalchemy.ext.asyncio import AsyncSession


class GameRepository:
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def _game_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}'

    def _players_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:players'

    def _player_key(self, game_id: str, player_id: int) -> str:
        return f'alias:game:{game_id}:player:{player_id}'

    async def create(self, game: Game) -> None:
        await self.redis_client.hset(
            self._game_key(game.id),
            mapping=Game.model_dump(game)
        )
        await self.redis_client.expire(self._game_key(game.id), 7200)

    async def add_player(self, game_id: str, player: Player) -> None:
        players_key = self._players_key(game_id)
        player_key = self._player_key(game_id, player.id)
        order = await self.redis_client.zcard(players_key)

        async with self.redis_client.pipeline() as pipe:
            await pipe.hset(
                player_key,
                mapping=Player.model_dump(player)
            )

            await pipe.zadd(players_key, mapping={str(player.id): order})

            await pipe.expire(players_key, 7200)
            await pipe.expire(player_key, 7200)

            await pipe.execute()

        await self.redis_client.expire(players_key, 7200)
