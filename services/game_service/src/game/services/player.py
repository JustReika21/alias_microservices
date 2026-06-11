from typing import List

from game.repositories.player import GamePlayerRepository
from game.schemas.schemas import Player


class GamePlayerService:
    def __init__(
            self,
            player_repo: GamePlayerRepository,
    ):
        self.player_repo = player_repo

    async def join_game(self, game_id: str, player: Player) -> None:
        player_exists = await self.player_repo.is_player_exists(game_id, player.id)

        if player_exists:
            return

        await self.player_repo.add_player(game_id, player)

    async def get_player_team_id(self, game_id: str, player_id: int) -> int:
        player_team = await self.player_repo.get_player_team_id(game_id, player_id)
        return player_team

    async def _get_players(
            self,
            game_id: str,
            team_player_ids: List[List[str]]
    ) -> List[dict]:
        player_ids = []
        for team in team_player_ids:
            player_ids.extend(pid for pid in team)

        if not player_ids:
            return []

        players = await self.player_repo.get_players(game_id, player_ids)
        return players

    async def get_player(self, game_id: str, player_id: str) -> dict:
        player = await self.player_repo.get_player(game_id, player_id)
        return player

    async def is_player_exist(self, game_id: str, player_id: int) -> bool:
        player_exists = await self.player_repo.is_player_exists(game_id, player_id)
        return player_exists

    async def remove_player(self, game_id: str, player_id: str) -> None:
        await self.player_repo.remove_player(game_id, player_id)

    async def disconnect_player(self, game_id: str, player_id: str) -> None:
        await self.player_repo.disconnect_player(game_id, player_id)

    async def connect_player(self, game_id: str, player_id: str) -> None:
        await self.player_repo.connect_player(game_id, player_id)
