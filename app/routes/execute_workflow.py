from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.core.database import get_db
from app.models.jobs import Job,FileState
from app.models.request_payloads import WorkflowExecutionRequest
from app.utils.file_handler import save_file
router = APIRouter()

@router.post("/execute/")
def execute_workflow(request: WorkflowExecutionRequest, db:Session = Depends(get_db)):
    try:
        job = Job(file_id=request.file_id, workflow_type=request.workflow_type)
        db.add(job)
        db.commit()
        return JSONResponse(content={"message": f"Workflow {request.workflow_type} executed successfully with file ID {request.file_id}"}, status_code=200)
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.get("/status/{job_id}")
def get_job_status(job_id:str, db:Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        return JSONResponse(content={"job_id": str(job.id), "status": job.status.value, "current_step": job.current_step}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)