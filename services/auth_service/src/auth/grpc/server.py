import asyncio

import grpc
from auth.grpc.servicer import User
from auth_grpc.v1 import auth_grpc_pb2_grpc


async def start_grpc_server():
    server = grpc.aio.server()
    auth_grpc_pb2_grpc.add_AuthServicer_to_server(User(), server)
    server.add_insecure_port("[::]:50051")
    print(f'''
========================================
Starting auth-grpc server on port 50051
========================================
''')
    await server.start()
    return  server
