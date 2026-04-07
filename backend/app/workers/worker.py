from rq import Worker, Queue
from app.core.redis_connection import redis_client

if __name__ == "__main__":
    queue = Queue("job-queue", connection=redis_client)
    worker = Worker([queue], connection=redis_client)
    worker.work()