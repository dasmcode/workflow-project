from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.core.database import get_db
from app.models.jobs import FileState, Job

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
                "created_at": str(job.created_at),
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


@router.post("/cancel-job/{job_id}")
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        if job.status in [FileState.completed, FileState.failed, FileState.cancelled]:
            return JSONResponse(
                content={
                    "error": f"Cannot cancel a job that is already {job.status.value}"
                },
                status_code=400,
            )
        job.status = FileState.cancel_requested
        db.commit()
        return JSONResponse(
            content={"message": f"Cancel request submitted for job with ID {job_id}"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.delete("/delete-job/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        db.delete(job)
        db.commit()
        return JSONResponse(
            content={"message": f"Job with ID {job_id} deleted successfully"},
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.delete("/delete-all-jobs/")
def delete_all_jobs(db: Session = Depends(get_db)):
    try:
        num_deleted = db.query(Job).delete()
        db.commit()
        return JSONResponse(
            content={
                "message": f"All jobs deleted successfully. Total deleted: {num_deleted}"
            },
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
