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
            "id": "eulers_equation",
            "name": "Euler's Equation",
            "description": "Euler's famous equation",
            "url": "/static/samples/Eulers-equation.png",
            "expected_latex": "e^{i\\pi} + 1 = 0"
        },
        {
            "id": "equation2", 
            "name": "Mathematical Equation",
            "description": "Complex mathematical expression",
            "url": "/static/samples/equation2.jpeg",
            "expected_latex": "\\frac{d}{dx}[f(x)] = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}"
        },
        {
            "id": "long_equation",
            "name": "Long Equation",
            "description": "Extended mathematical formula",
            "url": "/static/samples/long_equation.jpg", 
            "expected_latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"
        }
    ]
    
    return {"sample_images": sample_images}
