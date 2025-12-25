import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.config import settings

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

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
    return model_manager.get_current_model_info()


@router.get("/models/adapters")
async def get_available_adapters() -> List[Dict[str, Any]]:
    adapters = model_manager.get_available_adapters()
    return [
        {
            "job_id": a["job_id"],
            "path": a["path"],
            "config": a["config"],
            "name": os.path.basename(a["path"])
        }
        for a in adapters
    ]


@router.post("/models/switch")
async def switch_model(request: ModelSwitchRequest) -> Dict[str, Any]:
    if request.adapter_path == "base":
        success = model_manager.switch_to_base()
    else:
        success = model_manager.load_adapter(request.adapter_path)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to switch model")
    
    return {
        "message": "Model switched successfully",
        "current_model": model_manager.get_current_model_info()
    }


@router.get("/models/settings")
async def get_generation_settings() -> GenerationSettings:
    return GenerationSettings(
        max_new_tokens=settings.max_new_tokens,
        temperature=settings.temperature,
        min_p=settings.min_p
    )


@router.put("/models/settings")
async def update_generation_settings(
    settings_update: GenerationSettings
) -> GenerationSettings:
    settings.max_new_tokens = settings_update.max_new_tokens
    settings.temperature = settings_update.temperature
    settings.min_p = settings_update.min_p
    return settings_update
