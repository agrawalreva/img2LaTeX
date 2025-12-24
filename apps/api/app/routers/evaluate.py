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
            predicted, tokens, time_ms = await run_inference_service(pair.image_path)
            
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
