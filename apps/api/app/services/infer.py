import os
import tempfile
from typing import Tuple
from fastapi import HTTPException

from models.inference.unsloth_qwen import run_inference_with_cache
from ..core.config import settings


async def run_inference_service(image_path: str) -> Tuple[str, int, int]:
    """
    Service function to run inference on an uploaded image.
    
    Args:
        image_path: Path to the uploaded image
        
    Returns:
        Tuple of (latex_output, tokens_used, time_ms)
    """
    try:
        # Create cache directory
        cache_dir = os.path.join(tempfile.gettempdir(), "visionlatex_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Run inference with caching
        latex, tokens, time_ms = run_inference_with_cache(
            image_path=image_path,
            cache_dir=cache_dir,
            max_new_tokens=settings.max_new_tokens,
            temperature=settings.temperature,
            min_p=settings.min_p
        )
        
        return latex, tokens, time_ms
        
    except RuntimeError as e:
        if "CUDA not available" in str(e):
            raise HTTPException(
                status_code=503,
                detail="GPU required for local inference. Please ensure CUDA is available."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Inference failed: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during inference: {str(e)}"
        )
