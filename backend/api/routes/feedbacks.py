"""
Feedbacks and Questions routes for Wildberries data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.config.dependencies import get_wb_feedbacks_service
from backend.services.wildberries import WBFeedbacksService, WildberriesServiceError
from backend.schemas.wb import (
    FeedbacksListResponse, Feedback, AnswerFeedbackRequest,
    QuestionsListResponse, Question, AnswerQuestionRequest
)

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks & Questions"])


# ============================================
# Feedbacks
# ============================================

@router.get("/", response_model=FeedbacksListResponse)
async def get_feedbacks(
    is_answered: Optional[bool] = Query(None, description="Filter by answered status"),
    take: int = Query(10000, ge=1, le=10000, description="Maximum number of feedbacks"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Get list of customer feedbacks
    
    Returns paginated list of feedbacks with optional filtering.
    """
    try:
        data = await wb.get_feedbacks(is_answered=is_answered, take=take, skip=skip)
        return FeedbacksListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{feedback_id}", response_model=Feedback)
async def get_feedback_by_id(
    feedback_id: str,
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Get feedback by ID
    
    Returns detailed information about a specific feedback.
    """
    try:
        data = await wb.get_feedback_by_id(feedback_id)
        return Feedback(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{feedback_id}/answer")
async def answer_feedback(
    feedback_id: str,
    request: AnswerFeedbackRequest,
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Reply to customer feedback
    
    Posts an answer to a customer's feedback.
    """
    try:
        result = await wb.answer_feedback(feedback_id, request.text)
        return {"success": True, "data": result}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/unanswered")
async def get_unanswered_feedbacks_count(
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Get count of unanswered feedbacks
    
    Returns the number of feedbacks that haven't been answered yet.
    """
    try:
        count = await wb.get_unanswered_feedbacks_count()
        return {"countUnanswered": count}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Questions
# ============================================

@router.get("/questions", response_model=QuestionsListResponse)
async def get_questions(
    is_answered: Optional[bool] = Query(None, description="Filter by answered status"),
    take: int = Query(10000, ge=1, le=10000, description="Maximum number of questions"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Get list of customer questions
    
    Returns paginated list of questions with optional filtering.
    """
    try:
        data = await wb.get_questions(is_answered=is_answered, take=take, skip=skip)
        return QuestionsListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/answer")
async def answer_question(
    question_id: str,
    request: AnswerQuestionRequest,
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Answer customer question
    
    Posts an answer to a customer's question.
    """
    try:
        result = await wb.answer_question(question_id, request.text)
        return {"success": True, "data": result}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/new")
async def get_new_feedbacks_questions(
    wb: WBFeedbacksService = Depends(get_wb_feedbacks_service)
):
    """
    Get counts of new feedbacks and questions
    
    Returns the number of new/unseen feedbacks and questions.
    """
    try:
        data = await wb.get_new_feedbacks_questions()
        return data
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
