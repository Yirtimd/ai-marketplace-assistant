"""
AI Generation Workflow

LangGraph workflow that routes generation requests to AI service.
"""

from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph

from services import ai_service
from workflows.base import BaseWorkflow


class AIGenerationState(TypedDict):
    workflow_id: str
    operation: str
    params: Dict[str, Any]
    output: Dict[str, Any]
    result: Dict[str, Any]


class AIGenerationWorkflow(BaseWorkflow):
    """Single entry workflow for direct AI generation operations."""

    def __init__(self):
        super().__init__()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AIGenerationState)
        workflow.add_node("execute_generation", self._execute_generation)
        workflow.add_node("format_result", self._format_result)
        workflow.set_entry_point("execute_generation")
        workflow.add_edge("execute_generation", "format_result")
        workflow.add_edge("format_result", END)
        return workflow.compile()

    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        initial_state: AIGenerationState = {
            "workflow_id": workflow_id,
            "operation": str(context.get("operation", "")),
            "params": dict(context.get("params", {})),
            "output": {},
            "result": {},
        }
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _execute_generation(self, state: AIGenerationState) -> AIGenerationState:
        operation = state["operation"]
        params = state["params"]

        if operation == "generate_text":
            state["output"] = await ai_service.generate_text(
                prompt=params.get("prompt", ""),
                system_prompt=params.get("system_prompt"),
                model=params.get("model"),
                temperature=float(params.get("temperature", 0.3)),
                max_tokens=int(params.get("max_tokens", 700)),
            )
            return state

        if operation == "generate_image":
            state["output"] = await ai_service.generate_images(
                prompt=params.get("prompt", ""),
                size=params.get("size", "1024x1024"),
                quality=params.get("quality", "standard"),
            )
            return state

        if operation == "generate_video":
            state["output"] = await ai_service.generate_video(
                prompt=params.get("prompt", ""),
                duration_seconds=int(params.get("duration_seconds", 15)),
            )
            return state

        raise ValueError(f"Unsupported AI generation operation: {operation}")

    async def _format_result(self, state: AIGenerationState) -> AIGenerationState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "ai_generation_workflow",
            "operation": state["operation"],
            "output": state["output"],
            "status": "completed",
        }
        return state

