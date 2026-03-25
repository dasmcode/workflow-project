from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

router = APIRouter(prefix="/health")

@router.get("/")
async def health_check():
    print("Health check")
    return JSONResponse(content={"status": "ok"},status_code=200)