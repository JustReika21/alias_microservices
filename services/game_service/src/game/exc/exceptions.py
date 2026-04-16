class GameException(Exception):
    pass


class GameCreationError(GameException):
    pass


class GameNotFoundError(GameException):
    pass


class GameClosedError(GameException):
    pass


class TeamNotFoundError(GameException):
    pass