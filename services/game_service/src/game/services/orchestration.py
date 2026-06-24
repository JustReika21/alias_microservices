import asyncio
from time import time
from typing import List

from starlette.websockets import WebSocket

from game.database.models import generate_id
from game.exc.exceptions import GameAlreadyStartedError
from game.grpc.clients.auth import AuthClient
from game.grpc.clients.packs import PacksClient
from game.schemas.schemas import GameCreate, Player, Game, GameCreated
from game.services.broadcast import GameBroadcastService
from game.services.card import GameCardService
from game.services.connection_manager import ConnectionManager
from game.services.core import GameCoreService
from game.services.event_publisher import GameEventPublisher
from game.services.player import GamePlayerService
from game.services.round import GameRoundService
from game.services.score import GameScoreService
from game.services.snapshot import GameSnapshotService
from game.services.team import GameTeamService
from game.services.timer import GameTimerService

DEFAULT_TEAM_ID = 1


class GameOrchestrationService:
    def __init__(
            self,
            broadcast_service: GameBroadcastService,
            card_service: GameCardService,
            core_service: GameCoreService,
            event_publisher: GameEventPublisher,
            player_service: GamePlayerService,
            round_service: GameRoundService,
            score_service: GameScoreService,
            team_service: GameTeamService,
            timer_service: GameTimerService,
            snapshot_service: GameSnapshotService,

            auth_client: AuthClient,
            packs_client: PacksClient,
    ):
        self.card_service = card_service
        self.core_service = core_service
        self.event_publisher = event_publisher
        self.player_service = player_service
        self.round_service = round_service
        self.score_service = score_service
        self.team_service = team_service
        self.timer_service = timer_service
        self.snapshot_service = snapshot_service

        self.auth_client = auth_client
        self.packs_client = packs_client

    async def create_game(self, game_data: GameCreate, player: Player) -> GameCreated:
        game = Game(
            id=generate_id(),
            host=player.id,
            rounds=game_data.rounds,
            time=game_data.time,
            pack=game_data.pack,
            password=game_data.password or ''
        )

        await self.core_service.create_game(game)
        await self.team_service.create_team(game.id, DEFAULT_TEAM_ID)
        await self.player_service.join_game(game.id, player)

        game = GameCreated(id=game.id)
        return game

    async def join_game(self, game_id: str, user, game_status: str) -> Player:
        player_exists = await self.is_player_exist(game_id, user.user_id)

        if player_exists:
            player = await self.player_service.get_player(game_id, user.user_id)
            player = Player.model_validate(player)
            await self.player_service.connect_player(game_id, user.user_id)
        elif game_status == 'setting_up':
            player = Player(id=user.user_id, name=user.name)
            await self.player_service.join_game(game_id, player)
        else:
            raise GameAlreadyStartedError('Game already started')

        return player

    async def handle_snapshot(
            self,
            game_id: str,
            user_id: int,
            game_status: str,
            my_id: int,
    ):
        players = await self.get_players(game_id)
        current_player_id = await self.get_current_player_id(game_id)
        host = await self.get_host_id(game_id)
        teams = await self.get_teams(game_id)

        played_cards = None
        end_time = None
        winners = None

        if game_status == 'started' or game_status == 'calculating':
            played_cards = await self.card_service.get_played_cards(game_id)
            end_time = await self.timer_service.get_timer(game_id)
        elif game_status == 'finished':
            winners = await self._get_winners(game_id)

        snapshot = await self.snapshot_service.load_snapshot(
            user_id, game_status, players, my_id, current_player_id, host, teams,
            played_cards, end_time, winners
        )

        await self.event_publisher.publish(game_id, snapshot)

    async def handle_set_up(self, game_id: str):
        await self.core_service.set_game_status(game_id, 'waiting')
        await self.event_publisher.publish(game_id, {'type': 'status', 'value': 'waiting'})

    async def handle_start_round(self, game_id: str):
        await self.core_service.set_game_status(game_id, 'started')
        asyncio.create_task(self._run_round(game_id))

    async def _run_round(self, game_id: str):
        round_time = await self.core_service.get_round_time(game_id)
        pack_id = await self.core_service.get_pack_id(game_id)

        await self.card_service.set_up_game_cards(game_id, pack_id)

        end_time = int(time() + round_time)
        await self.timer_service.set_timer(game_id, end_time)

        await self.event_publisher.publish(
            game_id, {'type': 'status', 'value': 'started'}
        )
        await self.event_publisher.publish(
            game_id,{'type': 'timer', 'end_time': end_time}
        )

        await self.send_card(game_id)

        await asyncio.sleep(round_time)

        await self.core_service.set_game_status(game_id, 'calculating')

        await self._send_final_card(game_id)

        await self.card_service.set_guessed_cards(game_id)

    async def handle_switch_team(
            self,
            game_id: str,
            player_id: int,
            new_team_id: int,
    ):
        old_team_id = await self.player_service.get_player_team_id(game_id, player_id)

        await self.team_service.switch_team(
            game_id, player_id, new_team_id, old_team_id
        )

        current_player_id = await self.get_current_player_id(game_id)

        payload = {
            'type': 'player_switch_team',
            'player_id': player_id,
            'new_team_id': new_team_id,
            'current_player_id': current_player_id,
        }

        await self.event_publisher.publish(game_id, payload)

    async def send_card(self, game_id: str):
        current_player_id = await self.get_current_player_id(game_id)

        data = await self.card_service.get_card(game_id, current_player_id)

        if data is None:
            return

        current_card = data['current_card']
        previous_card = data['previous_card']

        await self._broadcast_card(
            game_id, current_card, previous_card, current_player_id
        )

    async def _broadcast_card(
            self,
            game_id: str,
            current_card,
            previous_card,
            current_player_id
    ):
        payload = {
            'type': 'card',
            'current_card': current_card,
            'previous_card': previous_card,
            'current_player_id': current_player_id,
        }
        await self.event_publisher.publish(game_id, payload)

    async def _send_final_card(self, game_id: str):
        current_player_id = await self.get_current_player_id(game_id)

        current_card = None
        previous_card = await self.card_service.get_final_card(game_id)

        await self._broadcast_card(
            game_id, current_card, previous_card, current_player_id
        )

        await self.event_publisher.publish(
            game_id, {'type': 'status', 'value': 'calculating'}
        )

    async def handle_card_guess(
            self,
            game_id: str,
            card_id: int,
            guessed: bool,
    ):
        played_cards = await self.card_service.get_played_cards(game_id)

        payload = await self.card_service.card_guessed(
            game_id, card_id, guessed, played_cards
        )

        if payload is not None:
            await self.event_publisher.publish(game_id, payload)

    async def handle_calculating(self, game_id: str):
        await self.core_service.set_game_status(game_id, 'waiting')

        guessed_card_ids = await self.card_service.get_guessed_cards(game_id)
        current_player_id = await self.get_current_player_id(game_id)
        current_team_id = await self.team_service.get_current_team_id(game_id)

        points = len(guessed_card_ids)

        player = await self.score_service.update_player_score(
            game_id, current_player_id, points
        )

        team = await self.score_service.update_team_score(
            game_id, current_team_id, points
        )

        await self.event_publisher.publish(game_id, {
            'type': 'player_score_update',
            'id': player.id,
            'score': player.score
        })
        await self.event_publisher.publish(game_id, {
            'type': 'team_score_update',
            'id': team.id,
            'score': team.score
        })

        await self.round_service.cleanup_round(game_id)
        await self._handle_next_round(game_id)

    async def _handle_next_round(self, game_id):
        total_rounds = await self.round_service.get_total_rounds(game_id)
        team_ids = await self.team_service.get_team_ids(game_id)
        team_offset = await self.team_service.increment_team_offset(game_id)

        team_idx = int(team_offset) % len(team_ids)
        team_id = team_ids[team_idx]

        turn_offset = await self.round_service.resolve_turn_offset(
            game_id, team_idx
        )

        team_player_ids = await self.team_service.get_team_player_ids(game_id, team_id)

        idx = int(turn_offset) % len(team_player_ids)
        next_player_id = int(team_player_ids[idx])

        payload = {
                'type': 'current_player',
                'player_id': next_player_id,
            }
        await self.event_publisher.publish(game_id, payload)

        if turn_offset == total_rounds:
            await self._handle_end_game(game_id)
        else:
            await self.event_publisher.publish(
                game_id, {'type': 'status', 'value': 'waiting'}
            )

    async def _handle_end_game(self, game_id: str):
        winners = await self._get_winners(game_id)

        await self.core_service.set_game_status(game_id, 'finished')
        await self.event_publisher.publish(
            game_id, {'type': 'end_game', 'status': 'finished', 'winners': winners}
        )

    async def _get_winners(self, game_id: str) -> List[str]:
        teams = await self.team_service.get_teams(game_id)

        winners = set()
        highest_score = 0
        for team in teams:
            team_score = int(team.get('score'))
            if team_score > highest_score:
                winners = {team.get('id')}
                highest_score = team_score
            elif team_score == highest_score:
                winners.add(team.get('id'))

        return list(winners)

    async def restart_game(self, game_id: str):
        players = await self.get_players(game_id)
        teams = await self.get_teams(game_id)

        player_ids = [player.get('id') for player in players]
        team_ids = [team.get('id') for team in teams]

        await self.round_service.reset_rounds(game_id)
        await self.score_service.reset_scores(game_id, player_ids, team_ids)

        await self.event_publisher.publish(
            game_id, {
                'type': 'restart',
                'players': player_ids,
                'teams': team_ids,
            }
        )

        await self.core_service.set_game_status(game_id, 'setting_up')

        current_player = await self.get_current_player_id(game_id)

        payload = {'type': 'current_player', 'player_id': current_player}
        await self.event_publisher.publish(game_id, payload)

    async def sender_is_current_player(
            self,
            game_id: str,
            user_id: int,
    ) -> bool:
        current_player_id = await self.get_current_player_id(game_id)
        return int(current_player_id) == user_id

    async def sender_is_host(
            self,
            game_id: str,
            user_id: int,
    ) -> bool:
        host_id = await self.get_host_id(game_id)
        return int(host_id) == user_id

    async def get_current_player_id(self, game_id: str) -> int:
        team_id = await self.team_service.get_current_team_id(game_id)
        team_players = await self.team_service.get_team_player_ids(game_id, team_id)

        turn_offset = await self.round_service.get_current_round(game_id)

        idx = int(turn_offset) % len(team_players)

        current_player_id = team_players[idx]
        return int(current_player_id)

    async def get_players(self, game_id: str) -> List[dict]:
        team_ids = await self.team_service.get_team_ids(game_id)
        team_player_ids = await self.team_service.get_every_team_player_ids(game_id, team_ids)

        players = await self.player_service._get_players(game_id, team_player_ids)
        return players

    async def is_game_exist(self, game_id: str) -> bool:
        exists = await self.core_service.is_game_exist(game_id)
        return exists

    async def get_game_status(self, game_id: str) -> str:
        status = await self.core_service.get_game_status(game_id)
        return status

    async def get_host_id(self, game_id: str) -> int:
        host = await self.core_service.get_host_id(game_id)
        return host

    async def get_teams(self, game_id: str) -> List[dict]:
        teams = await self.team_service.get_teams(game_id)
        return teams

    async def is_player_exist(self, game_id: str, player_id: int) -> bool:
        player_exists = await self.player_service.is_player_exist(game_id, player_id)
        return player_exists

    async def disconnect_user(self, game_id: str, user_id: str) -> None:
        await self.player_service.disconnect_player(game_id, user_id)
        await self.event_publisher.publish(
            game_id, {'type': 'player_disconnected', 'disconnected_user_id': user_id}
        )

    async def kick_player(self, game_id: str, user_id: str) -> None:
        player = await self.player_service.get_player(game_id, user_id)

        await self.team_service.remove_player_from_team(game_id, player)
        await self.player_service.remove_player(game_id, player.get('id'))

        await self.event_publisher.publish(
            game_id, {'type': 'player_kicked', 'kicked_user_id': user_id}
        )

        current_player = await self.get_current_player_id(game_id)
        payload = {'type': 'current_player', 'player_id': current_player}
        await self.event_publisher.publish(game_id, payload)
        