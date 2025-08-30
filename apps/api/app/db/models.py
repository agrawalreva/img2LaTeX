from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func

from .base import Base


class InferenceRecord(Base):
    __tablename__ = "inference_records"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    latex_output = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Pair(Base):
    __tablename__ = "pairs"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    latex_text = Column(Text, nullable=False)
    is_corrected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrainJob(Base):
    __tablename__ = "train_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False, default="QUEUED")  # QUEUED, RUNNING, DONE, FAILED
    config = Column(Text, nullable=False)  # JSON string
    logs = Column(Text, nullable=True)
    artifacts_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())