"""
Review Workflow

LangGraph workflow for review sentiment analysis and reply generation.
"""

from datetime import datetime
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agents import ReviewAgent
from database import db_manager
from database.repositories import review_repository
from services import ai_service, action_service
from workflows.base import BaseWorkflow


class ReviewState(TypedDict):
    workflow_id: str
    shop_id: Optional[int]
    execute_action: bool
    review_id: Optional[int]
    review_payload: Dict[str, Any]
    sentiment_payload: Dict[str, Any]
    ai_reply_payload: Dict[str, Any]
    reply_text: str
    moderation_passed: bool
    publish_payload: Dict[str, Any]
    action_result: Dict[str, Any]
    result: Dict[str, Any]


class ReviewWorkflow(BaseWorkflow):
    """Handle review processing from loading to reply payload."""

    def __init__(self):
        super().__init__()
        self.review_agent = ReviewAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ReviewState)
        workflow.add_node("load_review", self._load_review)
        workflow.add_node("sentiment_analysis", self._sentiment_analysis)
        workflow.add_node("generate_reply", self._generate_reply)
        workflow.add_node("moderation_check", self._moderation_check)
        workflow.add_node("publish_reply", self._publish_reply)
        workflow.add_node("execute_marketplace_action", self._execute_action)
        workflow.add_node("format_result", self._format_result)

        workflow.set_entry_point("load_review")
        workflow.add_edge("load_review", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", "generate_reply")
        workflow.add_edge("generate_reply", "moderation_check")
        workflow.add_edge("moderation_check", "publish_reply")
        workflow.add_edge("publish_reply", "execute_marketplace_action")
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
        initial_state: ReviewState = {
            "workflow_id": workflow_id,
            "shop_id": shop_id or context.get("shop_id"),
            "execute_action": bool(context.get("execute_action", False)),
            "review_id": context.get("review_id"),
            "review_payload": dict(context.get("review", {})),
            "sentiment_payload": {},
            "ai_reply_payload": {},
            "reply_text": "",
            "moderation_passed": False,
            "publish_payload": {},
            "action_result": {},
            "result": {},
        }

        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]

    async def _load_review(self, state: ReviewState) -> ReviewState:
        """Load review from context first, fallback to DB."""
        if state["review_payload"]:
            return state

        if state["review_id"]:
            async with db_manager.get_async_session() as db:
                review = await review_repository.get_by_id(db, int(state["review_id"]))
            if review:
                state["review_payload"] = {
                    "id": review.id,
                    "text": review.text,
                    "rating": review.rating,
                    "product_name": review.product.title if review.product else None,
                }
                return state

        if state["shop_id"]:
            async with db_manager.get_async_session() as db:
                unanswered = await review_repository.get_unanswered(
                    db=db,
                    shop_id=int(state["shop_id"]),
                    skip=0,
                    limit=1,
                )
            if unanswered:
                review = unanswered[0]
                state["review_payload"] = {
                    "id": review.id,
                    "text": review.text,
                    "rating": review.rating,
                    "product_name": review.product.title if review.product else None,
                }

        return state

    async def _sentiment_analysis(self, state: ReviewState) -> ReviewState:
        review_text = state["review_payload"].get("text", "")
        rating = state["review_payload"].get("rating")
        state["sentiment_payload"] = self.review_agent.analyze_sentiment(review_text, rating)
        return state

    async def _generate_reply(self, state: ReviewState) -> ReviewState:
        template_reply = self.review_agent.generate_reply(
            review_text=state["review_payload"].get("text", ""),
            sentiment=state["sentiment_payload"].get("sentiment", "neutral"),
            product_name=state["review_payload"].get("product_name"),
        )

        state["reply_text"] = template_reply

        # Stage 8: refine reply via AI provider while keeping template fallback.
        try:
            ai_result = await ai_service.generate_text(
                prompt=(
                    "Улучши ответ на отзыв клиента для маркетплейса. "
                    "Сохрани вежливый тон, без агрессии и обещаний компенсации. "
                    f"Исходный отзыв: {state['review_payload'].get('text', '')}\n"
                    f"Черновик ответа: {template_reply}"
                ),
                system_prompt=(
                    "Ты специалист клиентского сервиса e-commerce. "
                    "Пиши коротко, корректно и по-деловому."
                ),
                temperature=0.2,
                max_tokens=250,
            )
            state["ai_reply_payload"] = ai_result
            refined = (ai_result.get("text") or "").strip()
            if refined:
                state["reply_text"] = refined
        except Exception as exc:
            state["ai_reply_payload"] = {
                "status": "fallback_to_template",
                "error": str(exc),
            }
        return state

    async def _moderation_check(self, state: ReviewState) -> ReviewState:
        """Simple safety gate before Action Layer."""
        blocked_markers = ["idiot", "stupid", "ненавижу"]
        state["moderation_passed"] = not any(
            marker in state["reply_text"].lower() for marker in blocked_markers
        )
        return state

    async def _publish_reply(self, state: ReviewState) -> ReviewState:
        if not state["moderation_passed"]:
            state["publish_payload"] = {
                "status": "blocked_by_moderation",
                "reply_text": state["reply_text"],
            }
            return state

        review_id = int(state["review_payload"].get("id", 0) or 0)
        if review_id <= 0:
            state["publish_payload"] = {
                "status": "missing_review_id",
                "reply_text": state["reply_text"],
            }
            return state

        state["publish_payload"] = self.review_agent.publish_reply(
            review_id=review_id,
            reply_text=state["reply_text"],
        )
        state["publish_payload"]["prepared_at"] = datetime.utcnow().isoformat()
        return state

    async def _execute_action(self, state: ReviewState) -> ReviewState:
        if not state["execute_action"]:
            state["action_result"] = {"status": "skipped", "reason": "execute_action=false"}
            return state

        if state["publish_payload"].get("status") != "ready_to_publish":
            state["action_result"] = {
                "status": "skipped",
                "reason": "publish_payload_not_ready",
                "publish_payload_status": state["publish_payload"].get("status"),
            }
            return state

        review_id = str(state["publish_payload"].get("review_id"))
        reply_text = state["publish_payload"].get("reply_text", "")

        try:
            state["action_result"] = await action_service.reply_to_review(
                review_id=review_id,
                reply_text=reply_text,
            )
        except Exception as exc:
            state["action_result"] = {"status": "failed", "error": str(exc)}
        return state

    async def _format_result(self, state: ReviewState) -> ReviewState:
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "workflow": "review_workflow",
            "review": state["review_payload"],
            "sentiment": state["sentiment_payload"],
            "ai_reply_payload": state["ai_reply_payload"],
            "reply_text": state["reply_text"],
            "publish_payload": state["publish_payload"],
            "action_result": state["action_result"],
            "status": "completed",
        }
        return state
