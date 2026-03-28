"""
Tests for Stage 6 agents.
"""

from agents import (
    AnalyticsAgent,
    ContentAgent,
    InventoryAgent,
    PricingAgent,
    ReviewAgent,
)


def test_analytics_agent_analyze_sales():
    agent = AnalyticsAgent()
    result = agent.analyze_sales(
        [{"quantity": 2, "total_price": 1000}, {"quantity": 1, "total_price": 700}],
        period_days=2,
    )

    assert result["total_orders"] == 2
    assert result["total_units"] == 3
    assert result["total_revenue"] == 1700.0
    assert result["status"] == "completed"


def test_inventory_agent_generate_reorder_recommendation():
    agent = InventoryAgent()
    result = agent.generate_reorder_recommendation(
        products=[
            {"id": 1, "nm_id": 101, "title": "A", "current_stock": 0, "daily_sales_velocity": 2},
            {"id": 2, "nm_id": 102, "title": "B", "current_stock": 20, "daily_sales_velocity": 1},
        ],
        lead_time_days=7,
        safety_stock_days=3,
    )

    assert len(result) == 2
    assert result[0]["priority"] == "critical"
    assert result[0]["recommended_order_qty"] > 0


def test_review_agent_reply_generation():
    agent = ReviewAgent()
    sentiment = agent.analyze_sentiment("Очень плохо, товар брак", rating=1)
    reply = agent.generate_reply(
        review_text="Очень плохо, товар брак",
        sentiment=sentiment["sentiment"],
        product_name="Тестовый товар",
    )
    payload = agent.publish_reply(review_id=10, reply_text=reply)

    assert sentiment["sentiment"] == "negative"
    assert payload["status"] == "ready_to_publish"
    assert "Тестовый товар" in reply


def test_content_agent_description_and_seo():
    agent = ContentAgent()
    draft = agent.generate_product_description(
        {
            "title": "Набор контейнеров",
            "category": "хранение",
            "features": ["герметичная крышка", "без BPA"],
        }
    )
    seo = agent.optimize_seo(
        title=draft["title"],
        description=draft["description"],
        keywords=["контейнеры для хранения", "кухня"],
    )

    assert draft["status"] == "completed"
    assert seo["status"] == "completed"
    assert len(seo["keywords_used"]) == 2


def test_pricing_agent_recommend_price():
    agent = PricingAgent()
    recommendation = agent.recommend_price(
        current_price=1000.0,
        competitor_prices=[950.0, 980.0, 1020.0],
        demand_signal="low",
        cost_price=700.0,
        min_margin_pct=0.2,
    )

    assert recommendation["status"] == "completed"
    assert recommendation["recommended_price"] >= 840.0
