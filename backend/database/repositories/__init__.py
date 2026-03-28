"""
Repositories Module

Exports all repositories for easy import.
"""

from .base import BaseRepository
from .product import ProductRepository, product_repository
from .sale import SaleRepository, sale_repository
from .review import ReviewRepository, review_repository
from .shop import ShopRepository, shop_repository
from .price_history import PriceHistoryRepository, price_history_repository
from .stock_history import StockHistoryRepository, stock_history_repository
from .rating_history import RatingHistoryRepository, rating_history_repository
from .task_execution import TaskExecutionRepository, task_execution_repository
from .workflow_state import WorkflowStateRepository, workflow_state_repository

__all__ = [
    "BaseRepository",
    "ProductRepository",
    "product_repository",
    "SaleRepository",
    "sale_repository",
    "ReviewRepository",
    "review_repository",
    "ShopRepository",
    "shop_repository",
    "PriceHistoryRepository",
    "price_history_repository",
    "StockHistoryRepository",
    "stock_history_repository",
    "RatingHistoryRepository",
    "rating_history_repository",
    "TaskExecutionRepository",
    "task_execution_repository",
    "WorkflowStateRepository",
    "workflow_state_repository",
]
