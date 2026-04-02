"""
Pricing Workflow

LangGraph workflow for pricing analysis and recommendation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents import PricingAgent
from database import db_manager
from database.repositories import price_history_repository, product_repository, sale_repository
from services import ai_service, action_service
from workflows.base import BaseWorkflow


class PricingState(TypedDict):
    workflow_id: str
    shop_id: Optional[int]
    execute_action: bool
    product_id: Optional[int]
    current_price: float
    competitor_prices: List[float]
    sales_history: List[Dict[str, Any]]
    market_analysis: Dict[str, Any]
    demand_analysis: Dict[str, Any]
    recommendation: Dict[str, Any]
    ai_explanation: Dict[str, Any]
    update_payload: Dict[str, Any]
    action_result: Dict[str, Any]
    result: Dict[str, Any]


class PricingWorkflow(BaseWorkflow):
    """Analyze market and demand, then prepare a pricing decision."""

    def __init__(self):
        super().__init__()
        self.pricing_agent = PricingAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(PricingState)
        workflow.add_node("load_pricing_data", self._load_pricing_data)
        workflow.add_node("analyze_competitor_prices", self._analyze_competitor_prices)
        workflow.add_node("estimate_demand", self._estimate_demand)
        workflow.add_node("recommend_price", self._recommend_price)
        workflow.add_node("prepare_update_payload", self._prepare_update_payload)
        workflow.add_node("execute_marketplace_action", self._execute_action)
        workflow.add_node("format_result", self._format_result)

        workflow.set_entry_point("load_pricing_data")
        workflow.add_edge("load_pricing_data", "analyze_competitor_prices")
        workflow.add_edge("analyze_competitor_prices", "estimate_demand")
        workflow.add_edge("estimate_demand", "recommend_price")
        workflow.add_edge("recommend_price", "prepare_update_payload")
        workflow.add_edge("prepare_update_payload", "execute_marketplace_action")
        workflow.add_edge("execute_marketplace_action", "format_result")
        workflow.add_edge("format_result", END)
        return workflow.compile()

    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        initial_state: PricingState = {
            "workflow_id": workflow_id,
            "shop_id": shop_id or context.get("shop_id"),
            "execute_action": bool(context.get("execute_action", False)),
            "product_id": context.get("product_id"),
            "current_price": float(context.get("current_price", 0) or 0),
            "competitor_prices": list(context.get("competitor_prices", [])),
            "sales_history": list(context.get("sales_history", [])),
            "market_analysis": {},
            "demand_analysis": {},
            "recommendation": {},
            "ai_explanation": {},
            "update_payload": {},
            "action_result": {},
            "result": {},
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _load_pricing_data(self, state: PricingState) -> PricingState:
        """Load current product price and recent sales when missing in context."""
        if not state["product_id"]:
            return state

        async with db_manager.get_async_session() as db:
            product = await product_repository.get_by_id(db, int(state["product_id"]))
            if product and state["current_price"] <= 0:
                state["current_price"] = float(product.price or 0)

            if not state["sales_history"] and state["shop_id"]:
                date_to = datetime.utcnow()
                date_from = date_to - timedelta(days=14)
                sales = await sale_repository.get_by_date_range(
                    db=db,
                    shop_id=int(state["shop_id"]),
                    date_from=date_from,
                    date_to=date_to,
                )
                state["sales_history"] = [
                    {
                        "product_id": item.product_id,
                        "quantity": int(item.quantity or 0),
                        "sale_date": item.sale_date.isoformat() if item.sale_date else None,
                    }
                    for item in sales
                    if item.product_id == int(state["product_id"])
                ]

            if state["current_price"] <= 0:
                latest_price = await price_history_repository.get_latest(db, int(state["product_id"]))
                if latest_price:
                    state["current_price"] = float(latest_price.final_price or latest_price.price or 0)

        return state

    async def _analyze_competitor_prices(self, state: PricingState) -> PricingState:
        state["market_analysis"] = self.pricing_agent.analyze_competitor_prices(
            own_price=state["current_price"],
            competitor_prices=state["competitor_prices"],
        )
        return state

    async def _estimate_demand(self, state: PricingState) -> PricingState:
        state["demand_analysis"] = self.pricing_agent.estimate_demand(
            sales_history=state["sales_history"],
            price_history=None,
        )
        return state

    async def _recommend_price(self, state: PricingState) -> PricingState:
        state["recommendation"] = self.pricing_agent.recommend_price(
            current_price=state["current_price"],
            competitor_prices=state["competitor_prices"] or [state["current_price"]],
            demand_signal=state["demand_analysis"].get("demand_signal", "stable"),
        )

        try:
            ai_result = await ai_service.generate_text(
                prompt=(
                    "Кратко объясни решение по цене для менеджера магазина (2-3 предложения). "
                    f"Market: {state['market_analysis']}. Demand: {state['demand_analysis']}. "
                    f"Recommendation: {state['recommendation']}."
                ),
                system_prompt="Ты pricing-аналитик e-commerce.",
                temperature=0.2,
                max_tokens=160,
            )
            state["ai_explanation"] = ai_result
        except Exception as exc:
            state["ai_explanation"] = {
                "status": "fallback_to_rule_based",
                "error": str(exc),
            }
        return state

    async def _prepare_update_payload(self, state: PricingState) -> PricingState:
        if not state["product_id"]:
            state["update_payload"] = {
                "status": "missing_product_id",
                "recommended_price": state["recommendation"].get("recommended_price"),
            }
            return state

        state["update_payload"] = self.pricing_agent.update_price(
            product_id=int(state["product_id"]),
            new_price=float(state["recommendation"].get("recommended_price", state["current_price"])),
            reason=state["recommendation"].get("rationale", "market_alignment"),
        )
        return state

    async def _execute_action(self, state: PricingState) -> PricingState:
        if not state["execute_action"]:
            state["action_result"] = {"status": "skipped", "reason": "execute_action=false"}
            return state

        if state["update_payload"].get("status") != "ready_to_execute":
            state["action_result"] = {
                "status": "skipped",
                "reason": "update_payload_not_ready",
                "update_payload_status": state["update_payload"].get("status"),
            }
            return state

        try:
            state["action_result"] = await action_service.update_price(
                nm_id=int(state["update_payload"]["product_id"]),
                new_price=float(state["update_payload"]["new_price"]),
                reason=state["update_payload"].get("reason"),
                shop_id=state["shop_id"],
            )
        except Exception as exc:
            state["action_result"] = {"status": "failed", "error": str(exc)}
        return state

    async def _format_result(self, state: PricingState) -> PricingState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "pricing_workflow",
            "product_id": state["product_id"],
            "current_price": state["current_price"],
            "market_analysis": state["market_analysis"],
            "demand_analysis": state["demand_analysis"],
            "recommendation": state["recommendation"],
            "ai_explanation": state["ai_explanation"],
            "update_payload": state["update_payload"],
            "action_result": state["action_result"],
            "status": "completed",
        }
        return state
