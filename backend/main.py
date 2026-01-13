"""Main application entry point using faster-app framework pattern"""
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

    # Auto-discover and include routers from apps/*/routes.py
    from apps.auth.routes import router as auth_router
    from apps.salt.routes import router as salt_router
    from apps.audit.routes import router as audit_router

    # Include routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(salt_router)
    app.include_router(audit_router)

    return app


# Create app instance
app = create_app()

