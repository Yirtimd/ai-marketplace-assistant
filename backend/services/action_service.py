"""
Action Service

Action Layer for executing marketplace operations via Wildberries service.
"""

from typing import Any, Dict, Optional

from config import get_logger
from services.wb_service import WildberriesService, get_wb_service

logger = get_logger(__name__)


class ActionService:
    """
    Executes marketplace actions produced by workflows.

    All external API calls stay in services layer according to project rules.
    """

    def __init__(self, wb_service: Optional[WildberriesService] = None):
        self.wb_service = wb_service or get_wb_service()

    async def update_price(
        self,
        nm_id: int,
        new_price: float,
        reason: Optional[str] = None,
        discount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute product price update.
        """
        logger.info("ActionService.update_price nm_id=%s new_price=%s", nm_id, new_price)
        api_response = await self.wb_service.update_price(
            nm_id=nm_id,
            new_price=new_price,
            discount=discount,
        )
        return {
            "action": "update_price",
            "nm_id": nm_id,
            "new_price": new_price,
            "discount": discount,
            "reason": reason,
            "external_response": api_response,
            "status": "executed",
        }

    async def create_product_card(self, card_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute product card creation.
        """
        logger.info("ActionService.create_product_card")
        api_response = await self.wb_service.create_product_card(card_payload=card_payload)
        return {
            "action": "create_product_card",
            "card_payload": card_payload,
            "external_response": api_response,
            "status": "executed",
        }

    async def reply_to_review(self, review_id: str, reply_text: str) -> Dict[str, Any]:
        """
        Execute review reply publishing.
        """
        logger.info("ActionService.reply_to_review review_id=%s", review_id)
        api_response = await self.wb_service.reply_to_review(
            review_id=review_id,
            reply_text=reply_text,
        )
        return {
            "action": "reply_to_review",
            "review_id": review_id,
            "reply_text": reply_text,
            "external_response": api_response,
            "status": "executed",
        }


# Singleton instance
action_service = ActionService()
