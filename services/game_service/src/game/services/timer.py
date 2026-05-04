from game.repositories.timer import GameTimerRepository


class GameTimerService:
    def __init__(
            self,
            timer_repo: GameTimerRepository,
    ):
        self.timer_repo = timer_repo

    async def set_timer(self, game_id: str, end_time: int) -> None:
        await self.timer_repo.set_timer(game_id, end_time)

    async def get_timer(self, game_id: str) -> int:
        end_time = await self.timer_repo.get_timer(game_id)
        return end_time
