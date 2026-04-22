from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid, os
from datetime import datetime
from app.core.database import Base

FILES_TABLE = os.getenv("FILES_TABLE", "files")


def current_time():
    return datetime.now()


class Files(Base):
    __tablename__ = FILES_TABLE

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String)
    filepath = Column(String)
    created_at = Column(DateTime, default=current_time)
