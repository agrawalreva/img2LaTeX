import difflib
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.infer import run_inference_service

router = APIRouter()


class EvaluationPair(BaseModel):
    image_path: str
    ground_truth: str


class BatchEvaluationRequest(BaseModel):
    pairs: List[EvaluationPair]


@router.post("/evaluate/batch")
async def evaluate_batch(request: BatchEvaluationRequest) -> Dict[str, Any]:
    """Evaluate model on multiple image-LaTeX pairs."""
    if not request.pairs:
        raise HTTPException(status_code=400, detail="No pairs provided")
    
    results = []
    exact_matches = 0
    
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
                "error": str(e)
            })
    
    total = len(request.pairs)
    accuracy = exact_matches / total if total > 0 else 0.0
    valid_results = [r for r in results if "similarity" in r]
    avg_similarity = (
        sum(r["similarity"] for r in valid_results) / len(valid_results)
        if valid_results else 0.0
    )
    
    return {
        "total": total,
        "exact_matches": exact_matches,
        "accuracy": round(accuracy, 4),
        "average_similarity": round(avg_similarity, 4),
        "results": results
    }


@router.post("/evaluate/single")
async def evaluate_single(pair: EvaluationPair) -> Dict[str, Any]:
    """Evaluate model on a single image-LaTeX pair."""
    try:
        predicted, tokens, time_ms = await run_inference_service(pair.image_path)
        
        similarity = difflib.SequenceMatcher(
            None,
            pair.ground_truth.lower().strip(),
            predicted.lower().strip()
        ).ratio()
        
        is_exact = (pair.ground_truth.strip() == predicted.strip())
        
        return {
            "image_path": pair.image_path,
            "ground_truth": pair.ground_truth,
            "predicted": predicted,
            "similarity": round(similarity, 4),
            "exact_match": is_exact,
            "tokens": tokens,
            "time_ms": time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

