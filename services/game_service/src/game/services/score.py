from typing import List

from game.repositories.score import GameScoreRepository
from game.schemas.score_schemas import PlayerScore, TeamScore


class GameScoreService:
    def __init__(
            self,
            score_repo: GameScoreRepository
    ):
        self.score_repo = score_repo

    async def update_player_score(self, game_id: str, current_player_id: int, points: int):
        player_score = await self.score_repo.update_player_score(
            game_id, current_player_id, points
        )
        result = PlayerScore(id=current_player_id, score=player_score)
        return result

    async def update_team_score(self, game_id: str, current_team_id: int, points: int):
        team_score = await self.score_repo.update_team_score(
            game_id, current_team_id, points
        )
        result = TeamScore(id=current_team_id, score=team_score)
        return result

    async def reset_scores(self, game_id: str, player_ids: List[str], team_ids: List[str]):
        await self.score_repo.reset_scores(game_id, player_ids, team_ids)
