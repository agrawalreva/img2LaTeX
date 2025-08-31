import os
import time
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.repository import InferenceRepository
from ..core.config import settings
from ..services.infer import run_inference_service

router = APIRouter()


@router.post("/infer")
async def infer(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded image
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"{timestamp}_{image.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await image.read()
        buffer.write(content)
    
    # Run real inference
    try:
        latex_output, tokens_used, time_ms = await run_inference_service(file_path)
    except HTTPException:
        # Clean up uploaded file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    
    # Save inference record
    record = InferenceRepository.create(
        db=db,
        image_path=file_path,
        latex_output=latex_output,
        tokens_used=tokens_used,
        time_ms=time_ms
    )
    
    return {
        "latex": latex_output,
        "tokens": tokens_used,
        "time_ms": time_ms,
        "id": record.id
    }
