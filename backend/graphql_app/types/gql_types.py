import strawberry
from uuid import UUID
from enum import Enum
from typing import List, Optional

from app.models.jobs import Job
from app.models.files import Files

@strawberry.enum
class JobStatusGQL(Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    retrying = "retrying"
    cancel_requested = "cancel_requested"
    cancelled = "cancelled"

@strawberry.type
class JobType:
    id: UUID
    file_id: str
    workflow_type: str
    status: JobStatusGQL
    current_step: Optional[str]
    step_index: int
    result: Optional[str]
    created_at: str
    updated_at: str
    cancelled_at: Optional[str]
    retry_count: int
    max_retries: int
    error_message: Optional[str]
    
    @strawberry.field
    def files(self, info: strawberry.Info) -> Optional['FileType']:
        db = info.context.db
        file = db.query(Files).filter(Files.id == self.file_id).first()
        if file:
            return return_file(file)
        return None

@strawberry.type
class FileType:
    id: UUID
    filename: str
    filepath: str
    created_at: str

    @strawberry.field
    def jobs(self, info: strawberry.Info) -> List[JobType]:
        db = info.context.db
        jobs = db.query(Job).filter(Job.file_id == str(self.id)).all()
        if not jobs:
            return []
        return [return_job(job) for job in jobs]


def return_job(job: Job) -> JobType:
    return JobType(
        id=job.id,
        file_id=job.file_id,
        workflow_type=job.workflow_type,
        status=JobStatusGQL(job.status.value),
        current_step=job.current_step,
        step_index=job.step_index,
        result=job.result,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        cancelled_at=job.cancelled_at.isoformat() if job.cancelled_at else None,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        error_message=job.error_message,
    )


def return_file(file: Files) -> FileType:
    return FileType(
        id=file.id,
        filename=file.filename,
        filepath=file.filepath,
        created_at=file.created_at.isoformat(),
    )
