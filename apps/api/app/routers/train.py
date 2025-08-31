import uuid
import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.repository import TrainJobRepository
from ..core.config import settings

# Import Celery task
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../apps/worker'))
from tasks.train_lora import train_lora

router = APIRouter()


@router.post("/train")
async def start_training(
    config: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Start a new LoRA training job."""
    
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Validate config
        required_fields = ["max_steps", "learning_rate", "batch_size"]
        for field in required_fields:
            if field not in config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate max_steps (safety limit)
        max_steps = config.get("max_steps", 30)
        if max_steps > 200:
            raise HTTPException(status_code=400, detail="max_steps cannot exceed 200")
        
        # Create job record
        job = TrainJobRepository.create(
            db=db,
            job_id=job_id,
            config=json.dumps(config)
        )
        
        # Start Celery task
        task = train_lora.delay(job_id, config)
        
        return {
            "job_id": job_id,
            "task_id": task.id,
            "status": "QUEUED",
            "message": "Training job started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


@router.get("/train/{job_id}/status")
async def get_training_status(
    job_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get training job status and logs."""
    
    try:
        job = TrainJobRepository.get_by_id(db, job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "logs": job.logs,
            "artifacts_path": job.artifacts_path,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/train")
async def list_training_jobs(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List all training jobs."""
    
    try:
        # In a real implementation, you'd add pagination
        # For now, just return recent jobs
        jobs = db.query(TrainJob).order_by(TrainJob.created_at.desc()).limit(10).all()
        
        job_list = []
        for job in jobs:
            job_list.append({
                "job_id": job.job_id,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None
            })
        
        return {
            "jobs": job_list,
            "total": len(job_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")
