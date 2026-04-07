from rq import Queue
from app.core.redis_connection import redis_client

queue = Queue("job-queue", connection=redis_client)