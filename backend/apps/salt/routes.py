"""Salt management routes - imports from existing implementation"""
from fastapi import APIRouter

# Import existing routers from app structure
from app.api.v1 import (
    beacons,
    cloud,
    events,
    fileserver,
    grains,
    jobs,
    keys,
    mine,
    minions,
    orchestration,
    pillars,
    runners,
    schedules,
    ssh,
    states,
    templates,
)

# Create a combined router for all salt-related endpoints
router = APIRouter(prefix="/api/v1", tags=["salt"])

# Include all sub-routers
router.include_router(minions.router, tags=["minions"])
router.include_router(jobs.router, tags=["jobs"])
router.include_router(grains.router, tags=["grains"])
router.include_router(states.router, tags=["states"])
router.include_router(pillars.router, tags=["pillars"])
router.include_router(schedules.router, tags=["schedules"])
router.include_router(keys.router, tags=["keys"])
router.include_router(runners.router, tags=["runners"])
router.include_router(fileserver.router, tags=["fileserver"])
router.include_router(orchestration.router, tags=["orchestration"])
router.include_router(beacons.router, tags=["beacons"])
router.include_router(cloud.router, tags=["cloud"])
router.include_router(ssh.router, tags=["ssh"])
router.include_router(events.router, tags=["events"])
router.include_router(mine.router, tags=["mine"])
router.include_router(templates.router, prefix="/templates", tags=["templates"])


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Welcome to SaltShark API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}
