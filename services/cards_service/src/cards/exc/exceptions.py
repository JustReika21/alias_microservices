class CardException(Exception):
    pass


class CardCreationError(CardException):
    pass


class CardError(CardException):
    pass


class CardDoesNotExistError(CardException):
    pass


class CardDeletionError(CardException):
    pass
