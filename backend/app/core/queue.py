from rq import Queue
from redis import Redis


def get_queue(redis_client: Redis):
    if not redis_client:
        raise ValueError("Redis client is not initialized")
    return Queue("job-queue", connection=redis_client)
