"""Audit and compliance routes"""
from fastapi import APIRouter

# Import existing routers
from api.v1 import audit, compliance, notifications

# Create combined router
router = APIRouter(prefix="/api/v1")

# Include audit, compliance, and notifications
router.include_router(audit.router, prefix="/audit", tags=["audit"])
router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
