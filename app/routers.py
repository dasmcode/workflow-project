class IncludeAPIRouter(object):
    def __new__(cls):
        api_prefix = "/api/v1"
        print("Inside IncludeAPIRouter")
        from app.routes.health_check import router as health_check_router
        from app.routes.upload_file import router as upload_file_router
        from fastapi.routing import APIRouter
        
        router = APIRouter(prefix=api_prefix)
        router.include_router(health_check_router, tags=["Health Check"])
        router.include_router(upload_file_router, tags=["File Upload"])
        return router
        