"""
Inventory Agent

Stateless agent for stock analysis and restock recommendations.
"""

from math import ceil
from typing import Any, Dict, List, Optional

from config import get_logger

logger = get_logger(__name__)


class InventoryAgent:
    """
    Stateless inventory agent.

    Responsibilities:
    - Calculate sales velocity
    - Predict stock-out horizon
    - Generate reorder recommendations
    """

    def calculate_sales_velocity(
        self,
        sales_data: List[Dict[str, Any]],
        period_days: int = 7,
    ) -> float:
        """
        Calculate average daily units sold.

        Args:
            sales_data: List of sales records with `quantity`.
            period_days: Number of days in period.

        Returns:
            Units/day velocity.
        """
        if not sales_data or period_days <= 0:
            return 0.0

        total_units = sum(float(item.get("quantity", 1) or 0) for item in sales_data)
        return total_units / period_days

    def predict_stock_out(self, current_stock: int, sales_velocity: float) -> Optional[int]:
        """
        Predict in how many days stock will be depleted.

        Args:
            current_stock: Current available stock.
            sales_velocity: Units/day.

        Returns:
            Days until stock-out, or None when prediction is not possible.
        """
        if current_stock <= 0:
            return 0
        if sales_velocity <= 0:
            return None
        return int(current_stock / sales_velocity)

    def generate_reorder_recommendation(
        self,
        products: List[Dict[str, Any]],
        lead_time_days: int = 7,
        safety_stock_days: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Build reorder recommendations for products.

        Args:
            products: Product records with `id`, `nm_id`, `title`, `current_stock`.
            lead_time_days: Supplier lead time in days.
            safety_stock_days: Additional safety stock period.

        Returns:
            List of recommendation payloads.
        """
        recommendations: List[Dict[str, Any]] = []

        for product in products:
            current_stock = int(product.get("current_stock", 0) or 0)
            daily_sales = float(product.get("daily_sales_velocity", 1.0) or 1.0)
            days_until_stockout = self.predict_stock_out(current_stock, daily_sales)

            horizon = max(lead_time_days + safety_stock_days, 1)
            target_stock = ceil(daily_sales * horizon)
            reorder_qty = max(target_stock - current_stock, 0)

            if current_stock <= 0:
                priority = "critical"
                action = "Order immediately"
            elif days_until_stockout is not None and days_until_stockout <= lead_time_days:
                priority = "high"
                action = "Create urgent purchase order"
            elif days_until_stockout is not None and days_until_stockout <= lead_time_days + safety_stock_days:
                priority = "medium"
                action = "Plan replenishment this week"
            else:
                priority = "low"
                action = "Monitor stock dynamics"

            recommendations.append(
                {
                    "product_id": product.get("id"),
                    "nm_id": product.get("nm_id"),
                    "title": product.get("title"),
                    "current_stock": current_stock,
                    "daily_sales_velocity": round(daily_sales, 2),
                    "days_until_stockout": days_until_stockout,
                    "target_stock": target_stock,
                    "recommended_order_qty": reorder_qty,
                    "priority": priority,
                    "recommended_action": action,
                }
            )

        logger.info("InventoryAgent generated %s recommendations", len(recommendations))
        return recommendations
