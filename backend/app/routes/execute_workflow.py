from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.core.database import get_db
from app.models.jobs import Job
from app.models.files import Files
from app.models.request_payloads import WorkflowExecutionRequest
from app.utils.file_handler import save_file
from app.core.queue import queue
from app.workers.tasks import process_step
router = APIRouter()

@router.post("/execute/")
def execute_workflow(request: WorkflowExecutionRequest, db:Session = Depends(get_db)):
    try:
        file = db.query(Files).filter(Files.id == request.file_id).first()
        if not file:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        job = Job(file_id=request.file_id, workflow_type=request.workflow_type)
        db.add(job)
        db.commit()
        db.refresh(job)
        queue.enqueue(process_step, str(job.id))
        return JSONResponse(content={"message": f"Workflow {request.workflow_type} executed successfully with job ID {job.id}"}, status_code=200)
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
