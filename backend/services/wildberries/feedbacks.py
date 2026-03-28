"""
Wildberries Feedbacks Service

Handles all feedback and questions operations with WB API.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .base import WBBaseService
from backend.config import get_logger

logger = get_logger(__name__)


class WBFeedbacksService(WBBaseService):
    """Service for feedbacks and questions operations"""
    
    async def get_feedbacks(
        self,
        is_answered: Optional[bool] = None,
        take: int = 5000,
        skip: int = 0
    ) -> Dict[str, Any]:
        """Get feedbacks list"""
        logger.info(f"Getting feedbacks: is_answered={is_answered}, take={take}, skip={skip}")
        
        params = {"take": take, "skip": skip}
        if is_answered is not None:
            params["isAnswered"] = is_answered
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/feedbacks",
            params=params
        )
        
        return response
    
    async def get_questions(
        self,
        is_answered: Optional[bool] = None,
        take: int = 5000,
        skip: int = 0
    ) -> Dict[str, Any]:
        """Get questions list"""
        logger.info(f"Getting questions: is_answered={is_answered}, take={take}, skip={skip}")
        
        params = {"take": take, "skip": skip}
        if is_answered is not None:
            params["isAnswered"] = is_answered
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/questions",
            params=params
        )
        
        return response
    
    async def answer_feedback(self, feedback_id: str, text: str) -> Dict[str, Any]:
        """Answer a feedback"""
        logger.info(f"Answering feedback: {feedback_id}")
        
        response = await self._make_request(
            method="PATCH",
            endpoint=f"/api/v1/feedbacks/{feedback_id}/answer",
            json_data={"text": text}
        )
        
        return response
    
    async def answer_question(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Answer a question"""
        logger.info(f"Answering question: {question_id}")
        
        response = await self._make_request(
            method="PATCH",
            endpoint=f"/api/v1/questions/{question_id}/answer",
            json_data={"answer": answer}
        )
        
        return response
    
    async def get_unanswered_feedbacks_count(self) -> Dict[str, int]:
        """Get count of unanswered feedbacks"""
        logger.info("Getting unanswered feedbacks count")
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/feedbacks/count-unanswered"
        )
        
        return response
    
    async def get_unanswered_questions_count(self) -> Dict[str, int]:
        """Get count of unanswered questions"""
        logger.info("Getting unanswered questions count")
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/questions/count-unanswered"
        )
        
        return response
