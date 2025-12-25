from sqlalchemy.orm import Session
from .models import InferenceRecord


class InferenceRepository:
    @staticmethod
    def create(db: Session, image_path: str, latex_output: str, tokens_used: int, time_ms: int) -> InferenceRecord:
        record = InferenceRecord(
            image_path=image_path,
            latex_output=latex_output,
            tokens_used=tokens_used,
            time_ms=time_ms
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> list[InferenceRecord]:
        return db.query(InferenceRecord).order_by(InferenceRecord.created_at.desc()).limit(limit).all()


