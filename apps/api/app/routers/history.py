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
    records = InferenceRepository.get_recent(db, limit=limit)
    
    history_items = []
    import os
    for record in records:
        filename = os.path.basename(record.image_path)
        image_url = f"/api/uploads/{filename}"
        
        history_items.append({
            "id": record.id,
            "image_path": image_url,
            "thumbnail_url": image_url,
            "latex": record.latex_output,
            "tokens": record.tokens_used,
            "time_ms": record.time_ms,
            "created_at": record.created_at.isoformat() if record.created_at else None
        })
    
    return history_items
