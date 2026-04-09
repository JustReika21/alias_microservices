class AuthException(Exception):
    pass


class UserCreationError(AuthException):
    pass


class UserLoginError(AuthException):
    pass


class InvalidToken(AuthException):
    pass


class UserNotFound(AuthException):
    pass
