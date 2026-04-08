import json
from app.core.redis_connection import redis_client
import logging
logger = logging.getLogger(__name__)

def set_step_data(job_id:str, step_name:str, data, ttl:int = 3600):
    key = f"job:{job_id}:step:{step_name}"
    try:
        serialized_data = json.dumps(data)
        redis_client.set(key, serialized_data, ex=ttl)
        logger.info(f"[CACHE] SET {key}")
    except Exception as e:
        logger.error(f"Error occurred while setting step data: {str(e)}")

def get_step_data(job_id:str, step_name:str):
    key = f"job:{job_id}:step:{step_name}"
    data = redis_client.get(key)
    if not data:
        return None
    try:
        deserialized_data = json.loads(data)
        logger.info(f"[CACHE] GET {key}")
        return deserialized_data
    except Exception as e:
        logger.error(f"Error occurred while loading step data: {str(e)}")
        return None
    
def delete_step_data(job_id:str, step_name:str):
    key = f"job:{job_id}:step:{step_name}"
    try:
        redis_client.delete(key)
        logger.info(f"[CACHE] DELETE {key}")
    except Exception as e:
        logger.error(f"Error occurred while deleting step data: {str(e)}")
