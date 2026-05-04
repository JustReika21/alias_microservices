from game.repositories.core import GameCoreRepository
from game.schemas.schemas import Game

DEFAULT_TEAM_ID = 1


class GameCoreService:
    def __init__(
            self,
            core_repo: GameCoreRepository,
    ):
        self.core_repo = core_repo

    async def create_game(self, game: Game) -> None:
        await self.core_repo.create_game(game)

    async def set_game_status(self, game_id: str, status: str) -> None:
        await self.core_repo.set_game_status(game_id, status)

    async def get_round_time(self, game_id: str) -> int:
        return await self.core_repo.get_round_time(game_id)

    async def get_pack_id(self, game_id: str) -> int:
        return await self.core_repo.get_pack_id(game_id)

    async def is_game_exist(self, game_id: str) -> bool:
        return await self.core_repo.is_game_exist(game_id)

    async def get_game_status(self, game_id: str) -> str:
        return await self.core_repo.get_game_status(game_id)

    async def get_host_id(self, game_id: str) -> int:
        return await self.core_repo.get_host_id(game_id)
