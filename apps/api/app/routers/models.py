from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.inference.model_manager import model_manager

router = APIRouter()


class ModelSwitchRequest(BaseModel):
    adapter_path: str


class GenerationSettings(BaseModel):
    max_new_tokens: int = 256
    temperature: float = 0.7
    min_p: float = 0.1


@router.get("/models/current")
async def get_current_model() -> Dict[str, Any]:
    """Get information about the currently loaded model."""
    try:
        return model_manager.get_current_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.get("/models/adapters")
async def get_available_adapters() -> List[Dict[str, Any]]:
    """Get list of available fine-tuned adapters."""
    try:
        adapters = model_manager.get_available_adapters()
        return adapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adapters: {str(e)}")


@router.post("/models/switch")
async def switch_model(request: ModelSwitchRequest) -> Dict[str, Any]:
    """Switch to a specific adapter or back to base model."""
    try:
        if request.adapter_path == "base":
            success = model_manager.switch_to_base()
        else:
            success = model_manager.load_adapter(request.adapter_path)
        
        if success:
            return {
                "success": True,
                "message": f"Switched to {'base model' if request.adapter_path == 'base' else 'adapter'}",
                "model_info": model_manager.get_current_model_info()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to switch model")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}")


@router.get("/models/settings")
async def get_generation_settings() -> GenerationSettings:
    """Get current generation settings."""
    try:
        # In a real implementation, these would be stored in database/user preferences
        return GenerationSettings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.put("/models/settings")
async def update_generation_settings(settings: GenerationSettings) -> GenerationSettings:
    """Update generation settings."""
    try:
        # In a real implementation, these would be saved to database/user preferences
        # For now, just validate and return
        if settings.max_new_tokens < 1 or settings.max_new_tokens > 1024:
            raise HTTPException(status_code=400, detail="max_new_tokens must be between 1 and 1024")
        
        if settings.temperature < 0.0 or settings.temperature > 2.0:
            raise HTTPException(status_code=400, detail="temperature must be between 0.0 and 2.0")
        
        if settings.min_p < 0.0 or settings.min_p > 1.0:
            raise HTTPException(status_code=400, detail="min_p must be between 0.0 and 1.0")
        
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
