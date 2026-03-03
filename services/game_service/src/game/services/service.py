from sqlite3 import IntegrityError
from typing import Optional

from game.database.models import Game
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository


class GameService:
    def __init__(self, game_repository: GameRepository, packs_client: PacksClient):
        self.game_repository = game_repository
        self.db = game_repository.db
        self.packs_client = packs_client

    async def create_game(self, password: Optional[str]) -> Game:
        try:
            game = await self.game_repository.create(password)

            await self.db.commit()
            await self.db.refresh(game)

            return game
        except IntegrityError:
            await self.db.rollback()
