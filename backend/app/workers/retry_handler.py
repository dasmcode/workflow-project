import time
import logging
from app.models.jobs import Job, JobStatus
from app.core.database import SessionLocal
from app.services.job_state import transition_job

logger = logging.getLogger(__name__)


def run_with_retry(step_func, job: Job, step_name):
    max_retries = job.max_retries or 3

    while job.retry_count < max_retries:
        try:
            db = SessionLocal()
            logger.info(f"Running step {step_name} (attempt {job.retry_count+1})",extra={"job_id": str(job.id), "step_name": step_name})
            result = step_func()
            if job.status == JobStatus.retrying:
                transition_job(job, JobStatus.processing)
                db.commit()
            return result

        except Exception as e:
            job.retry_count += 1
            if job.status != JobStatus.retrying:
                transition_job(job, JobStatus.retrying)
            job.error_message = str(e)

            db.commit()

            logger.error(f"Step {step_name} failed: {e}")

            if job.retry_count >= max_retries:
                logger.warning(f"Step {step_name} failed after {max_retries} attempts. Marking job as failed.",extra={"job_id": str(job.id), "step_name": step_name})
                transition_job(job, JobStatus.failed)
                db.commit()
                return

            time.sleep(2*job.retry_count)
        finally:
            db.close()
