import time
from app.core.database import SessionLocal
from app.core.queue import queue
from app.models.jobs import Job, FileState

def process_job(job_id:str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"Job with ID {job_id} not found")
            return
        job.status = FileState.processing
        job.current_step = "started"
        db.commit()
        # Simulate processing steps
        steps = ["Step 1: Validating file", "Step 2: Processing data", "Step 3: Finalizing"]
        for step in steps:
            job.current_step = step
            db.commit()
            time.sleep(5)  # Simulate time taken for each step
        job.status = FileState.completed
        job.current_step = "completed"
        db.commit()
    except Exception as e:
        if job:
            job.status = FileState.failed
            job.current_step = "failed"
            db.commit()
        print(f"Error processing job {job_id}: {str(e)}")
    finally:
        db.close()