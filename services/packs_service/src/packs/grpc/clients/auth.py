from typing import Optional

import grpc
import grpc.aio
from auth_grpc.v1.auth_grpc_pb2 import GetUserReq
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

    async def get_user(self, access_token: str):
        response = await self.stub.GetUser(GetUserReq(access_token=access_token))
        return response
