"""
Standalone models for Alembic migrations

This file contains all models in a single location to avoid circular imports.
"""

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, Numeric, JSON, Enum as SQLEnum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Shop(Base):
    """Shop model"""
    __tablename__ = "shops"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    wb_api_key: Mapped[str] = mapped_column(String(512), nullable=False)
    wb_supplier_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Product(Base):
    """Product model - UPDATED with analytics fields"""
    __tablename__ = "products"
    
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    nm_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    imt_id: Mapped[int] = mapped_column(Integer, nullable=True)
    vendor_code: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    subject_name: Mapped[str] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Current pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Current rating
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=True)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Inventory tracking (NEW)
    current_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_in_warehouse: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_in_transit: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Analytics fields (NEW)
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversion_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Status (NEW)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # JSON fields
    sizes: Mapped[dict] = mapped_column(JSON, nullable=True)
    photos: Mapped[dict] = mapped_column(JSON, nullable=True)
    characteristics: Mapped[dict] = mapped_column(JSON, nullable=True)


class Sale(Base):
    """Sale model - UPDATED with financial fields"""
    __tablename__ = "sales"
    
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sale_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    order_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nm_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    vendor_code: Mapped[str] = mapped_column(String(255), nullable=False)
    sale_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Financial analytics (NEW)
    commission_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    commission_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    net_revenue: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Returns tracking (NEW)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    return_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Geography
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=True)
    oblast: Mapped[str] = mapped_column(String(255), nullable=True)
    region: Mapped[str] = mapped_column(String(255), nullable=True)


class Review(Base):
    """Review model"""
    __tablename__ = "reviews"
    
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    wb_feedback_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    nm_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    user_name: Mapped[str] = mapped_column(String(255), default="Покупатель", nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_answered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=True, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    priority: Mapped[str] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    celery_task_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)


class EventType(str, Enum):
    """Event type enum"""
    SYSTEM = "system"
    USER_ACTION = "user_action"
    DATA_SYNC = "data_sync"
    AGENT_ACTION = "agent_action"
    NOTIFICATION = "notification"
    ERROR = "error"


class EventLevel(str, Enum):
    """Event severity level"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Event(Base):
    """Event model"""
    __tablename__ = "events"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(SQLEnum(EventType), default=EventType.SYSTEM, nullable=False, index=True)
    event_level: Mapped[str] = mapped_column(SQLEnum(EventLevel), default=EventLevel.INFO, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class WorkflowStatus(str, Enum):
    """Workflow status enum"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(Base):
    """WorkflowState model"""
    __tablename__ = "workflow_states"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    workflow_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False, index=True)
    current_node: Mapped[str] = mapped_column(String(255), nullable=True)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    error: Mapped[str] = mapped_column(Text, nullable=True)


# NEW: History tables for analytics

class PriceHistory(Base):
    """Price change history for products"""
    __tablename__ = "price_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=True)


class StockHistory(Base):
    """Stock level history for products"""
    __tablename__ = "stock_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_total: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_warehouse: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_in_transit: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=True)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=True)


class RatingHistory(Base):
    """Rating change history for products"""
    __tablename__ = "rating_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
