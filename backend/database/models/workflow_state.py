"""
Workflow State model for orchestrator state management
"""

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from backend.database.base import Base


class WorkflowStatus(str, Enum):
    """Workflow status enum"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(Base):
    """WorkflowState model - stores state for LangGraph workflows"""
    __tablename__ = "workflow_states"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=True, index=True)
    
    workflow_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    workflow_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    status: Mapped[str] = mapped_column(
        SQLEnum(WorkflowStatus),
        default=WorkflowStatus.PENDING,
        nullable=False,
        index=True
    )
    
    current_node: Mapped[str] = mapped_column(String(255), nullable=True)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    input_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    error: Mapped[str] = mapped_column(Text, nullable=True)
    
    user: Mapped["User"] = relationship("User")
    shop: Mapped["Shop"] = relationship("Shop")
    
    def __repr__(self) -> str:
        return f"<WorkflowState(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"
