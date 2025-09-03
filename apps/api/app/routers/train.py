import os
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.base import get_db
from app.db.repository import TrainJobRepository, PairRepository
from app.core.config import settings

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
    # Check if we have enough data
    pairs = PairRepository.get_all(db)
    if len(pairs) < 5:
        raise HTTPException(
            status_code=400,
            detail="Need at least 5 image-LaTeX pairs to start training"
        )
    
    # For now, just create a mock training job
    # In production, this would enqueue a Celery task
    job = TrainJobRepository.create(
        db=db,
        config=config.dict(),
        status="pending"
    )
    
    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Training job created (mock - Celery integration pending)"
    }


@router.get("/train/{job_id}/status")
async def get_training_status(
    job_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    job = TrainJobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "config": job.config,
        "logs": job.logs or [],
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }


@router.get("/train")
async def list_training_jobs(
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    jobs = TrainJobRepository.get_all(db)
    return [
        {
            "job_id": job.id,
            "status": job.status,
            "config": job.config,
            "created_at": job.created_at
        }
        for job in jobs
    ]
