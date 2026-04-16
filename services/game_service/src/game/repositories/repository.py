from typing import List, Any

from redis.asyncio import Redis

from game.exc.exceptions import GameClosedError
from game.schemas.schemas import Game, Player, Team
from sqlalchemy.ext.asyncio import AsyncSession


EXPIRE_TIME = 7200


class GameRepository:
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def _game_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}'

    def _player_key(self, game_id: str, player_id: int) -> str:
        return f'alias:game:{game_id}:player:{player_id}'

    def _team_key(self, game_id: str, team_id: int) -> str:
        return f'alias:game:{game_id}:team:{team_id}'

    def _teams_key(self, game_id: str):
        return f'alias:game:{game_id}:teams'

    def _team_players_key(self, game_id: str, team_id: int) -> str:
        return f'alias:game:{game_id}:team:{team_id}:players'

    def _turn_offset_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:turn_offset'

    def _current_player_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:current_player'


    async def create_game(self, game: Game) -> None:
        await self.redis_client.hset(
            self._game_key(game.id),
            mapping=Game.model_dump(game)
        )
        await self.redis_client.expire(self._game_key(game.id), EXPIRE_TIME)

    async def create_team(self, game_id: str, team_id: int) -> None:
        async with self.redis_client.pipeline() as pipe:
            team_key = self._team_key(game_id, team_id)
            teams_key = self._teams_key(game_id)

            await pipe.hset(team_key, mapping={
                'id': team_id,
                'total_players': 0,
                'score': 0
            })

            await pipe.zadd(teams_key,{str(team_id): team_id})

            await pipe.expire(teams_key, EXPIRE_TIME)
            await pipe.expire(team_key, EXPIRE_TIME)

            await pipe.execute()

    async def add_player(self, game_id: str, player: Player) -> None:
        player_key = self._player_key(game_id, player.id)

        player_exists = await self.redis_client.exists(player_key)
        if player_exists:
            return

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

            await pipe.expire(player_in_team_key, EXPIRE_TIME)
            await pipe.expire(player_key, EXPIRE_TIME)

            await pipe.execute()

    async def switch_team(self, game_id: str, player_id: int, new_team_id: int):
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        player_key = self._player_key(game_id, player_id)
        old_team_id = await self.redis_client.hget(player_key, 'team_id')
        old_team_id = int(old_team_id)

        old_team_key = self._team_key(game_id, old_team_id)
        new_team_key = self._team_key(game_id, new_team_id)

        if new_team_id == old_team_id:
            return

        new_team_exists = await self.redis_client.exists(new_team_key)
        if not new_team_exists:
            await self.create_team(game_id, new_team_id)

        old_team_players = self._team_players_key(game_id, old_team_id)
        new_team_players = self._team_players_key(game_id, new_team_id)

        async with self.redis_client.pipeline() as pipe:
            await pipe.lrem(old_team_players, 0, str(player_id))
            await pipe.hincrby(old_team_key, "total_players", -1)

            await pipe.rpush(new_team_players, str(player_id))
            await pipe.hincrby(new_team_key, "total_players", 1)

            await pipe.hset(player_key, 'team_id', str(new_team_id))

            results = await pipe.execute()

        old_count = int(results[1])
        new_count = int(results[3])

        updates = 0

        async with self.redis_client.pipeline() as pipe:
            if new_count == 1:
                updates += 1
                await pipe.zadd(teams_key, {str(new_team_id): new_team_id})

            if old_count == 0:
                updates -= 1
                await pipe.delete(old_team_key)
                await pipe.zrem(teams_key, str(old_team_id))

            if updates != 0:
                await pipe.hincrby(game_key, 'total_teams', updates)

            await pipe.execute()

    async def next_turn(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        team_ids = await self.redis_client.zrange(teams_key, 0, -1)
        team_offset = await self.redis_client.hincrby(game_key, 'team_offset', 1)

        total_teams = len(team_ids)
        team_offset = int(team_offset) % int(total_teams)

        if team_offset == 0:
            turn_offset = await self.redis_client.hincrby(game_key, 'current_round', 1)
        else:
            turn_offset = await self.redis_client.hget(game_key, 'current_round')

        team_players_key = self._team_players_key(game_id, team_ids[team_offset])
        players = await self.redis_client.lrange(team_players_key, 0, -1)

        turn_offset = int(turn_offset) % len(players)

        next_player_id = players[turn_offset]

        return int(next_player_id)

    async def get_current_team_id(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        team_ids = await self.redis_client.zrange(teams_key, 0, -1)
        team_offset = await self.redis_client.hget(game_key, 'team_offset')

        total_teams = len(team_ids)

        current_team = int(team_offset) % int(total_teams) + 1

        return current_team

    async def get_current_player_id(self, game_id: str) -> int:
        game_key = self._game_key(game_id)
        teams_key = self._teams_key(game_id)

        team_ids = await self.redis_client.zrange(teams_key, 0, -1)
        turn_offset = await self.redis_client.hget(game_key, 'current_round')
        team_offset = await self.redis_client.hget(game_key, 'team_offset')

        total_teams = len(team_ids)
        team_offset = int(team_offset) % int(total_teams)

        team_players_key = self._team_players_key(game_id, team_ids[team_offset])
        players = await self.redis_client.lrange(team_players_key, 0, -1)

        turn_offset = int(turn_offset) % len(players)

        current_player_id = players[turn_offset]

        return int(current_player_id)

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

    async def get_players(self, game_id: str) -> List[dict[str: Any]]:
        players = []
        for i in range(1, 5):
            team_players_key = self._team_players_key(game_id, i)
            player_ids = await self.redis_client.lrange(team_players_key, 0, -1)

            for player_id in player_ids:
                player_key = self._player_key(game_id, player_id)
                player = await self.redis_client.hgetall(player_key)

                players.append(player)

        return players

    async def set_game_status(self, game_id: str, status: str) -> str:
        game_key = self._game_key(game_id)
        await self.redis_client.hset(game_key, 'status', status)
        return status

    async def update_player_score(self, game_id: str, player_id: int, points: int) -> int:
        player_key = self._player_key(game_id, player_id)
        return await self.redis_client.hincrby(player_key, 'score', points)

    async def update_team_score(self, game_id: str, team_id: int, points: int) -> int:
        team_key = self._team_key(game_id, team_id)
        return await self.redis_client.hincrby(team_key, 'score', points)
