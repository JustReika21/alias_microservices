from sqlite3 import IntegrityError
from typing import Optional

from game.database.models import generate_id
from game.schemas.schemas import Game, Player
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository


class GameService:
    def __init__(self, game_repository: GameRepository, packs_client: PacksClient):
        self.game_repository = game_repository

        self.db = game_repository.db
        self.redis_client = game_repository.redis_client

        self.packs_client = packs_client

    async def create_game(self, game: Game) -> None:
        player = Player(id=1, name='PLACEHOLDER', score=0)
        game.host = player.id
        game.current_player = player.id
        game.id = generate_id()
        game.total_players = 1

        await self.game_repository.create(game)
        await self.game_repository.add_player(game.id, player)

    async def join_game(self, game_id: str, player: Player) -> None:
        await self.game_repository.add_player(game_id, player)
