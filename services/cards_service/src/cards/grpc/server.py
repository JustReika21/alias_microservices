import asyncio

import grpc
from cards.grpc.servicer import Cards
from cards_grpc.v1 import cards_grpc_pb2_grpc


async def start_grpc_server(packs_client):
    server = grpc.aio.server()
    cards_grpc_pb2_grpc.add_CardsServicer_to_server(Cards(packs_client), server)
    server.add_insecure_port("[::]:50051")
    print(f'''
========================================
Starting cards-grpc server on port 50051
========================================
''')
    await server.start()
    return  server

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
