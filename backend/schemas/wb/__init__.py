"""
Wildberries API schemas

Modular organization of Pydantic schemas for Wildberries data.
"""

from .common import Category, Subject, Brand
from .product import (
    ProductSize,
    ProductPhoto,
    ProductCharacteristic,
    Product,
    ProductsListResponse
)
from .feedback import (
    FeedbackAnswer,
    Feedback,
    FeedbacksListResponse,
    AnswerFeedbackRequest,
    Question,
    QuestionsListResponse,
    AnswerQuestionRequest
)
from .sale import (
    Sale,
    SalesListResponse,
    Order,
    OrdersListResponse,
    Stock,
    StocksListResponse
)

__all__ = [
    # Common
    "Category",
    "Subject",
    "Brand",
    # Products
    "ProductSize",
    "ProductPhoto",
    "ProductCharacteristic",
    "Product",
    "ProductsListResponse",
    # Feedbacks
    "FeedbackAnswer",
    "Feedback",
    "FeedbacksListResponse",
    "AnswerFeedbackRequest",
    "Question",
    "QuestionsListResponse",
    "AnswerQuestionRequest",
    # Sales
    "Sale",
    "SalesListResponse",
    "Order",
    "OrdersListResponse",
    "Stock",
    "StocksListResponse",
]
