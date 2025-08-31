from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.repository import PairRepository

router = APIRouter()


@router.post("/dataset/pairs")
async def create_pair(
    image_path: str,
    latex_text: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save an image-LaTeX pair to the dataset."""
    
    try:
        pair = PairRepository.create(
            db=db,
            image_path=image_path,
            latex_text=latex_text
        )
        
        return {
            "id": pair.id,
            "image_path": pair.image_path,
            "latex_text": pair.latex_text,
            "is_corrected": pair.is_corrected,
            "created_at": pair.created_at.isoformat() if pair.created_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save pair: {str(e)}")


@router.get("/dataset/pairs")
async def get_pairs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get paginated dataset pairs."""
    
    try:
        pairs = PairRepository.get_all(db, skip=skip, limit=limit)
        
        # Convert to response format
        pair_list = []
        for pair in pairs:
            pair_list.append({
                "id": pair.id,
                "image_path": pair.image_path,
                "latex_text": pair.latex_text,
                "is_corrected": pair.is_corrected,
                "created_at": pair.created_at.isoformat() if pair.created_at else None,
                "updated_at": pair.updated_at.isoformat() if pair.updated_at else None
            })
        
        return {
            "pairs": pair_list,
            "skip": skip,
            "limit": limit,
            "total": len(pair_list)  # In production, you'd get total count from DB
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pairs: {str(e)}")


@router.put("/dataset/pairs/{pair_id}")
async def update_pair(
    pair_id: int,
    latex_text: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update LaTeX text for a dataset pair."""
    
    try:
        pair = PairRepository.update(db, pair_id, latex_text)
        
        if not pair:
            raise HTTPException(status_code=404, detail="Pair not found")
        
        return {
            "id": pair.id,
            "image_path": pair.image_path,
            "latex_text": pair.latex_text,
            "is_corrected": pair.is_corrected,
            "updated_at": pair.updated_at.isoformat() if pair.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update pair: {str(e)}")
