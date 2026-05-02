from game.repositories.repository import GameRepository
from game.schemas.score_schemas import ScoreResult, PlayerScore, TeamScore


class GameScoreService:
    def __init__(self, repo: GameRepository):
        self.repo = repo

    async def set_scores(
            self,
            game_id: str,
            guessed_card_ids: set[int],
            current_player_id: int,
            current_team_id: int,
    ):
        points = len(guessed_card_ids)

        player_score = await self.repo.update_player_score(
            game_id, current_player_id, points
        )

        team_score = await self.repo.update_team_score(
            game_id, current_team_id, points
        )

        result = ScoreResult(
            player=PlayerScore(id=current_player_id, score=player_score),
            team=TeamScore(id=current_team_id, score=team_score)
        )

        return result
