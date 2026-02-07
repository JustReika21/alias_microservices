import asyncio

import grpc
from packs.grpc.servicer import Packs
from packs_grpc.v1 import packs_grpc_pb2_grpc


async def start_grpc_server():
    server = grpc.aio.server()
    packs_grpc_pb2_grpc.add_PacksServicer_to_server(Packs(), server)
    server.add_insecure_port("[::]:50051")
    print(f'''
========================================
Starting packs-grpc server on port 50051
========================================
''')
    await server.start()
    return  server

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
