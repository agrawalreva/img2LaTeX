from sqlalchemy import Column, Integer, String, DateTime, Text
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

