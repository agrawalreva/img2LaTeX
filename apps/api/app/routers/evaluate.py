import os
import difflib
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.infer import run_inference_service

router = APIRouter()


class EvaluationPair(BaseModel):
    image_path: str
    ground_truth: str


class EvaluationRequest(BaseModel):
    pairs: List[EvaluationPair]


def resolve_image_path(image_path: str) -> str:
    """Resolve image path from URL or relative path to absolute file path."""
    if image_path.startswith("/static/"):
        static_path = image_path.replace("/static/", "")
        file_path = os.path.join("static", static_path)
        if os.path.exists(file_path):
            return os.path.abspath(file_path)
    elif os.path.exists(image_path):
        return os.path.abspath(image_path)
    raise FileNotFoundError(f"Image not found: {image_path}")


@router.post("/evaluate")
async def evaluate_batch(request: EvaluationRequest) -> Dict[str, Any]:
    """Evaluate model on multiple image-LaTeX pairs."""
    if not request.pairs:
        raise HTTPException(status_code=400, detail="No pairs provided")
    
    results = []
    exact_matches = 0
    total_similarity = 0.0
    
    for pair in request.pairs:
        try:
            file_path = resolve_image_path(pair.image_path)
            predicted, tokens, time_ms = await run_inference_service(file_path)
            
            similarity = difflib.SequenceMatcher(
                None,
                pair.ground_truth.lower().strip(),
                predicted.lower().strip()
            ).ratio()
            
            is_exact = (pair.ground_truth.strip() == predicted.strip())
            if is_exact:
                exact_matches += 1
            
            total_similarity += similarity
            
            results.append({
                "image_path": pair.image_path,
                "ground_truth": pair.ground_truth,
                "predicted": predicted,
                "similarity": round(similarity, 4),
                "exact_match": is_exact,
                "tokens": tokens,
                "time_ms": time_ms
            })
        except Exception as e:
            results.append({
                "image_path": pair.image_path,
                "ground_truth": pair.ground_truth,
                "predicted": None,
                "error": str(e),
                "similarity": 0.0,
                "exact_match": False
            })
    
    accuracy = exact_matches / len(request.pairs) if request.pairs else 0.0
    avg_similarity = total_similarity / len(request.pairs) if request.pairs else 0.0
    
    return {
        "total": len(request.pairs),
        "exact_matches": exact_matches,
        "accuracy": round(accuracy, 4),
        "average_similarity": round(avg_similarity, 4),
        "results": results
    }
