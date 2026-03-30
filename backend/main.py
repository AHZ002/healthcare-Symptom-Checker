from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from backend.database.db import create_tables
from backend.routes.symptom import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan: runs on startup and shutdown

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating database tables...")
    create_tables()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


# App Instance

app = FastAPI(
    title="Healthcare Symptom Checker",
    description=(
        "An AI-powered educational tool that analyzes symptoms and suggests "
        "possible conditions. This tool is for educational purposes only and "
        "does not provide medical advice."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# CORS Middleware
# Allows the HTML frontend (opened as a file) to call the API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Routes

app.include_router(router)


# Health Check

@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(content={"status": "ok", "service": "Healthcare Symptom Checker"})


@app.get("/", tags=["Root"])
async def root():
    return JSONResponse(content={
        "service": "Healthcare Symptom Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    })
