from typing import Optional

import grpc
import grpc.aio
from auth_grpc.v1.auth_grpc_pb2 import VerifyUserWebSoketReq, GetUserReq
from auth_grpc.v1.auth_grpc_pb2_grpc import AuthStub


class AuthClient:
    def __init__(self, target: str):
        self.target = target
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[AuthStub] = None

    async def connect(self):
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = AuthStub(self.channel)

    async def close(self):
        if self.channel:
            await self.channel.close()

    async def verify_user_websocket(self, refresh_token: str):
        response = await self.stub.VerifyUserWebSoket(VerifyUserWebSoketReq(refresh_token=refresh_token))
        return response

    async def get_user(self, refresh_token: str):
        response = await self.stub.GetUser(GetUserReq(refresh_token=refresh_token))
        return response
