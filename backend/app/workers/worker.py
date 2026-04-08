from rq import Worker, Queue
from app.core.redis_connection import redis_client
from app.core.logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    queue = Queue("job-queue", connection=redis_client)
    worker = Worker([queue], connection=redis_client)
    worker.work()