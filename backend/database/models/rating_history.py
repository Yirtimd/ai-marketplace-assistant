"""
Rating History model for tracking product rating changes

This table stores historical rating data for AI analytics:
- Rating impact on sales correlation
- Review sentiment analysis trends
- Product reputation monitoring
"""

from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class RatingHistory(Base):
    """Rating change history for products"""
    __tablename__ = "rating_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    product: Mapped["Product"] = relationship("Product", back_populates="rating_history")
    
    def __repr__(self) -> str:
        return f"<RatingHistory(product_id={self.product_id}, rating={self.rating}, reviews={self.reviews_count})>"


__table_args__ = (
    Index('idx_rating_history_product_time', 'product_id', 'recorded_at'),
)
