"""Jobs API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from schemas.job import JobExecuteRequest, JobList, JobResult, JobStatus
from services.salt_api import salt_client

router = APIRouter()


@router.get("/jobs", response_model=JobList)
async def list_jobs() -> JobList:
    """List all jobs"""
    try:
        response = await salt_client.list_jobs()
        jobs_data = response.get("return", [{}])[0]

        jobs = [
            JobStatus(
                jid=jid,
                function=data.get("function", ""),
                minions=data.get("minions", []),
                start_time=data.get("start_time"),
                status=data.get("status", "unknown"),
            )
            for jid, data in jobs_data.items()
        ]

        return JobList(jobs=jobs, total=len(jobs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{jid}", response_model=JobResult)
async def get_job(jid: str) -> JobResult:
    """Get job details and results"""
    try:
        response = await salt_client.get_job(jid)
        job_data = response.get("return", [{}])[0]

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobResult(
            jid=jid,
            function=job_data.get("function", ""),
            minions=job_data.get("minions", []),
            start_time=job_data.get("start_time"),
            end_time=job_data.get("end_time"),
            status=job_data.get("status", "unknown"),
            result=job_data.get("result"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/execute")
async def execute_job(job_request: JobExecuteRequest) -> dict[str, Any]:
    """Execute a Salt job on target minions"""
    try:
        response = await salt_client.execute_command(
            target=job_request.target,
            function=job_request.function,
            args=job_request.args if job_request.args else None,
        )

        return {
            "success": True,
            "message": "Job submitted successfully",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
