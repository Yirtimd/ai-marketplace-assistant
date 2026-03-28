"""
Stock History model for tracking inventory changes

This table stores historical stock data for AI analytics:
- Stockout prediction
- Sales velocity calculation
- Optimal reorder point recommendation
- Inventory optimization
"""

from sqlalchemy import String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


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
    
    product: Mapped["Product"] = relationship("Product", back_populates="stock_history")
    
    def __repr__(self) -> str:
        return f"<StockHistory(product_id={self.product_id}, total={self.stock_total}, recorded_at={self.recorded_at})>"


__table_args__ = (
    Index('idx_stock_history_product_time', 'product_id', 'recorded_at'),
)
