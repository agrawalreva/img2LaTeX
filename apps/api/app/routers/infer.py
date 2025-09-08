import os
import time
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.repository import InferenceRepository
from app.core.config import settings
from app.services.infer import run_inference_service

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
    
    # Run inference
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


@router.get("/sample-images")
async def get_sample_images() -> Dict[str, Any]:
    """Get list of sample images for testing."""
    sample_images = [
        {
            "id": "sample1",
            "name": "Gaussian Integral",
            "description": "Classic Gaussian integral formula",
            "url": "/api/sample-images/gaussian_integral.png",
            "expected_latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"
        },
        {
            "id": "sample2", 
            "name": "Quadratic Formula",
            "description": "Standard quadratic formula",
            "url": "/api/sample-images/quadratic_formula.png",
            "expected_latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
        },
        {
            "id": "sample3",
            "name": "Euler's Identity",
            "description": "Beautiful mathematical identity",
            "url": "/api/sample-images/eulers_identity.png", 
            "expected_latex": "e^{i\\pi} + 1 = 0"
        },
        {
            "id": "sample4",
            "name": "Pythagorean Theorem",
            "description": "Fundamental geometry theorem",
            "url": "/api/sample-images/pythagorean.png",
            "expected_latex": "a^2 + b^2 = c^2"
        }
    ]
    
    return {"sample_images": sample_images}
