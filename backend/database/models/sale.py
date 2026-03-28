"""
Sale model for Wildberries sales records
"""

from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class Sale(Base):
    """Sale model - represents a sale transaction from Wildberries"""
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
    
    shop: Mapped["Shop"] = relationship("Shop", back_populates="sales")
    product: Mapped["Product"] = relationship("Product", back_populates="sales")
    
    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, sale_id={self.sale_id}, total={self.total_price})>"
