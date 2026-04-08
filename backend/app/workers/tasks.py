from app.core.workflows import WORKFLOWS
from app.services.cancel_service import check_cancel
from app.core.database import SessionLocal
from app.models.jobs import Job, JobStatus
from app.services.steps import execute_step
from app.core.queue import queue
from app.services.job_state import transition_job
import logging

logger = logging.getLogger(__name__)


def process_step(job_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        logger.info(f"Processing job with ID {job_id}, current status: {job.status}")
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            raise Exception("Job not found")
        if check_cancel(db, job):
            logger.info(f"Job with ID {job_id} has been cancelled")
            return
        workflow = WORKFLOWS.get(job.workflow_type)

        if not workflow:
            logger.error(
                f"Workflow type {job.workflow_type} not found for job ID {job_id}"
            )
            transition_job(job, JobStatus.failed)
            db.commit()
            return
        step_index = job.step_index
        current_step = workflow[step_index]
        if job.status == JobStatus.pending:
            transition_job(job, JobStatus.processing)
        job.current_step = current_step
        db.commit()
        db.refresh(job)

        execute_step(current_step, job)

        if check_cancel(db, job):
            logger.info(f"Job with ID {job_id} has been cancelled after step execution")
            return

        job.step_index += 1
        db.commit()
        db.refresh(job)

        if job.step_index < len(workflow):
            queue.enqueue(process_step, str(job.id))
        else:
            if check_cancel(db, job):
                logger.info(f"Job with ID {job_id} has been cancelled before completion")
                return
            transition_job(job, JobStatus.completed)
            db.commit()
            logger.info(f"Job with ID {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Error processing job with ID {job_id}: {str(e)}")
        transition_job(job, JobStatus.failed)
        db.commit()
    finally:
        db.close()
