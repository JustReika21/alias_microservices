from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.exc.exceptions import InvalidToken, UserNotFound
from auth.schemas.schemas import UserCreate, UserLogin, TokenInfo, UserRead
from auth.services.service import create_user, validate_auth_user, get_user
from auth.services.utils import encode_jwt, decode_jwt
from auth.dependencies import get_session

auth_router = APIRouter(tags=['Authentication'])

security = HTTPBearer()


@auth_router.post('/register')
async def user_create_view(
        data: UserCreate,
        db: AsyncSession = Depends(get_session)
) -> None:
    await create_user(data, db)


@auth_router.post('/login')
async def user_login(
        data: UserLogin,
        db: AsyncSession = Depends(get_session)
) -> TokenInfo:
    user = await validate_auth_user(data, db)
    jwt_payload = {
        'sub': user.id,
        'name': user.name,
    }
    token = encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="Bearer")


@auth_router.post('/user')
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_session)
) -> UserRead:
    token = credentials.credentials

    try:
        payload = decode_jwt(token)
    except:
        raise InvalidToken('Invalid token')

    user_id = payload.get('sub')
    if not user_id:
        raise InvalidToken('Invalid token payload')

    user = await get_user(int(user_id), db)
    if not user:
        raise UserNotFound('User not found')

    return user


@auth_router.post('/test')
async def test(user_id: int, db: AsyncSession = Depends(get_session)):
    return await get_user(user_id, db)
