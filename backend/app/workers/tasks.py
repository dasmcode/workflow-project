from app.core.workflows import WORKFLOWS
from app.services.cancel_service import check_cancel
from app.core.database import SessionLocal
from app.models.jobs import Job, FileState
from app.services.steps import execute_step
from app.core.queue import queue

def process_step(job_id:str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"Job with ID {job_id} not found")
            return
        if check_cancel(db, job):
            print(f"Job with ID {job_id} has been cancelled")
            return
        workflow = WORKFLOWS.get(job.workflow_type)
        
        if not workflow:
            print(f"Workflow type {job.workflow_type} not found for job ID {job_id}")
            job.status = FileState.failed
            db.commit()
            return
        step_index = job.step_index
        current_step = workflow[step_index]
        
        job.status = FileState.processing
        job.current_step = current_step
        db.commit()
        db.refresh(job)
        
        execute_step(current_step, job)
        
        if check_cancel(db, job):
            print(f"Job with ID {job_id} has been cancelled after step execution")
            return
        
        job.step_index +=1
        db.commit()
        db.refresh(job)
        
        if job.step_index < len(workflow):
            queue.enqueue(process_step, str(job.id))
        else:
            job.status = FileState.completed
            db.commit()
            print(f"Job with ID {job_id} completed successfully")
    except Exception as e:
        print(f"Error processing job with ID {job_id}: {str(e)}")
        job.status = FileState.failed
        db.commit()
    finally:
        db.close()
        