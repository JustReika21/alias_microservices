class AuthException(Exception):
    pass


class UserCreationError(AuthException):
    pass


class UserLoginError(AuthException):
    pass


class InvalidToken(AuthException):
    pass


class TokenNotFound(AuthException):
    pass


class TokenExpired(AuthException):
    pass


class UserNotFound(AuthException):
    pass
