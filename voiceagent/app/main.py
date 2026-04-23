# voiceagent/app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calls, health
from app.config import settings

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Voice Agent — environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down Voice Agent")


app = FastAPI(
    title="AI Voice Agent",
    description="Azure Communication Services AI Voice Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(calls.router)


@app.get("/")
async def root():
    return {
        "service": "AI Voice Agent",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }