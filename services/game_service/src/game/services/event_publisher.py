import json

from redis.asyncio import Redis


class GameEventPublisher:
    def __init__(self, redis: Redis):
        self.redis_client = redis

    async def publish(self, game_id: str, payload: dict):
        await self.redis_client.publish(
            f'alias:game:sub:{game_id}',
            json.dumps({
                'game_id': game_id,
                **payload
            })
        )
