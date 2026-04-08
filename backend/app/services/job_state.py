from app.models.jobs import Job, JobStatus

VALID_TRANSITIONS = {
    JobStatus.pending: [JobStatus.processing, JobStatus.cancel_requested],
    JobStatus.processing: [JobStatus.completed, JobStatus.failed, JobStatus.cancel_requested, JobStatus.retrying],
    JobStatus.retrying: [JobStatus.processing, JobStatus.failed, JobStatus.cancel_requested],
    JobStatus.cancel_requested: [JobStatus.cancelled],
}

def transition_job(job: Job, new_status: JobStatus):
    current = job.status
    
    if new_status not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid status transition from {current} to {new_status} for job ID {job.id}")
    job.status = new_status