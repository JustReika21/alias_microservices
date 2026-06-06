from game.repositories.round import GameRoundRepository


class GameRoundService:
    def __init__(
            self,
            round_repo: GameRoundRepository,
    ):
        self.round_repo = round_repo

    async def resolve_turn_offset(
            self,
            game_id: str,
            team_idx: int,
    ) -> int:
        if team_idx == 0:
            turn_offset = await self.round_repo.increment_current_round(game_id)
        else:
            turn_offset = await self.round_repo.get_current_round(game_id)

        return turn_offset

    async def cleanup_round(self, game_id: str) -> None:
        await self.round_repo.cleanup_round(game_id)

    async def get_total_rounds(self, game_id: str) -> int:
        total_rounds = await self.round_repo.get_total_rounds(game_id)
        return total_rounds

    async def get_current_round(self, game_id: str) -> int:
        current_round = await self.round_repo.get_current_round(game_id)
        return current_round

    async def reset_rounds(self, game_id: str) -> None:
        await self.round_repo.reset_rounds(game_id)
