from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.async_api.router import router as async_router
from api.sync_api.router import router as sync_router
from exceptions import ExceptionBase


# App Lifespan
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 100
    yield


# APP Configuration
app = FastAPI(
    title="FastAPI AsyncPG vs Psycopg2 Benchmark",
    version="1.0.0",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

# Middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["GET", "POST"],
    allow_credentials=False,
)


@app.exception_handler(ExceptionBase)
async def http_exception_handler(_request, exc: ExceptionBase) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.get("/")
async def root():
    return {
        "message": "FastAPI AsyncPG vs Psycopg2 Benchmark",
        "endpoints": {
            "async_api": "/async/",
            "sync_api": "/sync/",
            "benchmark_async": "/async/benchmark?count=100",
            "benchmark_sync": "/sync/benchmark?count=100",
        },
    }


# Include routers
app.include_router(async_router)
app.include_router(sync_router)
