"""
Mock data generator for Wildberries Feedbacks and Questions
"""

from datetime import datetime, timedelta
import random
from typing import List, Optional
from ..models.feedback import (
    Feedback, FeedbackAnswer, Question, QuestionAnswer
)
from .products import MOCK_PRODUCTS


# Positive feedback texts
POSITIVE_TEXTS = [
    "Отличный товар! Очень доволен покупкой.",
    "Качество на высоте, рекомендую!",
    "Быстрая доставка, товар соответствует описанию.",
    "Прекрасное качество, буду заказывать еще!",
    "Все супер! Спасибо продавцу!",
]

# Negative feedback texts
NEGATIVE_TEXTS = [
    "Товар не соответствует описанию.",
    "Качество оставляет желать лучшего.",
    "Пришел бракованный товар.",
    "Разочарован покупкой.",
    "Не рекомендую к покупке.",
]

# Neutral feedback texts
NEUTRAL_TEXTS = [
    "Товар нормальный, за свою цену.",
    "Обычное качество, ничего особенного.",
    "Доставили быстро, качество среднее.",
]

# Questions
QUESTION_TEXTS = [
    "Какой размер подойдет на рост 175см?",
    "Есть ли в наличии другие цвета?",
    "Когда будет доставка?",
    "Можно ли вернуть товар?",
    "Соответствует ли размерной сетке?",
    "Какой состав материала?",
    "Есть ли гарантия на товар?",
]

# Seller answers
ANSWER_TEXTS = [
    "Спасибо за отзыв! Рады, что вам понравилось!",
    "Благодарим за покупку! Будем рады видеть вас снова!",
    "Приносим извинения за неудобства. Свяжитесь с нами для решения вопроса.",
    "Спасибо за обратную связь! Учтем ваши замечания.",
]


def generate_feedbacks(count: int = 100) -> List[Feedback]:
    """Generate mock feedbacks"""
    feedbacks = []
    
    for i in range(1, count + 1):
        product = random.choice(MOCK_PRODUCTS)
        rating = random.randint(1, 5)
        
        # Choose text based on rating
        if rating >= 4:
            text = random.choice(POSITIVE_TEXTS)
        elif rating <= 2:
            text = random.choice(NEGATIVE_TEXTS)
        else:
            text = random.choice(NEUTRAL_TEXTS)
        
        # Some feedbacks have answers
        has_answer = random.random() > 0.5
        answer = FeedbackAnswer(
            text=random.choice(ANSWER_TEXTS),
            editable=True
        ) if has_answer else None
        
        created_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        feedback = Feedback(
            id=f"feedback-{i:06d}",
            nmId=product.nmID,
            imtId=product.imtID,
            productName=product.title,
            productValuation=rating,
            text=text,
            userName=f"Покупатель{i}",
            matchingSize=random.choice(["Маломерит", "Соответствует", "Большемерит"]),
            createdDate=created_date,
            answer=answer,
            isAbleSupplierFeedbackValuation=True,
            supplierFeedbackValuation=random.randint(1, 5) if random.random() > 0.7 else None,
            isAbleSupplierProductValuation=True,
            supplierProductValuation=None,
            photoLinks=[f"https://feedback.wildberries.ru/{i}-{j}.jpg" for j in range(random.randint(0, 3))],
            videoLink=f"https://feedback.wildberries.ru/{i}.mp4" if random.random() > 0.9 else None,
            wasViewed=random.random() > 0.3,
            isAnswered=has_answer,
            state="active"
        )
        
        feedbacks.append(feedback)
    
    return feedbacks


def generate_questions(count: int = 50) -> List[Question]:
    """Generate mock questions"""
    questions = []
    
    for i in range(1, count + 1):
        product = random.choice(MOCK_PRODUCTS)
        
        # Some questions have answers
        has_answer = random.random() > 0.4
        answer = QuestionAnswer(
            text=random.choice([
                "Да, размер соответствует стандартной сетке.",
                "В наличии есть все размеры из описания.",
                "Доставка занимает 3-5 рабочих дней.",
                "Да, можно вернуть в течение 14 дней.",
            ]),
            editable=True
        ) if has_answer else None
        
        created_date = datetime.now() - timedelta(days=random.randint(0, 60))
        
        question = Question(
            id=f"question-{i:06d}",
            nmId=product.nmID,
            productName=product.title,
            text=random.choice(QUESTION_TEXTS),
            userName=f"Покупатель{i + 100}",
            createdDate=created_date,
            answer=answer,
            wasViewed=random.random() > 0.2,
            isAnswered=has_answer,
            state="active"
        )
        
        questions.append(question)
    
    return questions


# Generate mock data
MOCK_FEEDBACKS = generate_feedbacks(100)
MOCK_QUESTIONS = generate_questions(50)


def get_feedbacks(
    is_answered: Optional[bool] = None,
    take: int = 10000,
    skip: int = 0
) -> List[Feedback]:
    """Get feedbacks with filters"""
    feedbacks = MOCK_FEEDBACKS
    
    if is_answered is not None:
        feedbacks = [f for f in feedbacks if f.isAnswered == is_answered]
    
    return feedbacks[skip:skip + take]


def get_feedback_by_id(feedback_id: str) -> Optional[Feedback]:
    """Get feedback by ID"""
    for feedback in MOCK_FEEDBACKS:
        if feedback.id == feedback_id:
            return feedback
    return None


def get_questions(
    is_answered: Optional[bool] = None,
    take: int = 10000,
    skip: int = 0
) -> List[Question]:
    """Get questions with filters"""
    questions = MOCK_QUESTIONS
    
    if is_answered is not None:
        questions = [q for q in questions if q.isAnswered == is_answered]
    
    return questions[skip:skip + take]


def get_question_by_id(question_id: str) -> Optional[Question]:
    """Get question by ID"""
    for question in MOCK_QUESTIONS:
        if question.id == question_id:
            return question
    return None
