"""
Action Service

Action Layer for executing marketplace operations via Wildberries service.
"""

from typing import Any, Dict, Optional

from config import get_logger
from services.wb_service import WildberriesService, get_wb_service
from database import db_manager
from database.repositories import shop_repository

logger = get_logger(__name__)


class ActionService:
    """
    Executes marketplace actions produced by workflows.

    All external API calls stay in services layer according to project rules.
    """

    def __init__(self, wb_service: Optional[WildberriesService] = None):
        self.wb_service = wb_service

    async def _resolve_wb_service(self, shop_id: Optional[int] = None) -> WildberriesService:
        """
        Resolve Wildberries service instance.

        Priority:
        1) Explicitly injected service (tests/mocks)
        2) Shop-scoped service when shop_id is provided
        3) Global fallback service
        """
        if self.wb_service is not None:
            return self.wb_service

        if shop_id is None:
            return get_wb_service()

        async with db_manager.get_async_session() as db:
            shop = await shop_repository.get_by_id(db, int(shop_id))
        if not shop:
            raise ValueError(f"Shop not found: {shop_id}")
        if not shop.wb_api_key:
            raise ValueError(f"Shop {shop_id} has no wb_api_key configured")
        return WildberriesService(api_key=shop.wb_api_key)

    async def update_price(
        self,
        nm_id: int,
        new_price: float,
        reason: Optional[str] = None,
        discount: Optional[float] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute product price update.
        """
        logger.info(
            "ActionService.update_price nm_id=%s new_price=%s shop_id=%s",
            nm_id,
            new_price,
            shop_id,
        )
        wb_service = await self._resolve_wb_service(shop_id=shop_id)
        api_response = await wb_service.update_price(
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
            "shop_id": shop_id,
            "external_response": api_response,
            "status": "executed",
        }

    async def create_product_card(
        self,
        card_payload: Dict[str, Any],
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute product card creation.
        """
        logger.info("ActionService.create_product_card shop_id=%s", shop_id)
        wb_service = await self._resolve_wb_service(shop_id=shop_id)
        api_response = await wb_service.create_product_card(card_payload=card_payload)
        return {
            "action": "create_product_card",
            "card_payload": card_payload,
            "shop_id": shop_id,
            "external_response": api_response,
            "status": "executed",
        }

    async def reply_to_review(
        self,
        review_id: str,
        reply_text: str,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute review reply publishing.
        """
        logger.info("ActionService.reply_to_review review_id=%s shop_id=%s", review_id, shop_id)
        wb_service = await self._resolve_wb_service(shop_id=shop_id)
        api_response = await wb_service.reply_to_review(
            review_id=review_id,
            reply_text=reply_text,
        )
        return {
            "action": "reply_to_review",
            "review_id": review_id,
            "reply_text": reply_text,
            "shop_id": shop_id,
            "external_response": api_response,
            "status": "executed",
        }


# Singleton instance
action_service = ActionService()
