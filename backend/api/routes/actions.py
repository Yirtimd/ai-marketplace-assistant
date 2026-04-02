"""
Action Layer API routes

Endpoints for executing marketplace actions via ActionService.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from orchestrator import orchestrator

router = APIRouter(prefix="/actions", tags=["Actions"])


class UpdatePriceRequest(BaseModel):
    shop_id: Optional[int] = None
    nm_id: int
    new_price: float
    reason: Optional[str] = None
    discount: Optional[float] = None


class CreateProductCardRequest(BaseModel):
    shop_id: Optional[int] = None
    card_payload: Dict[str, Any] = Field(default_factory=dict)


class ReplyToReviewRequest(BaseModel):
    shop_id: Optional[int] = None
    review_id: str
    reply_text: str


@router.post("/update-price")
async def update_price(request: UpdatePriceRequest):
    """Execute product price update through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="action_execution_workflow",
            context={
                "operation": "update_price",
                "params": {
                    "shop_id": request.shop_id,
                    "nm_id": request.nm_id,
                    "new_price": request.new_price,
                    "reason": request.reason,
                    "discount": request.discount,
                },
            },
            shop_id=request.shop_id,
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/create-product-card")
async def create_product_card(request: CreateProductCardRequest):
    """Execute product card creation through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="action_execution_workflow",
            context={
                "operation": "create_product_card",
                "params": {
                    "shop_id": request.shop_id,
                    "card_payload": request.card_payload,
                },
            },
            shop_id=request.shop_id,
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reply-to-review")
async def reply_to_review(request: ReplyToReviewRequest):
    """Execute review reply through orchestrator workflow."""
    try:
        workflow_response = await orchestrator.execute_workflow(
            workflow_name="action_execution_workflow",
            context={
                "operation": "reply_to_review",
                "params": {
                    "shop_id": request.shop_id,
                    "review_id": request.review_id,
                    "reply_text": request.reply_text,
                },
            },
            shop_id=request.shop_id,
        )
        if workflow_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail=workflow_response.get("error", "Workflow failed"))
        return workflow_response.get("result", {}).get("output", {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
