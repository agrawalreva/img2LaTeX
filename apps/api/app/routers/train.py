import os
import json
import uuid
import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.base import get_db
from app.db.repository import TrainJobRepository, PairRepository
from app.core.config import settings

# Celery import will be done lazily when needed
worker_path = Path(__file__).parent.parent.parent.parent.parent / "apps" / "worker"
sys.path.insert(0, str(worker_path))

router = APIRouter()


class TrainingConfig(BaseModel):
    max_steps: int = 100
    learning_rate: float = 2e-4
    batch_size: int = 1
    gradient_accumulation_steps: int = 4


@router.post("/train")
async def start_training(
    config: TrainingConfig,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    pairs = PairRepository.get_all(db)
    if len(pairs) < 5:
        raise HTTPException(
            status_code=400,
            detail="Need at least 5 image-LaTeX pairs to start training"
        )
    
    job_id = str(uuid.uuid4())
    config_dict = config.dict()
    config_json = json.dumps(config_dict)
    
    job = TrainJobRepository.create(
        db=db,
        job_id=job_id,
        config=config_json
    )
    
    try:
        from apps.worker.tasks.train_lora import train_lora
        train_lora.delay(job_id, config_dict)
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Training worker not available. Celery not configured."
        )
    
    return {
        "job_id": job_id,
        "status": "QUEUED",
        "message": "Training job queued"
    }


@router.get("/train/{job_id}/status")
async def get_training_status(
    job_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    job = TrainJobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    try:
        config = json.loads(job.config)
    except:
        config = job.config
    
    logs = job.logs.split('\n') if job.logs else []
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "config": config,
        "logs": logs,
        "artifacts_path": job.artifacts_path,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }


@router.get("/train")
async def list_training_jobs(
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    from app.db.models import TrainJob
    jobs = db.query(TrainJob).order_by(TrainJob.created_at.desc()).all()
    return [
        {
            "job_id": job.job_id,
            "status": job.status,
            "config": json.loads(job.config) if job.config else {},
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        for job in jobs
    ]
