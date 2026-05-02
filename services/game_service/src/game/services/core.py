from typing import List

from game.database.models import generate_id
from game.exc.exceptions import TeamNotFoundError
from game.repositories.repository import GameRepository
from game.schemas.schemas import GameCreate, Player, Game


class GameCoreService:
    def __init__(
            self,
            repo: GameRepository,
    ):
        self.repo = repo

    async def create_game(self, game_data: GameCreate, player: Player) -> None:
        game = Game(
            id=generate_id(),
            host=player.id,
            rounds=game_data.rounds,
            time=game_data.time,
            pack=game_data.pack,
            password=game_data.password or ''
        )

        await self.repo.create_game(game)
        await self.repo.create_team(game.id, 1)
        await self.repo.add_player(game.id, player)

    async def join_game(self, game_id: str, player: Player) -> None:
        await self.repo.add_player(game_id, player)

    async def switch_team(
            self,
            game_id: str,
            player_id: int,
            new_team_id: int,
    ):
        if new_team_id < 0 or new_team_id > 4:
            raise TeamNotFoundError('Invalid team id')

        await self.repo.switch_team(game_id, player_id, new_team_id)

        teams = await self.get_teams(game_id)
        return teams



    async def get_game_status(self, game_id: str) -> str:
        return await self.repo.get_game_status(game_id)

    async def get_players(self, game_id: str) -> List[dict]:
        return await self.repo.get_players(game_id)

    async def get_current_player(self, game_id: str) -> int:
        return await self.repo.get_current_player_id(game_id)

    async def get_current_team(self, game_id: str) -> int:
        return await self.repo.get_current_team_id(game_id)

    async def get_teams(self, game_id: str) -> List[dict]:
        return await self.repo.get_teams(game_id)

    async def get_host(self, game_id: str) -> int:
        return await self.repo.get_host(game_id)

    async def get_guessed_cards(self, game_id: str) -> set[int]:
        return await self.repo.get_guessed_cards(game_id)
