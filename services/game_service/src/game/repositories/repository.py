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

    def _turn_offset_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:turn_offset'

    def _current_player_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:current_player'


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

    async def next_turn(self, game_id: str) -> str:
        players_key = self._players_key(game_id)
        game_key = self._game_key(game_id)
        players = await self.redis_client.zrange(players_key, 0, -1)
        offset = await self.redis_client.hincrby(game_key, 'turn_offset', 1)

        current = offset % len(players)
        current_player_id = players[current]

        async with self.redis_client.pipeline() as pipe:
            await pipe.hset(game_key, 'turn_offset', str(offset))
            await pipe.hset(game_key, 'current_player', current_player_id)

            await pipe.execute()

        return current_player_id