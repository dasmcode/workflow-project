from app.models.jobs import Job, JobStatus
import logging

logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    JobStatus.pending: [
        JobStatus.processing,
        JobStatus.cancel_requested,
        JobStatus.failed,
    ],
    JobStatus.processing: [
        JobStatus.completed,
        JobStatus.failed,
        JobStatus.cancel_requested,
        JobStatus.retrying,
    ],
    JobStatus.retrying: [
        JobStatus.processing,
        JobStatus.failed,
        JobStatus.cancel_requested,
    ],
    JobStatus.cancel_requested: [JobStatus.cancelled],
}


def transition_job(job: Job, new_status: JobStatus):
    current = job.status

    if new_status not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(
            f"Invalid status transition from {current} to {new_status} for job ID {job.id}"
        )
    logger.info(
        f"Job status transition from {current} to {new_status}",
        extra={"job_id": str(job.id)},
    )
    job.status = new_status
