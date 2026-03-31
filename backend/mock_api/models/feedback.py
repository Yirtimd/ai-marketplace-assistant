"""
Pydantic models for Wildberries Feedbacks and Questions API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Feedback(BaseModel):
    """Customer feedback model"""
    id: str = Field(..., description="Feedback ID")
    nmId: int = Field(..., description="Nomenclature ID")
    imtId: int = Field(..., description="IMT ID")
    productName: str = Field(..., description="Product name")
    productValuation: int = Field(..., ge=1, le=5, description="Product rating (1-5)")
    text: str = Field(..., description="Feedback text")
    userName: str = Field(..., description="User name")
    matchingSize: str = Field(..., description="Size matching")
    createdDate: datetime = Field(..., description="Created date")
    answer: Optional["FeedbackAnswer"] = Field(None, description="Seller's answer")
    isAbleSupplierFeedbackValuation: bool = Field(True, description="Can rate feedback")
    supplierFeedbackValuation: Optional[int] = Field(None, description="Supplier rating")
    isAbleSupplierProductValuation: bool = Field(True, description="Can rate product")
    supplierProductValuation: Optional[int] = Field(None, description="Supplier product rating")
    photoLinks: List[str] = Field(default_factory=list, description="Photo URLs")
    videoLink: Optional[str] = Field(None, description="Video URL")
    wasViewed: bool = Field(False, description="Was viewed by seller")
    isAnswered: bool = Field(False, description="Has answer")
    state: str = Field("active", description="Feedback state: active/archived")


class FeedbackAnswer(BaseModel):
    """Seller's answer to feedback"""
    text: str = Field(..., description="Answer text")
    editable: bool = Field(True, description="Can be edited")


class FeedbackListResponse(BaseModel):
    """Response for feedbacks list"""
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    feedbacks: List[Feedback] = Field(default_factory=list, description="Feedbacks list")
    countUnanswered: int = Field(0, description="Count of unanswered feedbacks")
    countArchive: int = Field(0, description="Count of archived feedbacks")


class FeedbackAnswerRequest(BaseModel):
    """Request for answering feedback"""
    id: str = Field(..., description="Feedback ID")
    text: str = Field(..., min_length=1, max_length=1000, description="Answer text")


class Question(BaseModel):
    """Customer question model"""
    id: str = Field(..., description="Question ID")
    nmId: int = Field(..., description="Nomenclature ID")
    productName: str = Field(..., description="Product name")
    text: str = Field(..., description="Question text")
    userName: str = Field(..., description="User name")
    createdDate: datetime = Field(..., description="Created date")
    answer: Optional["QuestionAnswer"] = Field(None, description="Seller's answer")
    wasViewed: bool = Field(False, description="Was viewed by seller")
    isAnswered: bool = Field(False, description="Has answer")
    state: str = Field("active", description="Question state")


class QuestionAnswer(BaseModel):
    """Seller's answer to question"""
    text: str = Field(..., description="Answer text")
    editable: bool = Field(True, description="Can be edited")


class QuestionListResponse(BaseModel):
    """Response for questions list"""
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    questions: List[Question] = Field(default_factory=list, description="Questions list")
    countUnanswered: int = Field(0, description="Count of unanswered questions")


class QuestionAnswerRequest(BaseModel):
    """Request for answering question"""
    id: str = Field(..., description="Question ID")
    text: str = Field(..., min_length=1, max_length=1000, description="Answer text")


class NewFeedbacksQuestionsResponse(BaseModel):
    """Response for new feedbacks and questions count"""
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    countUnansweredFeedbacks: int = Field(0, description="Unanswered feedbacks count")
    countUnansweredQuestions: int = Field(0, description="Unanswered questions count")
    hasNewFeedbacks: bool = Field(False, description="Has new feedbacks")
    hasNewQuestions: bool = Field(False, description="Has new questions")


# Update forward references
Feedback.model_rebuild()
Question.model_rebuild()
