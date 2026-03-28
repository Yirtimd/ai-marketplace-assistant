"""
Feedbacks and Questions router for Wildberries Mock API
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from ..models.feedback import (
    Feedback, FeedbackListResponse, FeedbackAnswerRequest,
    Question, QuestionListResponse, QuestionAnswerRequest,
    NewFeedbacksQuestionsResponse
)
from ..data.feedbacks import (
    get_feedbacks, get_feedback_by_id,
    get_questions, get_question_by_id,
    MOCK_FEEDBACKS, MOCK_QUESTIONS
)

router = APIRouter(prefix="/api/v1", tags=["Feedbacks & Questions"])


# ============================================
# Feedbacks
# ============================================

@router.get("/feedbacks", response_model=FeedbackListResponse)
async def get_feedbacks_list(
    authorization: str = Header(..., description="Bearer token"),
    is_answered: Optional[bool] = Query(None, description="Filter by answered status"),
    take: int = Query(10000, ge=1, le=10000),
    skip: int = Query(0, ge=0)
):
    """
    Get list of feedbacks
    
    Получить список отзывов
    """
    feedbacks = get_feedbacks(is_answered=is_answered, take=take, skip=skip)
    
    unanswered_count = len([f for f in MOCK_FEEDBACKS if not f.isAnswered])
    archived_count = len([f for f in MOCK_FEEDBACKS if f.state == "archived"])
    
    return FeedbackListResponse(
        data={"total": len(feedbacks)},
        feedbacks=feedbacks,
        countUnanswered=unanswered_count,
        countArchive=archived_count
    )


@router.get("/feedback", response_model=Feedback)
async def get_feedback(
    authorization: str = Header(..., description="Bearer token"),
    id: str = Query(..., description="Feedback ID")
):
    """
    Get feedback by ID
    
    Получить отзыв по ID
    """
    feedback = get_feedback_by_id(id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback


@router.get("/feedbacks/count")
async def get_feedbacks_count(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get total number of feedbacks
    
    Получить общее количество отзывов
    """
    return {
        "data": {},
        "countFeedbacks": len(MOCK_FEEDBACKS)
    }


@router.get("/feedbacks/count-unanswered")
async def get_unanswered_feedbacks_count(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get number of unanswered feedbacks
    
    Получить количество неотвеченных отзывов
    """
    unanswered = len([f for f in MOCK_FEEDBACKS if not f.isAnswered])
    
    return {
        "data": {},
        "countUnanswered": unanswered
    }


@router.post("/feedbacks/answer")
async def answer_feedback(
    request: FeedbackAnswerRequest,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Reply to feedback
    
    Ответить на отзыв
    """
    feedback = get_feedback_by_id(request.id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return {
        "data": {},
        "error": False,
        "errorText": "",
        "message": "Answer posted successfully (mock)"
    }


@router.patch("/feedbacks/answer")
async def edit_feedback_answer(
    request: FeedbackAnswerRequest,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Edit response to feedback
    
    Редактировать ответ на отзыв
    """
    feedback = get_feedback_by_id(request.id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return {
        "data": {},
        "error": False,
        "errorText": "",
        "message": "Answer updated successfully (mock)"
    }


# ============================================
# Questions
# ============================================

@router.get("/questions", response_model=QuestionListResponse)
async def get_questions_list(
    authorization: str = Header(..., description="Bearer token"),
    is_answered: Optional[bool] = Query(None, description="Filter by answered status"),
    take: int = Query(10000, ge=1, le=10000),
    skip: int = Query(0, ge=0)
):
    """
    Get list of questions
    
    Получить список вопросов
    """
    questions = get_questions(is_answered=is_answered, take=take, skip=skip)
    
    unanswered_count = len([q for q in MOCK_QUESTIONS if not q.isAnswered])
    
    return QuestionListResponse(
        data={"total": len(questions)},
        questions=questions,
        countUnanswered=unanswered_count
    )


@router.get("/question", response_model=Question)
async def get_question(
    authorization: str = Header(..., description="Bearer token"),
    id: str = Query(..., description="Question ID")
):
    """
    Get question by ID
    
    Получить вопрос по ID
    """
    question = get_question_by_id(id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.get("/questions/count")
async def get_questions_count(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get total number of questions
    
    Получить общее количество вопросов
    """
    return {
        "data": {},
        "countQuestions": len(MOCK_QUESTIONS)
    }


@router.get("/questions/count-unanswered")
async def get_unanswered_questions_count(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get number of unanswered questions
    
    Получить количество неотвеченных вопросов
    """
    unanswered = len([q for q in MOCK_QUESTIONS if not q.isAnswered])
    
    return {
        "data": {},
        "countUnanswered": unanswered
    }


@router.patch("/questions")
async def answer_question(
    request: QuestionAnswerRequest,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Answer question
    
    Ответить на вопрос
    """
    question = get_question_by_id(request.id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {
        "data": {},
        "error": False,
        "errorText": "",
        "message": "Answer posted successfully (mock)"
    }


# ============================================
# Combined
# ============================================

@router.get("/new-feedbacks-questions", response_model=NewFeedbacksQuestionsResponse)
async def get_new_feedbacks_questions(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get unseen feedbacks and questions count
    
    Получить количество непросмотренных отзывов и вопросов
    """
    unanswered_feedbacks = len([f for f in MOCK_FEEDBACKS if not f.isAnswered])
    unanswered_questions = len([q for q in MOCK_QUESTIONS if not q.isAnswered])
    
    has_new_feedbacks = len([f for f in MOCK_FEEDBACKS if not f.wasViewed]) > 0
    has_new_questions = len([q for q in MOCK_QUESTIONS if not q.wasViewed]) > 0
    
    return NewFeedbacksQuestionsResponse(
        data={},
        countUnansweredFeedbacks=unanswered_feedbacks,
        countUnansweredQuestions=unanswered_questions,
        hasNewFeedbacks=has_new_feedbacks,
        hasNewQuestions=has_new_questions
    )
