from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthBase(BaseModel):
    pass


class UserCreate(AuthBase):
    name: str
    password: str


class UserLogin(AuthBase):
    name: str
    password: str


class UserRead(AuthBase):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TokenInfo(AuthBase):
    access_token: str
    refresh_token: str | None = None
    token_type: str = 'Bearer'


class RefreshTokenCreate(AuthBase):
    user_id: int
    token: str
    expires_at: datetime

