"""
Tests for Action Layer service.
"""

import pytest

from services.action_service import ActionService


class FakeWBService:
    async def update_price(self, nm_id: int, new_price: float, discount=None):
        return {"status": "updated", "nm_id": nm_id, "new_price": new_price, "discount": discount}

    async def create_product_card(self, card_payload):
        return {"status": "created", "id": "mock-card-1", "payload": card_payload}

    async def reply_to_review(self, review_id: str, reply_text: str):
        return {"status": "answered", "id": review_id, "text": reply_text}


@pytest.mark.asyncio
async def test_update_price_action():
    service = ActionService(wb_service=FakeWBService())
    result = await service.update_price(nm_id=10001, new_price=1990.0, reason="test")
    assert result["status"] == "executed"
    assert result["external_response"]["status"] == "updated"


@pytest.mark.asyncio
async def test_create_product_card_action():
    service = ActionService(wb_service=FakeWBService())
    result = await service.create_product_card(card_payload={"title": "Test"})
    assert result["status"] == "executed"
    assert result["external_response"]["status"] == "created"


@pytest.mark.asyncio
async def test_reply_to_review_action():
    service = ActionService(wb_service=FakeWBService())
    result = await service.reply_to_review(review_id="feedback-1", reply_text="Thanks")
    assert result["status"] == "executed"
    assert result["external_response"]["status"] == "answered"
