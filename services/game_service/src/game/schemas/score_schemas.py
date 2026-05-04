from game.schemas.schemas import GameBase


class PlayerScore(GameBase):
    id: int
    score: int


class TeamScore(GameBase):
    id: int
    score: int
