"""
Product model for Wildberries products
"""

from sqlalchemy import String, Integer, ForeignKey, Text, Numeric, JSON, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database.base import Base


class Product(Base):
    """Product model - represents a Wildberries product"""
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
    
    # Relationships
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="product")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")
    
    # History relationships (NEW)
    price_history: Mapped[list["PriceHistory"]] = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    stock_history: Mapped[list["StockHistory"]] = relationship("StockHistory", back_populates="product", cascade="all, delete-orphan")
    rating_history: Mapped[list["RatingHistory"]] = relationship("RatingHistory", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, nm_id={self.nm_id}, title={self.title[:30]})>"
