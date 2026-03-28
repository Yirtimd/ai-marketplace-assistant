"""
Review model for customer reviews and feedbacks
"""

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class Review(Base):
    """Review model - represents customer feedback or question"""
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
    
    shop: Mapped["Shop"] = relationship("Shop", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, type={self.review_type}, rating={self.rating})>"
