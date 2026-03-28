"""
Shop model for Wildberries seller shops
"""

from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.base import Base


class Shop(Base):
    """Shop model - represents a Wildberries seller shop"""
    __tablename__ = "shops"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    wb_api_key: Mapped[str] = mapped_column(String(512), nullable=False)
    wb_supplier_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="shops")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="shop", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="shop", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Shop(id={self.id}, name={self.name})>"
