from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
from prometheus_client import (
    CollectorRegistry,
    multiprocess,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    PROM_DIR = os.getenv("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus")
    os.makedirs(PROM_DIR, exist_ok=True)
    for filename in os.listdir(PROM_DIR):
        file_path = os.path.join(PROM_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception:
            pass

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    return Response(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )
