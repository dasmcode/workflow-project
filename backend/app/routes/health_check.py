from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health")

@router.get("/")
async def health_check():
    logger.info("Health check")
    return JSONResponse(content={"status": "ok"},status_code=200)