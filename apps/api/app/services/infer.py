import os
import sys
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException

# Add project root to path for model imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from models.inference.unsloth_qwen import run_inference
from app.core.config import settings


async def run_inference_service(image_path: str) -> Tuple[str, int, int]:
    """Run model inference on image to generate LaTeX."""
    try:
        latex_output, tokens_used, time_ms = run_inference(
            image_path,
            max_new_tokens=settings.max_new_tokens,
            temperature=settings.temperature,
            min_p=settings.min_p
        )
        return latex_output, tokens_used, time_ms
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )
