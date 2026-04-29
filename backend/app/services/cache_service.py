import json
from app.core.redis_connection import redis_manager
import logging

logger = logging.getLogger(__name__)


async def set_step_data(job_id: str, step_name: str, data, ttl: int = 3600):
    key = f"job:{job_id}:step:{step_name}"
    try:
        serialized_data = json.dumps(data)
        await redis_manager.async_client.set(key, serialized_data, ex=ttl)
        logger.info(
            f"[CACHE] SET {key}", extra={"job_id": job_id, "step_name": step_name}
        )
    except Exception as e:
        logger.error(
            f"Error occurred while setting step data: {str(e)}",
            extra={"job_id": job_id, "step_name": step_name},
        )


async def get_step_data(job_id: str, step_name: str):
    key = f"job:{job_id}:step:{step_name}"
    data = await redis_manager.async_client.get(key)
    if not data:
        return None
    try:
        deserialized_data = json.loads(data)
        logger.info(
            f"[CACHE] GET {key}", extra={"job_id": job_id, "step_name": step_name}
        )
        return deserialized_data
    except Exception as e:
        logger.error(
            f"Error occurred while loading step data: {str(e)}",
            extra={"job_id": job_id, "step_name": step_name},
        )
        return None


async def delete_step_data(job_id: str, step_name: str):
    key = f"job:{job_id}:step:{step_name}"
    try:
        await redis_manager.async_client.delete(key)
        logger.info(
            f"[CACHE] DELETE {key}", extra={"job_id": job_id, "step_name": step_name}
        )
    except Exception as e:
        logger.error(
            f"Error occurred while deleting step data: {str(e)}",
            extra={"job_id": job_id, "step_name": step_name},
        )
