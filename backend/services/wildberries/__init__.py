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

__all__ = [
    "WBBaseService",
    "WBProductsService",
    "WBFeedbacksService",
    "WBSalesService",
    "WildberriesServiceError",
    "WildberriesAuthError",
    "WildberriesAPIError",
    "WildberriesRateLimitError",
    "WildberriesNotFoundError",
]
