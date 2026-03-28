"""
TaskExecution model for tracking task execution history and metrics
"""

from sqlalchemy import String, Integer, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class TaskExecution(Base):
    """
    TaskExecution model - tracks Celery task execution history
    
    Stores metrics, status, and error details for monitoring and analytics.
    """
    __tablename__ = "task_executions"
    
    # Task identification
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Context
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        default="pending"
    )  # pending, running, success, failed, skipped
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Metrics
    records_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error details
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    error_type: Mapped[str] = mapped_column(String(255), nullable=True)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Result data
    result_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    input_params: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Relationships
    shop: Mapped["Shop"] = relationship("Shop", foreign_keys=[shop_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<TaskExecution(id={self.id}, task_name={self.task_name}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "shop_id": self.shop_id,
            "user_id": self.user_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "metrics": {
                "created": self.records_created,
                "updated": self.records_updated,
                "skipped": self.records_skipped,
                "failed": self.records_failed,
                "total": self.records_total
            },
            "error": {
                "message": self.error_message,
                "type": self.error_type,
                "retry_count": self.retry_count
            } if self.error_message else None,
            "result_data": self.result_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
