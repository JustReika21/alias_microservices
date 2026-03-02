from typing import Annotated

from cards.schemas.utils import strip_whitespace
from pydantic import BeforeValidator, Field

WORD_MIN_LENGTH = 2
WORD_MAX_LENGTH = 127

WORD = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    Field(
        min_length=WORD_MIN_LENGTH,
        max_length=WORD_MAX_LENGTH,
    )
]

LIMIT = Annotated[
    int,
    Field(
        ge=1,
        le=5000,
    )
]