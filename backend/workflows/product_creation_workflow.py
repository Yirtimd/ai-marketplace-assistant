"""
Product Creation Workflow

LangGraph workflow for AI-assisted product card preparation.
"""

from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents import ContentAgent
from services import ai_service, action_service
from workflows.base import BaseWorkflow


class ProductCreationState(TypedDict):
    workflow_id: str
    execute_action: bool
    product_data: Dict[str, Any]
    description_payload: Dict[str, Any]
    image_payload: Dict[str, Any]
    video_payload: Dict[str, Any]
    seo_payload: Dict[str, Any]
    ai_description_payload: Dict[str, Any]
    card_payload: Dict[str, Any]
    action_result: Dict[str, Any]
    result: Dict[str, Any]


class ProductCreationWorkflow(BaseWorkflow):
    """Generate product content artifacts through staged graph execution."""

    def __init__(self):
        super().__init__()
        self.content_agent = ContentAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ProductCreationState)
        workflow.add_node("generate_description", self._generate_description)
        workflow.add_node("generate_images", self._generate_images)
        workflow.add_node("generate_video", self._generate_video)
        workflow.add_node("seo_optimization", self._seo_optimization)
        workflow.add_node("create_product_card", self._create_product_card_payload)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("format_result", self._format_result)

        workflow.set_entry_point("generate_description")
        workflow.add_edge("generate_description", "generate_images")
        workflow.add_edge("generate_images", "generate_video")
        workflow.add_edge("generate_video", "seo_optimization")
        workflow.add_edge("seo_optimization", "create_product_card")
        workflow.add_edge("create_product_card", "execute_action")
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
        initial_state: ProductCreationState = {
            "workflow_id": workflow_id,
            "execute_action": bool(context.get("execute_action", False)),
            "product_data": dict(context.get("product_data", {})),
            "description_payload": {},
            "image_payload": {},
            "video_payload": {},
            "seo_payload": {},
            "ai_description_payload": {},
            "card_payload": {},
            "action_result": {},
            "result": {},
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _generate_description(self, state: ProductCreationState) -> ProductCreationState:
        state["description_payload"] = self.content_agent.generate_product_description(state["product_data"])

        # Stage 8: improve deterministic draft via AI service when provider is configured.
        try:
            ai_result = await ai_service.generate_text(
                prompt=(
                    "Сгенерируй продающее описание товара для маркетплейса на русском языке. "
                    "Сделай 1 абзац + 4-6 коротких преимуществ. "
                    f"Данные товара: {state['product_data']}"
                ),
                system_prompt=(
                    "Ты e-commerce копирайтер. Пиши конкретно, без воды и без выдуманных фактов. "
                    "Не используй запрещенные медицинские/гарантийные обещания."
                ),
                temperature=0.4,
                max_tokens=700,
            )
            state["ai_description_payload"] = ai_result
            ai_text = (ai_result.get("text") or "").strip()
            if ai_text:
                state["description_payload"]["description"] = ai_text
                state["description_payload"]["generated_by"] = ai_result.get("provider", "ai")
        except Exception as exc:
            state["ai_description_payload"] = {
                "status": "fallback_to_agent",
                "error": str(exc),
            }
        return state

    async def _generate_images(self, state: ProductCreationState) -> ProductCreationState:
        base_payload = self.content_agent.generate_product_images(state["product_data"])
        state["image_payload"] = await ai_service.generate_images(
            prompt=base_payload.get("prompt", ""),
            size="1024x1024",
            quality="standard",
        )
        if state["image_payload"].get("status") != "completed":
            # Keep deterministic payload as fallback for external workers.
            state["image_payload"]["fallback_payload"] = base_payload
        return state

    async def _generate_video(self, state: ProductCreationState) -> ProductCreationState:
        base_payload = self.content_agent.generate_product_video(state["product_data"])
        state["video_payload"] = await ai_service.generate_video(
            prompt=base_payload.get("prompt", ""),
            duration_seconds=15,
        )
        state["video_payload"]["fallback_payload"] = base_payload
        return state

    async def _seo_optimization(self, state: ProductCreationState) -> ProductCreationState:
        keywords = list(state["product_data"].get("keywords", []))
        state["seo_payload"] = self.content_agent.optimize_seo(
            title=state["description_payload"].get("title", state["product_data"].get("title", "")),
            description=state["description_payload"].get("description", ""),
            keywords=keywords,
        )
        return state

    async def _create_product_card_payload(self, state: ProductCreationState) -> ProductCreationState:
        state["card_payload"] = {
            "title": state["seo_payload"].get("seo_title", state["description_payload"].get("title")),
            "description": state["seo_payload"].get(
                "seo_description",
                state["description_payload"].get("description"),
            ),
            "bullets": state["description_payload"].get("bullets", []),
            "media_tasks": [state["image_payload"], state["video_payload"]],
            "status": "ready_for_action_layer",
        }
        return state

    async def _execute_action(self, state: ProductCreationState) -> ProductCreationState:
        if not state["execute_action"]:
            state["action_result"] = {"status": "skipped", "reason": "execute_action=false"}
            return state

        try:
            state["action_result"] = await action_service.create_product_card(
                card_payload=state["card_payload"]
            )
        except Exception as exc:
            state["action_result"] = {"status": "failed", "error": str(exc)}
        return state

    async def _format_result(self, state: ProductCreationState) -> ProductCreationState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "product_creation_workflow",
            "description_payload": state["description_payload"],
            "ai_description_payload": state["ai_description_payload"],
            "image_payload": state["image_payload"],
            "video_payload": state["video_payload"],
            "seo_payload": state["seo_payload"],
            "card_payload": state["card_payload"],
            "action_result": state["action_result"],
            "status": "completed",
        }
        return state
