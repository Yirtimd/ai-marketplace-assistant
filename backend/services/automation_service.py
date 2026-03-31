"""
Automation Service

Stage 11 automation orchestration:
- detect sales drop
- detect low stock
- generate price optimization recommendations
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config import get_logger, settings
from database import db_manager
from database.models.event import EventLevel, EventType
from database.repositories import event_repository, product_repository, sale_repository, shop_repository
from orchestrator import orchestrator

logger = get_logger(__name__)


class AutomationService:
    """Service for periodic automation cycle."""

    async def run_automation_cycle(
        self,
        shop_id: Optional[int] = None,
        execute_actions: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Run automation checks for one shop or all shops.
        """
        if not settings.automation_enabled:
            return {"status": "disabled", "message": "Automation is disabled by settings"}

        effective_execute_actions = (
            settings.automation_execute_actions
            if execute_actions is None
            else bool(execute_actions)
        )

        async with db_manager.get_async_session() as db:
            if shop_id is not None:
                shops = []
                shop = await shop_repository.get_by_id(db, int(shop_id))
                if shop:
                    shops.append(shop)
            else:
                shops = await shop_repository.get_all(db, skip=0, limit=1000)

        cycle_results: List[Dict[str, Any]] = []
        for shop in shops:
            result = await self._evaluate_shop(
                shop_id=shop.id,
                shop_name=shop.name,
                execute_actions=effective_execute_actions,
            )
            cycle_results.append(result)

        return {
            "status": "completed",
            "shops_processed": len(cycle_results),
            "execute_actions": effective_execute_actions,
            "results": cycle_results,
        }

    async def _evaluate_shop(
        self,
        shop_id: int,
        shop_name: str,
        execute_actions: bool,
    ) -> Dict[str, Any]:
        """
        Evaluate automation rules for a single shop.
        """
        sales_trigger = await self._check_sales_drop(shop_id=shop_id)
        stock_trigger = await self._check_low_stock(shop_id=shop_id)
        pricing_trigger = await self._check_pricing_opportunity(shop_id=shop_id)

        workflows_triggered: List[Dict[str, Any]] = []

        if sales_trigger["triggered"]:
            workflows_triggered.append(
                await self._trigger_workflow(
                    workflow_name="sales_analysis_workflow",
                    context={"shop_id": shop_id, "days_back": 14, "trigger": "sales_drop_automation"},
                    shop_id=shop_id,
                    title="Sales drop detected",
                    message=(
                        f"Shop '{shop_name}': sales dropped by "
                        f"{sales_trigger.get('drop_pct', 0):.2f}% over the last week."
                    ),
                    details=sales_trigger,
                    level=EventLevel.WARNING,
                )
            )

        if stock_trigger["triggered"]:
            workflows_triggered.append(
                await self._trigger_workflow(
                    workflow_name="inventory_workflow",
                    context={
                        "shop_id": shop_id,
                        "threshold": settings.automation_low_stock_threshold,
                        "trigger": "low_stock_automation",
                    },
                    shop_id=shop_id,
                    title="Low stock alert",
                    message=(
                        f"Shop '{shop_name}': {stock_trigger.get('low_stock_count', 0)} items "
                        "are below stock threshold."
                    ),
                    details=stock_trigger,
                    level=EventLevel.WARNING,
                )
            )

        if pricing_trigger["triggered"]:
            workflows_triggered.append(
                await self._trigger_workflow(
                    workflow_name="pricing_workflow",
                    context={
                        "shop_id": shop_id,
                        "product_id": pricing_trigger.get("product_id"),
                        "current_price": pricing_trigger.get("current_price"),
                        "competitor_prices": pricing_trigger.get("competitor_prices", []),
                        "sales_history": pricing_trigger.get("sales_history", []),
                        "execute_action": execute_actions,
                        "trigger": "pricing_automation",
                    },
                    shop_id=shop_id,
                    title="Pricing opportunity found",
                    message=(
                        f"Shop '{shop_name}': product {pricing_trigger.get('product_id')} "
                        "has low demand and high stock."
                    ),
                    details=pricing_trigger,
                    level=EventLevel.INFO,
                )
            )

        return {
            "shop_id": shop_id,
            "shop_name": shop_name,
            "sales_trigger": sales_trigger,
            "stock_trigger": stock_trigger,
            "pricing_trigger": pricing_trigger,
            "workflows_triggered": workflows_triggered,
        }

    async def _check_sales_drop(self, shop_id: int) -> Dict[str, Any]:
        date_to = datetime.utcnow()
        date_from = date_to - timedelta(days=14)
        mid = date_to - timedelta(days=7)

        async with db_manager.get_async_session() as db:
            sales = await sale_repository.get_by_date_range(
                db=db,
                shop_id=shop_id,
                date_from=date_from,
                date_to=date_to,
            )

        previous_week = sum(float(item.total_price or 0) for item in sales if item.sale_date < mid)
        current_week = sum(float(item.total_price or 0) for item in sales if item.sale_date >= mid)

        if previous_week <= 0:
            return {
                "triggered": False,
                "reason": "insufficient_baseline",
                "previous_week_revenue": previous_week,
                "current_week_revenue": current_week,
            }

        drop_pct = ((previous_week - current_week) / previous_week) * 100
        triggered = drop_pct >= settings.automation_sales_drop_threshold_pct
        return {
            "triggered": triggered,
            "drop_pct": round(drop_pct, 2),
            "previous_week_revenue": round(previous_week, 2),
            "current_week_revenue": round(current_week, 2),
            "threshold_pct": settings.automation_sales_drop_threshold_pct,
        }

    async def _check_low_stock(self, shop_id: int) -> Dict[str, Any]:
        async with db_manager.get_async_session() as db:
            products = await product_repository.get_by_shop(db, shop_id=shop_id, skip=0, limit=1000)

        low = [
            {
                "product_id": item.id,
                "nm_id": item.nm_id,
                "title": item.title,
                "current_stock": int(item.current_stock or 0),
            }
            for item in products
            if item.is_active and int(item.current_stock or 0) <= settings.automation_low_stock_threshold
        ]

        return {
            "triggered": len(low) > 0,
            "low_stock_count": len(low),
            "threshold": settings.automation_low_stock_threshold,
            "products": low[:20],
        }

    async def _check_pricing_opportunity(self, shop_id: int) -> Dict[str, Any]:
        """
        Heuristic rule:
        - product has high stock
        - product had no sales in last 7 days
        """
        date_to = datetime.utcnow()
        date_from = date_to - timedelta(days=7)

        async with db_manager.get_async_session() as db:
            products = await product_repository.get_by_shop(db, shop_id=shop_id, skip=0, limit=500)
            sales = await sale_repository.get_by_date_range(
                db=db,
                shop_id=shop_id,
                date_from=date_from,
                date_to=date_to,
            )

        sales_by_product: Dict[int, int] = {}
        sales_history: Dict[int, List[Dict[str, Any]]] = {}
        for sale in sales:
            sales_by_product[sale.product_id] = sales_by_product.get(sale.product_id, 0) + int(sale.quantity or 0)
            sales_history.setdefault(sale.product_id, []).append({"quantity": int(sale.quantity or 0)})

        candidate = None
        for item in products:
            if not item.is_active:
                continue
            if not item.price or float(item.price) <= 0:
                continue
            if int(item.current_stock or 0) < settings.automation_low_stock_threshold * 2:
                continue
            if sales_by_product.get(item.id, 0) == 0:
                candidate = item
                break

        if not candidate:
            return {"triggered": False, "reason": "no_candidate"}

        current_price = float(candidate.price or 0)
        competitor_prices = [round(current_price * ratio, 2) for ratio in (0.95, 0.98, 1.02)]
        return {
            "triggered": True,
            "product_id": candidate.id,
            "nm_id": candidate.nm_id,
            "current_price": current_price,
            "competitor_prices": competitor_prices,
            "sales_history": sales_history.get(candidate.id, []),
            "reason": "high_stock_with_low_recent_sales",
        }

    async def _trigger_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any],
        shop_id: int,
        title: str,
        message: str,
        details: Dict[str, Any],
        level: EventLevel,
    ) -> Dict[str, Any]:
        """
        Trigger workflow and log automation event.
        """
        workflow_result = await orchestrator.execute_workflow(
            workflow_name=workflow_name,
            context=context,
            shop_id=shop_id,
        )

        await self._create_event(
            shop_id=shop_id,
            title=title,
            message=message,
            level=level,
            details={
                "workflow_name": workflow_name,
                "workflow_result": workflow_result,
                "automation_details": details,
            },
        )

        return {
            "workflow_name": workflow_name,
            "workflow_id": workflow_result.get("workflow_id"),
            "status": workflow_result.get("status"),
        }

    async def _create_event(
        self,
        shop_id: int,
        title: str,
        message: str,
        level: EventLevel,
        details: Dict[str, Any],
    ) -> None:
        """
        Persist automation event notification.
        """
        try:
            async with db_manager.get_async_session() as db:
                await event_repository.create(
                    db,
                    {
                        "shop_id": shop_id,
                        "event_type": EventType.NOTIFICATION,
                        "event_level": level,
                        "title": title,
                        "message": message,
                        "details": details,
                        "source": "automation_service",
                        "event_time": datetime.utcnow(),
                    },
                )
        except Exception as exc:
            logger.warning("Failed to store automation event for shop %s: %s", shop_id, exc)


# Singleton instance
automation_service = AutomationService()
