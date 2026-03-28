"""
Price History model for tracking product price changes

This table stores historical price data for AI analytics:
- Price elasticity analysis
- A/B testing effectiveness
- Optimal pricing recommendations
"""

from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class PriceHistory(Base):
    """Price change history for products"""
    __tablename__ = "price_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=True)
    
    product: Mapped["Product"] = relationship("Product", back_populates="price_history")
    
    def __repr__(self) -> str:
        return f"<PriceHistory(product_id={self.product_id}, price={self.price}, changed_at={self.changed_at})>"


__table_args__ = (
    Index('idx_price_history_product_time', 'product_id', 'changed_at'),
)
