import asyncio
import json

from redis.asyncio import Redis

from game.services.connection_manager import ConnectionManager


import json
import asyncio
from redis.asyncio import Redis


async def redis_listener(redis: Redis, queue: asyncio.Queue):
    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.psubscribe('alias:game:sub:*')

            async for msg in pubsub.listen():
                if msg['type'] != 'pmessage':
                    continue

                try:
                    data = json.loads(msg['data'])
                except Exception:
                    continue

                try:
                    queue.put_nowait(data)
                except asyncio.QueueFull:
                    print('WS queue full')

        except Exception as e:
            print('Redis listener crashed:', e)
            await asyncio.sleep(1)


async def ws_worker(queue: asyncio.Queue, manager):
    while True:
        data = await queue.get()

        try:
            game_id = data['game_id']

            if 'user_id' in data:
                await manager.send_to(game_id, data['user_id'], data)
            else:
                await manager.broadcast(game_id, data)

        except Exception as e:
            print('WS worker error:', e)

        finally:
            queue.task_done()
