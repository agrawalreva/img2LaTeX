import os
import tempfile
from typing import Tuple
from fastapi import HTTPException

# Simplified service for now - will be replaced with real ML in production
async def run_inference_service(image_path: str) -> Tuple[str, int, int]:
    """
    Simplified inference service that returns mock output.
    In production, this will call the real Unsloth model.
    """
    try:
        # Mock inference for now
        import time
        time.sleep(0.5)  # Simulate processing time
        
        # Return mock LaTeX output
        mock_latex = "E = mc^2"
        tokens_used = 12
        time_ms = 500
        
        return mock_latex, tokens_used, time_ms
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )
