import logging
from app.core.database import SessionLocal
from app.models.jobs import Job
logger = logging.getLogger(__name__)
from app.services.embedding_steps import delete_existing_vectors

def delete_jobs(job_ids:list[str]):
    db = SessionLocal()
    try:
        for job_id in job_ids:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                logger.info(f"Deleting job with ID: {job_id}",extra={"job_id": job_id})
                delete_existing_vectors(str(job.id))
                db.delete(job)
        db.commit()
        logger.info(f"Deleted jobs with IDs: {', '.join(job_ids)}",extra={"job_id": job_id})
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting jobs: {str(e)}",extra={"job_id": job_id})
    finally:
        db.close()