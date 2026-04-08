from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base
from enum import Enum


def current_time():
    return datetime.now()


class JobStatus(Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    retrying = "retrying"
    cancel_requested = "cancel_requested"
    cancelled = "cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(String)
    workflow_type = Column(String)
    status = Column(
        SQLEnum(JobStatus, name="job_status", native_enum=True),
        default=JobStatus.pending,
    )
    current_step = Column(String, nullable=True)
    step_index = Column(Integer, default=0)
    result = Column(String, nullable=True)
    created_at = Column(DateTime, default=current_time)
    updated_at = Column(DateTime, default=current_time)
    cancelled_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(String, nullable=True)
