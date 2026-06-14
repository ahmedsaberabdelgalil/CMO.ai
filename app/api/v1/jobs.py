"""Generic job status endpoint for background (async) agent work."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user_async
from app.models.user import User
from app.services.jobs import job_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user_async),
):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or expired")
    if job.owner_id is not None and job.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this job")
    return job.to_dict()
