from typing import List

from game.exc.exceptions import TeamNotFoundError
from game.repositories.team import GameTeamRepository


class GameTeamService:
    def __init__(
            self,
            team_repo: GameTeamRepository,
    ):
        self.team_repo = team_repo

    async def switch_team(
            self,
            game_id: str,
            player_id: int,
            new_team_id: int,
            old_team_id: int,
    ) -> None:
        if new_team_id <= 0 or new_team_id >= 5:
            raise TeamNotFoundError('Team ID is out of range')

        if old_team_id == new_team_id:
            return

        new_team_exists = await self.team_repo.is_team_exists(game_id, new_team_id)
        if not new_team_exists:
            await self.team_repo.create_team(game_id, new_team_id)

        await self.team_repo.move_player(
            game_id, player_id, old_team_id, new_team_id
        )


    async def create_team(self, game_id: str, team_id: int) -> None:
        await self.team_repo.create_team(game_id, team_id)

    async def get_current_team_id(self, game_id: str) -> int:
        team_id = await self.team_repo.get_current_team_id(game_id)
        return team_id

    async def get_teams(self, game_id: str) -> List[dict]:
        teams = await self.team_repo.get_teams(game_id)
        return teams

    async def get_team_ids(self, game_id: str) -> List[str]:
        team_ids = await self.team_repo.get_team_ids(game_id)
        return team_ids

    async def get_every_team_player_ids(self, game_id: str, team_ids: List[str]) -> List[List[str]]:
        team_ids = await self.team_repo.get_every_team_player_ids(game_id, team_ids)
        return team_ids

    async def get_team_player_ids(self, game_id: str, team_id: str | int) -> List[str]:
        team_players = await self.team_repo.get_team_player_ids(game_id, team_id)
        return team_players

    async def increment_team_offset(self, game_id: str) -> int:
        team_offset = await self.team_repo.increment_team_offset(game_id)
        return team_offset
