"""Test configuration"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from apps.salt.salt_api_client import salt_client
from config.settings import settings


# Create test app
def create_test_app() -> FastAPI:
    """Create FastAPI app for testing"""
    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Import and include routers
    from apps.auth.routes import router as auth_router
    from apps.audit.routes import router as audit_router
    from apps.salt.routes import router as salt_router
    from apps.system.routes import router as system_router
    from apps.webhooks.routes import router as webhooks_router
    
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(salt_router)
    app.include_router(audit_router)
    app.include_router(system_router, prefix="/api/v1", tags=["System"])
    app.include_router(webhooks_router, prefix="/api/v1", tags=["Webhooks"])
    
    # Root endpoints
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to SaltShark API",
            "version": settings.version,
            "docs": "/docs",
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


app = create_test_app()


@pytest.fixture(autouse=True)
def reset_salt_client():
    """Reset the Salt API client before each test"""
    # Reset token to force re-login
    salt_client.token = None
    yield
    # Clean up after test
    salt_client.token = None


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def api_base_url():
    """API base URL"""
    return "/api/v1"
