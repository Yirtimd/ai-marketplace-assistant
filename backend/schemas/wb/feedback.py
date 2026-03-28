"""
Feedback and question schemas for Wildberries API
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FeedbackAnswer(BaseModel):
    """Feedback answer"""
    text: str
    createdAt: datetime


class Feedback(BaseModel):
    """Customer feedback (review)"""
    id: str
    nmId: int
    text: str
    rating: int
    createdAt: datetime
    isAnswered: bool
    answer: Optional[FeedbackAnswer] = None
    userName: str = "Покупатель"


class FeedbacksListResponse(BaseModel):
    """Response for feedbacks list"""
    data: list[Feedback]
    countUnanswered: int
    countArchive: int


class AnswerFeedbackRequest(BaseModel):
    """Request to answer a feedback"""
    text: str


class Question(BaseModel):
    """Customer question"""
    id: str
    nmId: int
    text: str
    createdAt: datetime
    isAnswered: bool
    answer: Optional[str] = None
    userName: str = "Покупатель"


class QuestionsListResponse(BaseModel):
    """Response for questions list"""
    data: list[Question]
    countUnanswered: int


class AnswerQuestionRequest(BaseModel):
    """Request to answer a question"""
    answer: str
