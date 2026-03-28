"""
Action Layer API routes

Endpoints for executing marketplace actions via ActionService.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import action_service

router = APIRouter(prefix="/actions", tags=["Actions"])


class UpdatePriceRequest(BaseModel):
    nm_id: int
    new_price: float
    reason: Optional[str] = None
    discount: Optional[float] = None


class CreateProductCardRequest(BaseModel):
    card_payload: Dict[str, Any] = Field(default_factory=dict)


class ReplyToReviewRequest(BaseModel):
    review_id: str
    reply_text: str


@router.post("/update-price")
async def update_price(request: UpdatePriceRequest):
    """Execute product price update action."""
    try:
        return await action_service.update_price(
            nm_id=request.nm_id,
            new_price=request.new_price,
            reason=request.reason,
            discount=request.discount,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/create-product-card")
async def create_product_card(request: CreateProductCardRequest):
    """Execute product card creation action."""
    try:
        return await action_service.create_product_card(card_payload=request.card_payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reply-to-review")
async def reply_to_review(request: ReplyToReviewRequest):
    """Execute review reply action."""
    try:
        return await action_service.reply_to_review(
            review_id=request.review_id,
            reply_text=request.reply_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
