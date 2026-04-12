from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import IncludeAPIRouter
from app.core.database import init_db
from app.core.qdrant_client import create_collection
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging
from graphql_app.controller import graphql_router

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    setup_logging()
    init_db()
    create_collection()
    yield
    print("Shutting down the application...")


def init_application():
    _app = FastAPI(
        title="Workflow API",
        description="API for managing workflows",
        version="1.0.0",
        lifespan=lifespan,
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(IncludeAPIRouter())
    _app.include_router(graphql_router, tags=["GraphQL"])
    return _app


app = init_application()
