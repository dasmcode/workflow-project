import redis, os
import redis.asyncio as async_redis
import logging

logger = logging.getLogger(__name__)

REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
redis_client = redis.Redis(host=REDIS_SERVER, port=6379, db=0)


class RedisManager:
    def __init__(self):
        self.sync_client = None
        self.async_client = None
        self.REDIS_URL = f"redis://{os.getenv('REDIS_SERVER', 'localhost')}:6379/0"

    def connect_sync(self):
        if not self.sync_client:
            self.sync_client = redis.from_url(self.REDIS_URL)
            logger.info("Initialized redis sync client")

    async def connect_async(self):
        if not self.async_client:
            self.async_client = async_redis.from_url(self.REDIS_URL)
            logger.info("Initialized redis async client")

    async def disconnect_all(self):
        if self.async_client:
            await self.async_client.close()
        if self.sync_client:
            self.sync_client.close()
        logger.info("Disconnected redis clients")


redis_manager = RedisManager()
