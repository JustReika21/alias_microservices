from fastapi import APIRouter, Response, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from auth.schemas.schemas import UserCreate, UserLogin, TokenInfo, UserRead
from auth.services.service import UserService
from auth.services.utils import create_access_token, \
    create_refresh_token, ACCESS_TOKEN_TYPE, decode_jwt
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
        secure=False,
        samesite='lax'
    )

    return TokenInfo(access_token=access_token, token_type="Bearer")


@auth_router.post('/me', response_model=UserRead)
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        user_service: UserService = Depends(get_user_service)
):
    token = credentials.credentials
    user = await user_service.get_auth_user(token, ACCESS_TOKEN_TYPE)
    return user


@auth_router.post('/refresh')
async def refresh_jwt(
        request: Request,
        user_service: UserService = Depends(get_user_service)
) -> TokenInfo:
    refresh_token = request.cookies.get('refresh_token')

    access_token = await user_service.refresh(refresh_token)

    return access_token


@auth_router.get('/verify')
async def verify(
        response: Response,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    token = credentials.credentials

    payload = decode_jwt(token)

    response.headers['X-User-Id'] = str(payload['sub'])
    return JSONResponse(content={'X-User-Id': str(payload["sub"])}, status_code=status.HTTP_200_OK)


@auth_router.get('/wsverify')
async def websocket_verify(
        refresh_token: str,
        user_service: UserService = Depends(get_user_service)
) -> UserRead:
    user = await user_service.validate_refresh_token_for_websocket(refresh_token)
    return user
