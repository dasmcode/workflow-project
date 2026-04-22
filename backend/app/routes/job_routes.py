from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.database import get_db
from app.models.jobs import JobStatus, Job
from app.services.retrieval import stream_response
from app.models.request_payloads import JobPayload, QueryRequest, FilePayload
from app.services.job_state import transition_job
from app.services.delete_job_service import delete_jobs
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/job/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        return JSONResponse(
            content={
                "job_id": str(job.id),
                "file_id": str(job.file_id),
                "workflow_type": job.workflow_type,
                "status": job.status.value,
                "current_step": job.current_step,
                "step_index": job.step_index,
                "result": job.result,
                "created_at": str(job.created_at),
                "updated_at": str(job.updated_at),
                "cancelled_at": str(job.cancelled_at) if job.cancelled_at else None,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/get-jobs/")
def get_all_jobs(db: Session = Depends(get_db)):
    try:
        jobs = db.query(Job).all()
        job_list = [
            {
                "job_id": str(job.id),
                "file_id": str(job.file_id),
                "workflow_type": job.workflow_type,
                "status": job.status.value,
                "current_step": job.current_step,
                "result": job.result,
            }
            for job in jobs
        ]
        return JSONResponse(content={"jobs": job_list}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/cancel-job/")
def cancel_job(job_id: JobPayload, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id.job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        if job.status in [JobStatus.completed, JobStatus.failed, JobStatus.cancelled]:
            return JSONResponse(
                content={
                    "error": f"Cannot cancel a job that is already {job.status.value}"
                },
                status_code=400,
            )
        transition_job(job, JobStatus.cancel_requested)
        db.commit()
        return JSONResponse(
            content={"message": f"Cancel request submitted for job with ID {job_id}"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.delete("/delete-job/")
def delete_job(job_id: JobPayload, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id.job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        delete_jobs([job_id.job_id])
        return JSONResponse(
            content={"message": f"Job with ID {job_id.job_id} deleted successfully"},
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.delete("/delete-all-jobs/")
def delete_all_jobs(file_id: FilePayload, db: Session = Depends(get_db)):
    try:
        num_deleted = db.query(Job).filter(Job.file_id == file_id.file_id).all()
        job_ids = [str(job.id) for job in num_deleted]
        delete_jobs(job_ids)
        return JSONResponse(
            content={
                "message": f"All jobs deleted successfully. Total deleted: {len(num_deleted)}"
            },
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/query-job/")
def query_job(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)

        return StreamingResponse(
            stream_response(db, job, request.query), media_type="text/event-stream"
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
