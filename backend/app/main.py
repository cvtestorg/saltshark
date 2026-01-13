"""Main FastAPI application for SaltShark"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import minions, jobs, grains
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="SaltShark API",
    description="Web UI API for SaltStack/SaltProject",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(minions.router, prefix="/api/v1", tags=["minions"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(grains.router, prefix="/api/v1", tags=["grains"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SaltShark API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
