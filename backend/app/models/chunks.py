from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid, os
from app.core.database import Base

CHUNKS_TABLE = os.getenv("CHUNKS_TABLE", "chunks")


class Chunks(Base):
    __tablename__ = CHUNKS_TABLE

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    job_id = Column(String, nullable=False, index=True)
