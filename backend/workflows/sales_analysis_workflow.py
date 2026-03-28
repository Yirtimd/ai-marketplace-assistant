"""
Sales Analysis Workflow

LangGraph workflow for analyzing sales dynamics and producing recommendations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents import AnalyticsAgent
from config import get_logger
from database import db_manager
from database.repositories import sale_repository
from services import ai_service
from workflows.base import BaseWorkflow

logger = get_logger(__name__)


class SalesAnalysisState(TypedDict):
    workflow_id: str
    shop_id: Optional[int]
    days_back: int
    sales_data: List[Dict[str, Any]]
    competitor_prices: List[float]
    sales_report: Dict[str, Any]
    trend_report: Dict[str, Any]
    recommendation: Dict[str, Any]
    ai_insights: Dict[str, Any]
    result: Dict[str, Any]


class SalesAnalysisWorkflow(BaseWorkflow):
    """Analyze sales and return actionable recommendation."""

    def __init__(self):
        super().__init__()
        self.analytics_agent = AnalyticsAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(SalesAnalysisState)
        workflow.add_node("load_sales_data", self._load_sales_data)
        workflow.add_node("analyze_sales", self._analyze_sales)
        workflow.add_node("detect_trends", self._detect_trends)
        workflow.add_node("recommend_action", self._recommend_action)
        workflow.add_node("format_result", self._format_result)

        workflow.set_entry_point("load_sales_data")
        workflow.add_edge("load_sales_data", "analyze_sales")
        workflow.add_edge("analyze_sales", "detect_trends")
        workflow.add_edge("detect_trends", "recommend_action")
        workflow.add_edge("recommend_action", "format_result")
        workflow.add_edge("format_result", END)
        return workflow.compile()

    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        self.log_step("start", {"workflow_id": workflow_id, "shop_id": shop_id})

        initial_state: SalesAnalysisState = {
            "workflow_id": workflow_id,
            "shop_id": shop_id or context.get("shop_id"),
            "days_back": int(context.get("days_back", 14)),
            "sales_data": list(context.get("sales_data", [])),
            "competitor_prices": list(context.get("competitor_prices", [])),
            "sales_report": {},
            "trend_report": {},
            "recommendation": {},
            "ai_insights": {},
            "result": {},
        }

        final_state = await self.graph.ainvoke(initial_state)
        self.log_step("complete", {"workflow_id": workflow_id})
        return final_state["result"]

    async def _load_sales_data(self, state: SalesAnalysisState) -> SalesAnalysisState:
        """Load recent sales either from context or from repository."""
        if state["sales_data"]:
            return state

        if not state["shop_id"]:
            return state

        date_to = datetime.utcnow()
        date_from = date_to - timedelta(days=state["days_back"])

        async with db_manager.get_async_session() as db:
            sales = await sale_repository.get_by_date_range(
                db=db,
                shop_id=state["shop_id"],
                date_from=date_from,
                date_to=date_to,
            )

        state["sales_data"] = [
            {
                "sale_id": item.sale_id,
                "product_id": item.product_id,
                "sale_date": item.sale_date.isoformat() if item.sale_date else None,
                "quantity": int(item.quantity or 0),
                "total_price": float(item.total_price or 0),
            }
            for item in sales
        ]
        logger.info("Loaded %s sales records for workflow %s", len(state["sales_data"]), state["workflow_id"])
        return state

    async def _analyze_sales(self, state: SalesAnalysisState) -> SalesAnalysisState:
        state["sales_report"] = self.analytics_agent.analyze_sales(
            sales_data=state["sales_data"],
            period_days=state["days_back"],
        )
        return state

    async def _detect_trends(self, state: SalesAnalysisState) -> SalesAnalysisState:
        state["trend_report"] = self.analytics_agent.detect_trends(state["sales_data"])
        return state

    async def _recommend_action(self, state: SalesAnalysisState) -> SalesAnalysisState:
        trend = state["trend_report"].get("trend", "unknown")
        total_revenue = state["sales_report"].get("total_revenue", 0.0)
        delta = state["trend_report"].get("change_pct", 0.0)

        if trend == "declining":
            recommendation = {
                "priority": "high",
                "action": "start_sales_drop_investigation",
                "reason": f"Revenue trend declining by {delta}%",
            }
        elif trend == "growing":
            recommendation = {
                "priority": "medium",
                "action": "increase_inventory_buffer",
                "reason": f"Revenue trend growing by {delta}%",
            }
        else:
            recommendation = {
                "priority": "low",
                "action": "keep_current_strategy",
                "reason": "Sales trend is stable",
            }

        recommendation["current_revenue"] = total_revenue
        state["recommendation"] = recommendation

        # Stage 8: optionally add AI narrative for operator.
        try:
            ai_result = await ai_service.generate_text(
                prompt=(
                    "На основе данных сформулируй 3 короткие практические рекомендации для продавца WB. "
                    f"Sales report: {state['sales_report']}. Trend: {state['trend_report']}."
                ),
                system_prompt=(
                    "Ты аналитик e-commerce. "
                    "Пиши конкретные действия, без общих фраз."
                ),
                temperature=0.2,
                max_tokens=220,
            )
            state["ai_insights"] = ai_result
        except Exception as exc:
            state["ai_insights"] = {
                "status": "fallback_to_rule_based",
                "error": str(exc),
            }
        return state

    async def _format_result(self, state: SalesAnalysisState) -> SalesAnalysisState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "sales_analysis_workflow",
            "shop_id": state["shop_id"],
            "sales_count": len(state["sales_data"]),
            "sales_report": state["sales_report"],
            "trend_report": state["trend_report"],
            "recommendation": state["recommendation"],
            "ai_insights": state["ai_insights"],
            "status": "completed",
        }
        return state
