from typing import Annotated

from pydantic import Field, BeforeValidator

from cards.schemas.utils import strip_whitespace

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