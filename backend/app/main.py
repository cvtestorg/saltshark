"""Main FastAPI application for SaltShark"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    audit,
    auth,
    beacons,
    cloud,
    compliance,
    events,
    fileserver,
    grains,
    jobs,
    keys,
    mine,
    minions,
    notifications,
    orchestration,
    pillars,
    runners,
    schedules,
    ssh,
    states,
    templates,
)
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(minions.router, prefix="/api/v1", tags=["minions"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(grains.router, prefix="/api/v1", tags=["grains"])
app.include_router(states.router, prefix="/api/v1", tags=["states"])
app.include_router(pillars.router, prefix="/api/v1", tags=["pillars"])
app.include_router(schedules.router, prefix="/api/v1", tags=["schedules"])
app.include_router(keys.router, prefix="/api/v1", tags=["keys"])
app.include_router(runners.router, prefix="/api/v1", tags=["runners"])
app.include_router(fileserver.router, prefix="/api/v1", tags=["fileserver"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["orchestration"])
app.include_router(beacons.router, prefix="/api/v1", tags=["beacons"])
app.include_router(cloud.router, prefix="/api/v1", tags=["cloud"])
app.include_router(ssh.router, prefix="/api/v1", tags=["ssh"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(mine.router, prefix="/api/v1", tags=["mine"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Welcome to SaltShark API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}
