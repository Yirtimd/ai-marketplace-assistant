"""
Inventory Workflow

LangGraph workflow for inventory monitoring and reorder recommendations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents import InventoryAgent
from database import db_manager
from database.repositories import product_repository, sale_repository
from workflows.base import BaseWorkflow


class InventoryWorkflowState(TypedDict):
    workflow_id: str
    shop_id: Optional[int]
    threshold: int
    days_back: int
    products: List[Dict[str, Any]]
    low_stock_products: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    result: Dict[str, Any]


class InventoryWorkflow(BaseWorkflow):
    """Inventory workflow built for Stage 7."""

    def __init__(self):
        super().__init__()
        self.inventory_agent = InventoryAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(InventoryWorkflowState)
        workflow.add_node("load_inventory_data", self._load_inventory_data)
        workflow.add_node("check_stock_levels", self._check_stock_levels)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("format_result", self._format_result)

        workflow.set_entry_point("load_inventory_data")
        workflow.add_edge("load_inventory_data", "check_stock_levels")
        workflow.add_edge("check_stock_levels", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "format_result")
        workflow.add_edge("format_result", END)
        return workflow.compile()

    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        initial_state: InventoryWorkflowState = {
            "workflow_id": workflow_id,
            "shop_id": shop_id or context.get("shop_id"),
            "threshold": int(context.get("threshold", 10)),
            "days_back": int(context.get("days_back", 14)),
            "products": list(context.get("products", [])),
            "low_stock_products": [],
            "recommendations": [],
            "result": {},
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _load_inventory_data(self, state: InventoryWorkflowState) -> InventoryWorkflowState:
        """Load products and enrich with daily sales velocity."""
        if not state["products"]:
            if not state["shop_id"]:
                return state

            async with db_manager.get_async_session() as db:
                products = await product_repository.get_by_shop(
                    db=db,
                    shop_id=int(state["shop_id"]),
                    skip=0,
                    limit=1000,
                )

                date_to = datetime.utcnow()
                date_from = date_to - timedelta(days=state["days_back"])
                sales = await sale_repository.get_by_date_range(
                    db=db,
                    shop_id=int(state["shop_id"]),
                    date_from=date_from,
                    date_to=date_to,
                )

            sales_by_product: Dict[int, float] = {}
            for sale in sales:
                sales_by_product[sale.product_id] = sales_by_product.get(sale.product_id, 0.0) + float(
                    sale.quantity or 0
                )

            state["products"] = [
                {
                    "id": item.id,
                    "nm_id": item.nm_id,
                    "title": item.title,
                    "current_stock": int(item.current_stock or 0),
                    "is_active": bool(item.is_active),
                    "daily_sales_velocity": (
                        sales_by_product.get(item.id, 0.0) / max(state["days_back"], 1)
                    ),
                }
                for item in products
            ]
            return state

        # If products are provided by context, ensure required fields exist.
        normalized: List[Dict[str, Any]] = []
        for item in state["products"]:
            normalized.append(
                {
                    "id": item.get("id"),
                    "nm_id": item.get("nm_id"),
                    "title": item.get("title"),
                    "current_stock": int(item.get("current_stock", 0) or 0),
                    "is_active": bool(item.get("is_active", True)),
                    "daily_sales_velocity": float(item.get("daily_sales_velocity", 1.0) or 1.0),
                }
            )
        state["products"] = normalized
        return state

    async def _check_stock_levels(self, state: InventoryWorkflowState) -> InventoryWorkflowState:
        threshold = state["threshold"]
        state["low_stock_products"] = [
            product
            for product in state["products"]
            if product["is_active"] and int(product["current_stock"]) <= threshold
        ]
        return state

    async def _generate_recommendations(self, state: InventoryWorkflowState) -> InventoryWorkflowState:
        state["recommendations"] = self.inventory_agent.generate_reorder_recommendation(
            products=state["low_stock_products"],
            lead_time_days=7,
            safety_stock_days=3,
        )
        return state

    async def _format_result(self, state: InventoryWorkflowState) -> InventoryWorkflowState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "inventory_workflow",
            "shop_id": state["shop_id"],
            "total_products": len(state["products"]),
            "low_stock_count": len(state["low_stock_products"]),
            "recommendations": state["recommendations"],
            "status": "completed",
        }
        return state
