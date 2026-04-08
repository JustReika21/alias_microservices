from typing import List

from pydantic import BaseModel

from game.database.models import generate_id


class GameBase(BaseModel):
    pass


class Player(GameBase):
    id: int
    name: str
    score: int = 0


class Game(GameBase):
    id: str
    host: int
    current_player: int
    turn_offset: int
    rounds: int
    current_round: int = 0
    time: int
    pack: int
    password: str = None
    status: str = 'waiting'
    total_players: int