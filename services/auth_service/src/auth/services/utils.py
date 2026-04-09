from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

from auth.database.models import User
from auth.exc.exceptions import InvalidToken
from auth.settings import settings

TOKEN_TYPE_FIELD = 'type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def create_jwt(token_type: str, token_data: dict, expire_minutes: int) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    token = encode_jwt(jwt_payload, expire_minutes)
    return token


def create_access_token(user: User) -> str:
    jwt_payload = {
        'sub': str(user.id),
        'name': user.name,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes
    )


def create_refresh_token(user: User) -> str:
    jwt_payload = {
        'sub': str(user.id),
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.refresh_token_expire_minutes
    )


def validate_token_type(payload: dict, token_type: str) -> bool:
    if payload.get('type') == token_type:
        return True
    raise InvalidToken('Invalid token type')


def encode_jwt(
        payload: dict,
        expire_minutes: int,
        key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire)
    encoded = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded


def decode_jwt(
        encoded: str | bytes,
        key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(encoded, key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password=hashed_password)
