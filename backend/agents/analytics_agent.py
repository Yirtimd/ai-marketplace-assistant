"""
Analytics Agent

Stateless agent for sales analytics and trend detection.
"""

from typing import Any, Dict, List, Optional

from config import get_logger

logger = get_logger(__name__)


class AnalyticsAgent:
    """
    Stateless analytics agent.

    Responsibilities:
    - Analyze sales performance
    - Detect trends
    - Compare own pricing against competitors
    """

    def analyze_sales(
        self,
        sales_data: List[Dict[str, Any]],
        period_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Analyze sales data and return compact report.

        Args:
            sales_data: List of sales records with at least `quantity` and `total_price`.
            period_days: Analysis period in days.

        Returns:
            Sales analytics report.
        """
        if not sales_data:
            return {
                "period_days": period_days,
                "total_orders": 0,
                "total_units": 0,
                "total_revenue": 0.0,
                "average_order_value": 0.0,
                "status": "insufficient_data",
            }

        total_orders = len(sales_data)
        total_units = float(sum(float(item.get("quantity", 1) or 0) for item in sales_data))
        total_revenue = float(sum(float(item.get("total_price", 0) or 0) for item in sales_data))
        average_order_value = total_revenue / total_orders if total_orders else 0.0

        logger.info(
            "AnalyticsAgent analyzed sales: orders=%s, revenue=%.2f",
            total_orders,
            total_revenue,
        )

        return {
            "period_days": period_days,
            "total_orders": total_orders,
            "total_units": int(total_units),
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(average_order_value, 2),
            "status": "completed",
        }

    def detect_trends(self, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect a simple sales trend based on chronological revenue sequence.

        Args:
            sales_data: Ordered sales records (oldest -> newest).

        Returns:
            Trend result with signal and confidence.
        """
        revenues = [float(item.get("total_price", 0) or 0) for item in sales_data]

        if len(revenues) < 2:
            return {
                "trend": "unknown",
                "change_pct": 0.0,
                "confidence": "low",
                "status": "insufficient_data",
            }

        first_half = revenues[: len(revenues) // 2] or [revenues[0]]
        second_half = revenues[len(revenues) // 2 :] or [revenues[-1]]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        if avg_first == 0:
            change_pct = 100.0 if avg_second > 0 else 0.0
        else:
            change_pct = ((avg_second - avg_first) / avg_first) * 100

        if change_pct > 7:
            trend = "growing"
        elif change_pct < -7:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_pct": round(change_pct, 2),
            "confidence": "medium" if len(revenues) >= 7 else "low",
            "status": "completed",
        }

    def analyze_competitors(
        self,
        own_price: float,
        competitor_prices: List[float],
        own_position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compare own price with competitor prices.

        Args:
            own_price: Current shop price.
            competitor_prices: List of competitor prices.
            own_position: Optional ranking position in search.

        Returns:
            Competitive price analysis.
        """
        if not competitor_prices:
            return {
                "own_price": own_price,
                "market_average_price": own_price,
                "delta_to_market_pct": 0.0,
                "recommendation": "collect_more_competitor_data",
                "own_position": own_position,
                "status": "insufficient_data",
            }

        market_avg = sum(competitor_prices) / len(competitor_prices)
        delta_pct = ((own_price - market_avg) / market_avg) * 100 if market_avg else 0.0

        if delta_pct > 10:
            recommendation = "consider_price_decrease"
        elif delta_pct < -10:
            recommendation = "consider_margin_increase"
        else:
            recommendation = "keep_current_price"

        return {
            "own_price": round(own_price, 2),
            "market_average_price": round(market_avg, 2),
            "delta_to_market_pct": round(delta_pct, 2),
            "recommendation": recommendation,
            "own_position": own_position,
            "status": "completed",
        }
