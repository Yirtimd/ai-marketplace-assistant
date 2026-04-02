"""
Wildberries Services Module

Provides modular access to Wildberries API services.
"""

from .base import WBBaseService
from .exceptions import (
    WildberriesServiceError,
    WildberriesAuthError,
    WildberriesAPIError,
    WildberriesRateLimitError,
    WildberriesNotFoundError
)
from .products import WBProductsService
from .feedbacks import WBFeedbacksService
from .sales import WBSalesService
from .normalizer import (
    extract_products,
    extract_sales,
    extract_feedbacks,
    normalize_sale_record,
    normalize_feedback_record,
)

__all__ = [
    "WBBaseService",
    "WBProductsService",
    "WBFeedbacksService",
    "WBSalesService",
    "extract_products",
    "extract_sales",
    "extract_feedbacks",
    "normalize_sale_record",
    "normalize_feedback_record",
    "WildberriesServiceError",
    "WildberriesAuthError",
    "WildberriesAPIError",
    "WildberriesRateLimitError",
    "WildberriesNotFoundError",
]
