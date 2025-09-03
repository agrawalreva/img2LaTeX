from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class ModelSwitchRequest(BaseModel):
    adapter_path: str


class GenerationSettings(BaseModel):
    max_new_tokens: int = 256
    temperature: float = 0.7
    min_p: float = 0.1


@router.get("/models/current")
async def get_current_model() -> Dict[str, Any]:
    # For now, return mock data
    # In production, this would query the actual loaded model
    return {
        "type": "base",
        "path": "unsloth/Qwen2-VL-7B-Instruct",
        "name": "Qwen2-VL 7B (Base)"
    }


@router.get("/models/adapters")
async def get_available_adapters() -> List[Dict[str, Any]]:
    # For now, return empty list
    # In production, this would scan the artifacts directory
    return []


@router.post("/models/switch")
async def switch_model(request: ModelSwitchRequest) -> Dict[str, Any]:
    # For now, just return success
    # In production, this would actually switch the model
    return {
        "message": f"Model switched to {request.adapter_path}",
        "current_model": request.adapter_path
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
    # For now, just return the updated settings
    # In production, this would update the actual model settings
    return settings_update
