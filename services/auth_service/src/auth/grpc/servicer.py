from auth.database.db import async_session
from auth.repositories.repository import UserRepository
from auth.services.service import UserService
from auth.services.utils import ACCESS_TOKEN_TYPE
from auth_grpc.v1 import auth_grpc_pb2, auth_grpc_pb2_grpc


class User(auth_grpc_pb2_grpc.AuthServicer):
    async def VerifyUserWebSoket(self, request, context):
        refresh_token = request.refresh_token
        async with async_session() as db:
            service = UserService(UserRepository(db))
            user = await service.validate_refresh_token_for_websocket(refresh_token)
        return auth_grpc_pb2.VerifyUserWebSoketResp(user_id=user.id, name=user.name)

    async def GetUser(self, request, context):
        access_token = request.access_token
        async with async_session() as db:
            service = UserService(UserRepository(db))
            user = await service.get_auth_user(access_token, ACCESS_TOKEN_TYPE)
        return auth_grpc_pb2.GetUserResp(user_id=user.id,name=user.name)
