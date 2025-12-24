import os
import sys
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException

# Add project root to path for model imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from models.inference.unsloth_qwen import run_inference


async def run_inference_service(image_path: str) -> Tuple[str, int, int]:
    """Run model inference on image to generate LaTeX."""
    try:
        latex_output, tokens_used, time_ms = run_inference(
            image_path,
            max_new_tokens=256,
            temperature=0.7,
            min_p=0.1
        )
        return latex_output, tokens_used, time_ms
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )
