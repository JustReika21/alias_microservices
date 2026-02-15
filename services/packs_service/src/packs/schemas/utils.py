def strip_whitespace(v: str) -> str:
    if not isinstance(v, str):
        raise TypeError('Expected a string')
    return v.strip()
