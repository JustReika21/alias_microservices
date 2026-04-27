import asyncio
from typing import Any, List

from fastapi import WebSocket
from game.database.models import generate_id
from game.exc.exceptions import TeamNotFoundError
from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository
from game.schemas.schemas import Game, GameCreate, Player


class GameService:
    def __init__(
            self, game_repository: GameRepository, packs_client: PacksClient,
            cards_client: CardsClient, auth_client: AuthClient
    ):
        self.game_repository = game_repository

        self.db = game_repository.db
        self.redis_client = game_repository.redis_client

        self.packs_client = packs_client
        self.cards_client = cards_client
        self.auth_client = auth_client


    async def create_game(self, game_data: GameCreate, player: Player) -> None:
        game = Game(
            id=generate_id(),
            host=player.id,
            rounds=game_data.rounds,
            time=game_data.time,
            pack=game_data.pack,
            password=game_data.password or ''
        )

        await self.game_repository.create_game(game)
        await self.game_repository.create_team(game.id, 1)
        await self.game_repository.add_player(game.id, player)


    async def join_game(self, game_id: str, player: Player) -> None:
        await self.game_repository.add_player(game_id, player)

    async def load_snapshot(
            self,
            game_id: str,
            user_id: int,
            game_status: str,
            websocket: WebSocket
    ):
        current_player_id = await self.get_current_player(game_id)
        is_current = user_id == current_player_id

        snapshot = {
            'type': 'snapshot',
            'current_player': {
                'player_id': current_player_id,
                'is_current': is_current
            },
            'status': game_status,
            'cards': None
        }

        if game_status == 'started':
            cards = await self.game_repository.get_played_cards(game_id)
            snapshot['cards'] = cards if is_current else cards[:-1]

        elif game_status == 'calculating':
            cards = await self.game_repository.get_played_cards(game_id)
            snapshot['cards'] = cards

        await websocket.send_json(snapshot)


    async def start_game(
            self,
            game_id: str,
            con: dict[int, WebSocket]
    ):
        asyncio.create_task(self.run_round(game_id, con))

    async def run_round(
            self,
            game_id: str,
            con: dict[int, WebSocket]
    ):
        round_time = await self.game_repository.get_round_time(game_id)
        pack_id = await self.game_repository.get_pack_id(game_id)
        cards = await self.cards_client.get_random_cards(pack_id, 100)

        await self.game_repository.set_game_status(game_id, 'started')

        await self.game_repository.set_game_cards(game_id, cards)
        await self.game_repository.set_card_cursor(game_id)

        for ws in con.values():
            await ws.send_json({'type': 'timer', 'time': round_time})
            await ws.send_json({'type': 'status', 'value': 'started'})

        await self.send_card(game_id, con)

        await asyncio.sleep(round_time)

        await self.game_repository.set_game_status(game_id, 'calculating')

        await self.send_final_card(game_id, con)

    async def send_card(
            self,
            game_id: str,
            con: dict[int, WebSocket]
    ):
        cards = await self.game_repository.get_player_cards(game_id)
        current_player_id = await self.get_current_player(game_id)

        current_card = cards['current']
        if current_card is None:
            await self.game_repository.set_game_status(game_id, 'calculating')
            return

        previous_card = cards['previous']

        await self.game_repository.push_played_card(game_id, current_card)
        await self.game_repository.increment_cursor(game_id)

        for user_id, ws in con.items():
            await ws.send_json({
                'type': 'card',
                'card': current_card if user_id == current_player_id else previous_card,
                'guessed': True
            })

    async def send_final_card(self, game_id: str, con: dict[int, WebSocket]):
        current_player_id = await self.game_repository.get_current_player_id(game_id)

        cards = await self.game_repository.get_player_cards(game_id)
        card = cards['previous']

        for user_id, ws in con.items():
            if current_player_id != user_id:
                await ws.send_json({'type': 'card', 'card': card, 'guessed': True})
            await ws.send_json({'type': 'status', 'value': 'calculating'})

        await self.game_repository.set_guessed_cards(game_id)

    async def card_guessed(self, game_id, card_id: int, guessed: bool, con: dict[int, WebSocket]):
        played_cards = await self.game_repository.get_played_cards(game_id)
        played_card_ids = set(card['id'] for card in played_cards)
        if card_id not in played_card_ids:
            return

        await self.game_repository.guess_card(game_id, card_id, guessed)

        for ws in con.values():
            await ws.send_json({'type': 'guess', 'card': card_id, 'guessed': guessed})

    async def set_scores(self, game_id: str, con: dict[int, WebSocket]):
        await self.game_repository.set_game_status(game_id, 'waiting')
        current_player_id = await self.game_repository.get_current_player_id(game_id)
        current_team_id = await self.game_repository.get_current_team_id(game_id)
        guessed_card_ids = await self.game_repository.get_guessed_cards(game_id)

        points = len(guessed_card_ids)

        await self.game_repository.cleanup_round(game_id)

        player_score = await self.game_repository.update_player_score(game_id, current_player_id, points)
        team_score = await self.game_repository.update_team_score(game_id, current_team_id, points)

        next_player_id = await self.game_repository.next_turn(game_id)
        for user_id, ws in con.items():
            await ws.send_json({
                'type': 'current_player',
                'player_id': next_player_id,
                'is_current': user_id == next_player_id
            })

            await ws.send_json({
                'type': 'player_score_update',
                'id': current_player_id,
                'score': player_score
            })

            await ws.send_json({
                'type': 'team_score_update',
                'id': current_team_id,
                'score': team_score
            })

            await ws.send_json({'type': 'status', 'value': 'waiting'})


    async def switch_team(self, game_id: str, player_id: int, new_team_id: int):
        if new_team_id < 0 or new_team_id > 4:
            raise TeamNotFoundError('Invalid team id')

        await self.game_repository.switch_team(game_id, player_id, new_team_id)

    async def get_current_player(self, game_id: str) -> int:
        return await self.game_repository.get_current_player_id(game_id)

    async def get_game_status(self, game_id: str) -> str:
        return await self.game_repository.get_game_status(game_id)

    async def get_players(self, game_id: str) -> List[dict[str: Any]]:
        return await self.game_repository.get_players(game_id)

    async def get_teams(self, game_id: str) -> List[dict[str: Any]]:
        return await self.game_repository.get_teams(game_id)

    async def sender_is_current_player(
            self,
            game_id: str,
            websocket: WebSocket,
            con: dict[int, WebSocket]
    ) -> bool:
        current_player_id = await self.game_repository.get_current_player_id(game_id)
        current_player = con.get(current_player_id)

        return current_player and current_player == websocket
