from sqlalchemy import Column, String, DateTime,Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base
from enum import Enum

def current_time():
    return datetime.now()

class FileState(Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancel_requested = "cancel_requested"
    cancelled = "cancelled"

class Job(Base):
    __tablename__ = "jobs_new"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(String)
    workflow_type = Column(String)
    status = Column(SQLEnum(FileState,name="file_state",native_enum=True),default=FileState.pending)
    current_step = Column(String, nullable=True)
    result = Column(String, nullable=True)
    created_at = Column(DateTime, default=current_time)
    updated_at = Column(DateTime, default=current_time)
    cancelled_at = Column(DateTime, nullable=True)