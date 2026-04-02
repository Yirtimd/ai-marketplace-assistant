"""
Action Execution Workflow

LangGraph workflow that executes marketplace actions through ActionService.
"""

from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph

from services import action_service
from workflows.base import BaseWorkflow


class ActionExecutionState(TypedDict):
    workflow_id: str
    operation: str
    params: Dict[str, Any]
    output: Dict[str, Any]
    result: Dict[str, Any]


class ActionExecutionWorkflow(BaseWorkflow):
    """Single entry workflow for direct action execution operations."""

    def __init__(self):
        super().__init__()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ActionExecutionState)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("format_result", self._format_result)
        workflow.set_entry_point("execute_action")
        workflow.add_edge("execute_action", "format_result")
        workflow.add_edge("format_result", END)
        return workflow.compile()

    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        params = dict(context.get("params", {}))
        if shop_id is not None and "shop_id" not in params:
            params["shop_id"] = shop_id

        initial_state: ActionExecutionState = {
            "workflow_id": workflow_id,
            "operation": str(context.get("operation", "")),
            "params": params,
            "output": {},
            "result": {},
        }
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _execute_action(self, state: ActionExecutionState) -> ActionExecutionState:
        operation = state["operation"]
        params = state["params"]

        if operation == "update_price":
            state["output"] = await action_service.update_price(
                shop_id=params.get("shop_id"),
                nm_id=int(params.get("nm_id")),
                new_price=float(params.get("new_price")),
                reason=params.get("reason"),
                discount=params.get("discount"),
            )
            return state

        if operation == "create_product_card":
            state["output"] = await action_service.create_product_card(
                shop_id=params.get("shop_id"),
                card_payload=dict(params.get("card_payload", {})),
            )
            return state

        if operation == "reply_to_review":
            state["output"] = await action_service.reply_to_review(
                shop_id=params.get("shop_id"),
                review_id=str(params.get("review_id")),
                reply_text=str(params.get("reply_text", "")),
            )
            return state

        raise ValueError(f"Unsupported action operation: {operation}")

    async def _format_result(self, state: ActionExecutionState) -> ActionExecutionState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "action_execution_workflow",
            "operation": state["operation"],
            "output": state["output"],
            "status": "completed",
        }
        return state

