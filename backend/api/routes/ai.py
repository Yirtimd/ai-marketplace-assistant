"""
AI API routes

Endpoints for direct AI service checks and generation tasks.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import ai_service
from orchestrator import orchestrator

router = APIRouter(prefix="/ai", tags=["AI"])


class GenerateTextRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 700


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    size: str = "1024x1024"
    quality: str = "standard"


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    duration_seconds: int = 15


@router.get("/providers")
async def ai_providers_status():
    """Get configured providers status (without exposing secret values)."""
    return {
        "deepseek_configured": bool(ai_service.deepseek_api_key),
        "openai_configured": bool(ai_service.openai_api_key),
        "anthropic_configured": bool(ai_service.anthropic_api_key),
        "deepseek_model": ai_service.deepseek_model,
        "openai_model": ai_service.openai_model,
        "anthropic_model": ai_service.anthropic_model,
    }


@router.post("/generate-text")
async def generate_text(request: GenerateTextRequest):
    """Generate text through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="ai_generation_workflow",
            context={
                "operation": "generate_text",
                "params": {
                    "prompt": request.prompt,
                    "system_prompt": request.system_prompt,
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                },
            },
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-image")
async def generate_image(request: GenerateImageRequest):
    """Generate image through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="ai_generation_workflow",
            context={
                "operation": "generate_image",
                "params": {
                    "prompt": request.prompt,
                    "size": request.size,
                    "quality": request.quality,
                },
            },
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-video")
async def generate_video(request: GenerateVideoRequest):
    """Generate video through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="ai_generation_workflow",
            context={
                "operation": "generate_video",
                "params": {
                    "prompt": request.prompt,
                    "duration_seconds": request.duration_seconds,
                },
            },
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
