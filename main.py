from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import IncludeAPIRouter
from app.core.database import init_db
from app.core.qdrant_client import create_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    init_db()
    create_collection()
    yield
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