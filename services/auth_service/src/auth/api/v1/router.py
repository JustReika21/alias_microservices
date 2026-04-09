from fastapi import APIRouter, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.schemas.schemas import UserCreate, UserLogin, TokenInfo, UserRead
from auth.services.service import UserService
from auth.services.utils import create_access_token, \
    create_refresh_token, ACCESS_TOKEN_TYPE
from auth.dependencies import get_user_service

auth_router = APIRouter(tags=['Authentication'])

security = HTTPBearer()


@auth_router.post('/register')
async def user_create_view(
        data: UserCreate,
        user_service: UserService = Depends(get_user_service)
) -> None:
    await user_service.create_user(data)


@auth_router.post('/login')
async def user_login(
        data: UserLogin,
        response: Response,
        user_service: UserService = Depends(get_user_service)
) -> TokenInfo:
    user = await user_service.validate_auth_user(data)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    await user_service.save_refresh_token(user.id, refresh_token)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax'
    )

    return TokenInfo(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")

@auth_router.post('/user', response_model=UserRead)
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        user_service: UserService = Depends(get_user_service)
):
    token = credentials.credentials
    user = await user_service.get_auth_user(token, ACCESS_TOKEN_TYPE)
    return user

@auth_router.post('/refresh')
async def refresh_jwt(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        user_service: UserService = Depends(get_user_service)
) -> TokenInfo:
    token = credentials.credentials
    user_id = await user_service.validate_refresh_token(token)

    user = await user_service.get_user(user_id)
    access_token = create_access_token(user)

    return TokenInfo(access_token=access_token, token_type="Bearer")
