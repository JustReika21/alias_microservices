class PackException(Exception):
    pass


class PackCreationError(PackException):
    pass


class PackUpdateError(PackException):
    pass


class PackDoesNotExist(PackException):
    pass


class PermissionDenied(PackException):
    pass


class PackDeletionError(PackException):
    pass
