"""
Pydantic models for Wildberries Products API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Size(BaseModel):
    """Product size model"""
    techSize: str = Field(..., description="Technical size")
    wbSize: str = Field(..., description="WB size")
    price: int = Field(..., description="Price in rubles")
    discountedPrice: int = Field(..., description="Discounted price")
    skus: List[str] = Field(default_factory=list, description="SKU list")


class Photo(BaseModel):
    """Product photo model"""
    big: str = Field(..., description="Big photo URL")
    small: str = Field(..., description="Small photo URL")


class Characteristic(BaseModel):
    """Product characteristic"""
    name: str = Field(..., description="Characteristic name")
    value: str | List[str] = Field(..., description="Characteristic value")


class Product(BaseModel):
    """Product card model"""
    nmID: int = Field(..., description="Nomenclature ID")
    imtID: int = Field(..., description="IMT ID")
    nmUUID: str = Field(..., description="Nomenclature UUID")
    subjectID: int = Field(..., description="Subject ID")
    subjectName: str = Field(..., description="Subject name")
    vendorCode: str = Field(..., description="Vendor code")
    brand: str = Field(..., description="Brand name")
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Product description")
    video: Optional[str] = Field(None, description="Video URL")
    sizes: List[Size] = Field(default_factory=list, description="Sizes list")
    photos: List[Photo] = Field(default_factory=list, description="Photos list")
    characteristics: List[Characteristic] = Field(default_factory=list, description="Characteristics")
    createdAt: datetime = Field(default_factory=datetime.now, description="Created at")
    updatedAt: datetime = Field(default_factory=datetime.now, description="Updated at")


class ProductListResponse(BaseModel):
    """Response for product list"""
    cursor: Dict[str, Any] = Field(default_factory=dict, description="Pagination cursor")
    cards: List[Product] = Field(default_factory=list, description="Product cards")


class ProductCreateRequest(BaseModel):
    """Request for creating product"""
    subjectID: int = Field(..., description="Subject ID")
    vendorCode: str = Field(..., description="Vendor code")
    brand: str = Field(..., description="Brand name")
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Product description")
    characteristics: List[Characteristic] = Field(..., description="Characteristics")
    sizes: List[Dict[str, Any]] = Field(..., description="Sizes")


class ProductUpdateRequest(BaseModel):
    """Request for updating product"""
    nmID: int = Field(..., description="Nomenclature ID")
    vendorCode: Optional[str] = Field(None, description="Vendor code")
    title: Optional[str] = Field(None, description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    characteristics: Optional[List[Characteristic]] = Field(None, description="Characteristics")


class Category(BaseModel):
    """Product category model"""
    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    parentID: Optional[int] = Field(None, description="Parent category ID")
    isVisible: bool = Field(True, description="Is visible")


class Subject(BaseModel):
    """Product subject (предмет)"""
    id: int = Field(..., description="Subject ID")
    name: str = Field(..., description="Subject name")
    parentID: int = Field(..., description="Parent category ID")
    parentName: str = Field(..., description="Parent category name")


class Brand(BaseModel):
    """Brand model"""
    id: int = Field(..., description="Brand ID")
    name: str = Field(..., description="Brand name")


class CharacteristicOption(BaseModel):
    """Characteristic option"""
    id: int = Field(..., description="Option ID")
    name: str = Field(..., description="Option name")


class SubjectCharacteristic(BaseModel):
    """Subject characteristic"""
    id: int = Field(..., description="Characteristic ID")
    name: str = Field(..., description="Characteristic name")
    required: bool = Field(..., description="Is required")
    unitName: Optional[str] = Field(None, description="Unit name")
    maxCount: int = Field(1, description="Max count of values")
    options: List[CharacteristicOption] = Field(default_factory=list, description="Available options")
