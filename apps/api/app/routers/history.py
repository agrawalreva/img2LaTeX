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
        # Convert absolute path to relative URL for serving
        image_url = record.image_path
        if image_url.startswith('/'):
            # Already absolute path
            pass
        elif 'uploads' in image_url:
            # Extract relative path
            if 'uploads/' in image_url:
                image_url = '/api/' + image_url.split('uploads/')[-1] if 'uploads/' in image_url else image_url
            else:
                image_url = '/api/uploads/' + image_url.split('/')[-1]
        else:
            image_url = '/api/uploads/' + image_url.split('/')[-1]
        
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
