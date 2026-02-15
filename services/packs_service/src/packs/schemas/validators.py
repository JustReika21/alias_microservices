from typing import Annotated

from packs.schemas.utils import strip_whitespace
from pydantic import BeforeValidator, Field

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 127
DESCRIPTION_MIN_LENGTH = 2
DESCRIPTION_MAX_LENGTH = 1024

NAME = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
    )
]

DESCRIPTION = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    Field(
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
]
