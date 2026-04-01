from app.models.jobs import Job, FileState
import datetime

def check_cancel(db, job:Job):
    job = db.query(Job).filter(Job.id == job.id).first()
    if job.status == FileState.cancel_requested:
        job.status = FileState.cancelled
        job.cancelled_at = datetime.datetime.now()
        db.commit()
        return True
    return False