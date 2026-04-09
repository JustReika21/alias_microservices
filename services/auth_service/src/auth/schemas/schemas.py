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
    token_type: str
