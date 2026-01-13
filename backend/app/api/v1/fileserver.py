"""File Server API endpoints"""
from fastapi import APIRouter, HTTPException

from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/fileserver/files")
async def list_files(environment: str = "base"):
    """List files in file server"""
    try:
        response = await salt_client.list_files(environment)
        return {
            "success": True,
            "environment": environment,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fileserver/roots")
async def list_file_roots():
    """List file server roots"""
    try:
        response = await salt_client.list_file_roots()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fileserver/file")
async def get_file_content(path: str):
    """Get content of a file from file server"""
    try:
        response = await salt_client.get_file_content(path)
        return {
            "success": True,
            "path": path,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
