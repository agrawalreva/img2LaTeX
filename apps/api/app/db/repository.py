from sqlalchemy.orm import Session
from .models import InferenceRecord, Pair, TrainJob


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


class PairRepository:
    @staticmethod
    def create(db: Session, image_path: str, latex_text: str) -> Pair:
        pair = Pair(image_path=image_path, latex_text=latex_text)
        db.add(pair)
        db.commit()
        db.refresh(pair)
        return pair

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Pair]:
        return db.query(Pair).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, pair_id: int, latex_text: str) -> Pair:
        pair = db.query(Pair).filter(Pair.id == pair_id).first()
        if pair:
            pair.latex_text = latex_text
            pair.is_corrected = True
            db.commit()
            db.refresh(pair)
        return pair


class TrainJobRepository:
    @staticmethod
    def create(db: Session, job_id: str, config: str) -> TrainJob:
        job = TrainJob(job_id=job_id, config=config)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_by_id(db: Session, job_id: str) -> TrainJob:
        return db.query(TrainJob).filter(TrainJob.job_id == job_id).first()

    @staticmethod
    def update_status(db: Session, job_id: str, status: str, logs: str = None, artifacts_path: str = None) -> TrainJob:
        job = db.query(TrainJob).filter(TrainJob.job_id == job_id).first()
        if job:
            job.status = status
            if logs:
                job.logs = logs
            if artifacts_path:
                job.artifacts_path = artifacts_path
            db.commit()
            db.refresh(job)
        return job
