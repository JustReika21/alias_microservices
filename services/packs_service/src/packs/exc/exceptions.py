class PackException(Exception):
    pass


class PackCreationError(PackException):
    pass


class PackUpdateError(PackException):
    pass


class PackDoesNotExist(PackException):
    pass