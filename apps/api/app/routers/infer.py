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
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "../../static/samples")
    
    # Map of filenames to metadata
    image_metadata = {
        "Eulers-equation.png": {
            "id": "eulers_equation",
            "name": "Euler's Equation",
            "description": "Euler's famous identity",
            "expected_latex": "e^{i\\pi} + 1 = 0"
        },
        "eulers_identity.png": {
            "id": "eulers_identity",
            "name": "Euler's Identity",
            "description": "Euler's identity equation",
            "expected_latex": "e^{i\\pi} + 1 = 0"
        },
        "equation2.jpeg": {
            "id": "equation2",
            "name": "Linear Equation",
            "description": "Simple linear equation",
            "expected_latex": "2x - 3 = -7"
        },
        "long_equation.jpg": {
            "id": "long_equation",
            "name": "Gaussian Integral",
            "description": "Gaussian integral formula",
            "expected_latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"
        },
        "gaussian_integral.png": {
            "id": "gaussian_integral",
            "name": "Gaussian Integral",
            "description": "Gaussian integral",
            "expected_latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"
        },
        "pythagorean_theorem.png": {
            "id": "pythagorean",
            "name": "Pythagorean Theorem",
            "description": "Pythagorean theorem",
            "expected_latex": "a^2 + b^2 = c^2"
        },
        "quadratic_formula.png": {
            "id": "quadratic",
            "name": "Quadratic Formula",
            "description": "Quadratic formula",
            "expected_latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
        }
    }
    
    sample_images = []
    
    # Images to exclude
    exclude_images = {
        "Eulers-equation.png",
        "eulers_identity.png",
        "gaussian_integral.png"
    }
    
    if os.path.exists(static_dir):
        for filename in os.listdir(static_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and filename not in exclude_images:
                metadata = image_metadata.get(filename, {
                    "id": filename.replace('.', '_').replace(' ', '_').lower(),
                    "name": filename.replace('_', ' ').replace('.png', '').replace('.jpg', '').replace('.jpeg', '').title(),
                    "description": "Mathematical equation",
                    "expected_latex": ""
                })
                
                sample_images.append({
                    "id": metadata["id"],
                    "name": metadata["name"],
                    "description": metadata["description"],
                    "url": f"/static/samples/{filename}",
                    "expected_latex": metadata["expected_latex"]
                })
    
    return {"sample_images": sample_images}
