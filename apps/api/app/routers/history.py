from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.repository import InferenceRepository

router = APIRouter()


@router.get("/history")
async def get_history(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent inference history with thumbnails."""
    
    records = InferenceRepository.get_recent(db, limit=limit)
    
    history_items = []
    for record in records:
        # Create thumbnail URL (in production, this would be a proper image service)
        thumbnail_url = f"/api/images/{record.id}/thumbnail"
        
        history_items.append({
            "id": record.id,
            "image_path": record.image_path,
            "thumbnail_url": thumbnail_url,
            "latex": record.latex_output,
            "tokens": record.tokens_used,
            "time_ms": record.time_ms,
            "created_at": record.created_at.isoformat() if record.created_at else None
        })
    
    return history_items
