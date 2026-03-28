"""
Pricing Agent

Stateless agent for competitive pricing analysis and recommendations.
"""

from typing import Any, Dict, List, Optional

from config import get_logger

logger = get_logger(__name__)


class PricingAgent:
    """
    Stateless pricing agent.

    Responsibilities:
    - Analyze competitor prices
    - Estimate demand signal
    - Recommend and prepare price updates
    """

    def analyze_competitor_prices(
        self,
        own_price: float,
        competitor_prices: List[float],
    ) -> Dict[str, Any]:
        """
        Compare own price with market distribution.
        """
        if not competitor_prices:
            return {
                "own_price": own_price,
                "market_min": own_price,
                "market_max": own_price,
                "market_average": own_price,
                "position": "unknown",
                "status": "insufficient_data",
            }

        market_min = min(competitor_prices)
        market_max = max(competitor_prices)
        market_avg = sum(competitor_prices) / len(competitor_prices)

        if own_price < market_min:
            position = "below_market"
        elif own_price > market_max:
            position = "above_market"
        else:
            position = "within_market"

        return {
            "own_price": round(own_price, 2),
            "market_min": round(market_min, 2),
            "market_max": round(market_max, 2),
            "market_average": round(market_avg, 2),
            "position": position,
            "status": "completed",
        }

    def estimate_demand(
        self,
        sales_history: List[Dict[str, Any]],
        price_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Estimate demand signal based on recent sales dynamics.
        """
        if len(sales_history) < 2:
            return {"demand_signal": "unknown", "change_pct": 0.0, "status": "insufficient_data"}

        quantities = [float(item.get("quantity", 0) or 0) for item in sales_history]
        first_half = quantities[: len(quantities) // 2] or [quantities[0]]
        second_half = quantities[len(quantities) // 2 :] or [quantities[-1]]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        if avg_first == 0:
            change_pct = 100.0 if avg_second > 0 else 0.0
        else:
            change_pct = ((avg_second - avg_first) / avg_first) * 100

        if change_pct > 12:
            demand_signal = "high"
        elif change_pct < -12:
            demand_signal = "low"
        else:
            demand_signal = "stable"

        return {
            "demand_signal": demand_signal,
            "change_pct": round(change_pct, 2),
            "status": "completed",
        }

    def recommend_price(
        self,
        current_price: float,
        competitor_prices: List[float],
        demand_signal: str = "stable",
        cost_price: Optional[float] = None,
        min_margin_pct: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Recommend target price based on market and demand.
        """
        analysis = self.analyze_competitor_prices(current_price, competitor_prices)
        market_average = float(analysis["market_average"])

        if demand_signal == "high":
            target_price = max(current_price, market_average * 1.03)
            rationale = "high_demand"
        elif demand_signal == "low":
            target_price = min(current_price, market_average * 0.98)
            rationale = "low_demand"
        else:
            target_price = market_average
            rationale = "market_alignment"

        if cost_price is not None:
            min_allowed = cost_price * (1 + min_margin_pct)
            target_price = max(target_price, min_allowed)

        change_pct = ((target_price - current_price) / current_price * 100) if current_price else 0.0

        return {
            "current_price": round(current_price, 2),
            "recommended_price": round(target_price, 2),
            "change_pct": round(change_pct, 2),
            "rationale": rationale,
            "demand_signal": demand_signal,
            "status": "completed",
        }

    def update_price(self, product_id: int, new_price: float, reason: str) -> Dict[str, Any]:
        """
        Prepare payload for Action Layer.

        Stage 6 keeps this as a pure payload, without direct API calls.
        """
        logger.info("PricingAgent prepared price update for product_id=%s", product_id)
        return {
            "product_id": product_id,
            "new_price": round(new_price, 2),
            "reason": reason,
            "status": "ready_to_execute",
        }
