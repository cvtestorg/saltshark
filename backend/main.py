"""Main application entry point - Compatible with faster-app framework"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Application lifespan handler"""
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure FastAPI application with faster-app pattern"""
    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Import routers - they already have prefixes and tags configured
    from apps.auth.routes import router as auth_router
    from apps.audit.routes import router as audit_router
    from apps.salt.routes import router as salt_router
    from apps.system.routes import router as system_router
    from apps.webhooks.routes import router as webhooks_router

    # Include routers (they already have prefixes and tags)
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(salt_router)  # Already has /api/v1 prefix and sub-tags
    app.include_router(audit_router)  # Already has /api/v1 prefix and sub-tags
    app.include_router(system_router, prefix="/api/v1", tags=["System"])
    app.include_router(webhooks_router, prefix="/api/v1", tags=["Webhooks"])

    return app


# Create app instance (required for uvicorn and faster server start)
app = create_app()
