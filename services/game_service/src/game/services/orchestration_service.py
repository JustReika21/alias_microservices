import asyncio

from starlette.websockets import WebSocket

from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository
from game.services.broadcast_service import GameBroadcastService
from game.services.core import GameCoreService
from game.services.round_service import GameRoundService
from game.services.score_service import GameScoreService
from game.services.snapshot_service import GameSnapshotService


class GameOrchestrationService:
    def __init__(
            self,
            repo: GameRepository,
            broadcast: GameBroadcastService,
            core: GameCoreService,
            round_service: GameRoundService,
            score_service: GameScoreService,
            snapshot_service: GameSnapshotService,
            auth_client: AuthClient,
            cards_client: CardsClient,
            packs_client: PacksClient,

    ):
        self.repo = repo

        self.broadcast = broadcast
        self.core = core
        self.round_service = round_service
        self.score_service = score_service
        self.snapshot_service = snapshot_service

        self.auth_client = auth_client
        self.cards_client = cards_client
        self.packs_client = packs_client

    async def handle_snapshot(
            self,
            game_id: str,
            user_id: int,
            game_status: str,
            ws: WebSocket,
    ):
        current_player_id = await self.repo.get_current_player_id(game_id)

        snapshot = await self.snapshot_service.load_snapshot(
            game_id, user_id, game_status, current_player_id
        )

        await self.broadcast.send_to(ws, snapshot)

    async def handle_start_round(self, game_id: str, con: dict[int, WebSocket]):
        await self.repo.set_game_status(game_id, 'started')
        asyncio.create_task(self._run_round(game_id, con))

    async def _run_round(
            self,
            game_id: str,
            con: dict[int, WebSocket]
    ):
        round_time = await self.repo.get_round_time(game_id)
        pack_id = await self.repo.get_pack_id(game_id)
        cards = await self.cards_client.get_random_cards(pack_id, 100)

        await self.repo.set_game_cards(game_id, cards)
        await self.repo.set_card_cursor(game_id)

        end_time = await self.round_service.set_timer(game_id, round_time)

        await self.broadcast.broadcast(con, {'type': 'status', 'value': 'started'})
        await self.broadcast.broadcast(con, {'type': 'timer', 'end_time': end_time})

        await self.send_card(game_id, con)

        await asyncio.sleep(round_time)

        await self.repo.set_game_status(game_id, 'calculating')

        await self._send_final_card(game_id, con)

        await self.repo.set_guessed_cards(game_id)

    async def handle_switch_team(
            self,
            game_id: str,
            player_id: int,
            new_team_id: int,
            con: dict[int, WebSocket]
    ):
        teams = await self.core.switch_team(game_id, player_id, new_team_id)
        payload = {'type': 'teams', 'teams': teams}

        await self.broadcast.broadcast(con, payload)

    async def _broadcast_card(self, card: dict, ws: WebSocket):
        payload = {'type': 'card', 'card': card, 'guessed': True}
        await self.broadcast.send_to(ws, payload)

    async def send_card(self, game_id: str, con: dict[int, WebSocket]):
        current_player_id = await self.core.get_current_player(game_id)

        data = await self.round_service.get_card(game_id, current_player_id)

        if data is None:
            await self.repo.set_game_status(game_id, 'calculating')
            return
        
        for user_id, ws in con.items():
            card = (
                data['current_card']
                if user_id == data['current_player_id']
                else data['previous_card']
            )
            await self._broadcast_card(card, ws)

    async def _send_final_card(self, game_id: str, con: dict[int, WebSocket]):
        current_player_id = await self.core.get_current_player(game_id)

        card = await self.round_service.get_final_card(game_id, current_player_id)

        for user_id, ws in con.items():
            if current_player_id != user_id:
                await self._broadcast_card(card, ws)

        await self.broadcast.broadcast(con, {'type': 'status', 'value': 'calculating'})

    async def handle_card_guess(
            self,
            game_id: str,
            card_id: int,
            guessed: bool,
            con: dict[int, WebSocket]
    ):
        played_cards = await self.repo.get_played_cards(game_id)

        payload = await self.round_service.card_guessed(
            game_id, card_id, guessed, played_cards
        )

        if payload is not None:
            await self.broadcast.broadcast(con, payload)


    async def handle_calculating(self, game_id: str, con: dict[int, WebSocket]):
        await self.repo.set_game_status(game_id, 'waiting')

        guessed_card_ids = await self.core.get_guessed_cards(game_id)
        current_player_id = await self.core.get_current_player(game_id)
        current_team_id = await self.core.get_current_team(game_id)

        await self.repo.cleanup_round(game_id)

        result = await self.score_service.set_scores(
            game_id, guessed_card_ids, current_player_id, current_team_id
        )

        for ws in con.values():
            await self.broadcast.send_to(ws, {
                'type': 'player_score_update',
                'id': result.player.id,
                'score': result.player.score
            })
            await self.broadcast.send_to(ws, {
                'type': 'team_score_update',
                'id': result.team.id,
                'score': result.team.score
            })

        await self._handle_next_round(game_id, con)

    async def _handle_next_round(self, game_id, con: dict[int, WebSocket]):
        next_player_id = await self.round_service.next_round(game_id)

        for user_id, ws in con.items():
            payload = {
                    'type': 'current_player',
                    'player_id': next_player_id,
                    'is_current': user_id == next_player_id
                }
            await self.broadcast.send_to(ws, payload)

        await self.broadcast.broadcast(con, {'type': 'status', 'value': 'waiting'})

    async def sender_is_current_player(
            self,
            game_id: str,
            websocket: WebSocket,
            con: dict[int, WebSocket]
    ) -> bool:
        current_player_id = await self.core.get_current_player(game_id)
        current_player = con.get(current_player_id)

        return current_player and current_player == websocket
