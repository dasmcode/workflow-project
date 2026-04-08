from app.models.jobs import Job, JobStatus
import datetime
from app.services.job_state import transition_job


def check_cancel(db, job: Job):
    job = db.query(Job).filter(Job.id == job.id).first()
    if job.status == JobStatus.cancel_requested:
        transition_job(job, JobStatus.cancelled)
        job.cancelled_at = datetime.datetime.now()
        db.commit()
        return True
    if job.status == JobStatus.cancelled:
        return True
    return False
