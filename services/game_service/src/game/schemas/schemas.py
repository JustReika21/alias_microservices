from typing import List

from pydantic import BaseModel


class GameBase(BaseModel):
    pass


class Player(GameBase):
    id: int
    name: str
    score: int = 0
    team_id: int = 1


class Team(GameBase):
    id: int
    players_ids: List[int] = []
    score: int = 0


class GameCreate(BaseModel):
    rounds: int
    time: int = 60
    pack: int
    password: str | None = None


class Game(GameBase):
    id: str
    host: int
    team_offset: int = 0
    rounds: int
    current_round: int = 0
    time: int = 60
    pack: int
    password: str | None = None
    status: str = 'setting_up'

class GameCreated(GameBase):
    id: str
