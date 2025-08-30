import os
import time
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.repository import InferenceRepository
from ..core.config import settings

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
    
    # Mock inference (will be replaced with real model in Step 8)
    start_time = time.time()
    
    # Simulate processing time
    time.sleep(0.1)
    
    # Mock LaTeX output
    mock_latex = "E = mc^2"
    tokens_used = 12
    time_ms = int((time.time() - start_time) * 1000)
    
    # Save inference record
    record = InferenceRepository.create(
        db=db,
        image_path=file_path,
        latex_output=mock_latex,
        tokens_used=tokens_used,
        time_ms=time_ms
    )
    
    return {
        "latex": mock_latex,
        "tokens": tokens_used,
        "time_ms": time_ms,
        "id": record.id
    }
