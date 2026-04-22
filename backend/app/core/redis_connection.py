import redis, os

REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
redis_client = redis.Redis(host=REDIS_SERVER, port=6379, db=0)
