from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import IncludeAPIRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    print("Starting up the application...")
    yield
    # Perform any shutdown tasks here
    print("Shutting down the application...")
    
def init_application():
    _app = FastAPI(
        title="Workflow API",
        description="API for managing workflows",
        version="1.0.0",
        lifespan=lifespan
    )
    _app.include_router(IncludeAPIRouter())
    return _app

app = init_application()