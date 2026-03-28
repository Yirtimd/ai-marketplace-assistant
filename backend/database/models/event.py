"""
Event model for system events and notifications
"""

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from backend.database.base import Base


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
    """Event model - represents system events and logs"""
    __tablename__ = "events"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    
    event_type: Mapped[str] = mapped_column(
        SQLEnum(EventType),
        default=EventType.SYSTEM,
        nullable=False,
        index=True
    )
    event_level: Mapped[str] = mapped_column(
        SQLEnum(EventLevel),
        default=EventLevel.INFO,
        nullable=False,
        index=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user: Mapped["User"] = relationship("User")
    shop: Mapped["Shop"] = relationship("Shop")
    task: Mapped["Task"] = relationship("Task")
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type={self.event_type}, level={self.event_level})>"
