from rq import Worker, Queue
from app.core.redis_connection import redis_manager
from app.core.logging_config import setup_logging
from app.core.queue import get_queue
import logging, asyncio

logger = logging.getLogger(__name__)


async def main():
    setup_logging()
    redis_manager.connect_sync()
    await redis_manager.connect_async()
    try:
        queue = get_queue(redis_manager.sync_client)
        worker = Worker([queue], connection=redis_manager.sync_client)
        logger.info("Worker starting...")
        worker.work()
    except Exception as e:
        logger.error(f"Error occurred while starting worker: {str(e)}")
    finally:
        await redis_manager.disconnect_all()


if __name__ == "__main__":
    asyncio.run(main())
