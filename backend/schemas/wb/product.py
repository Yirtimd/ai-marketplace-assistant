"""
Product schemas for Wildberries API
"""

from typing import List, Union
from pydantic import BaseModel


class ProductSize(BaseModel):
    """Product size"""
    techSize: str
    wbSize: str
    price: int
    discountedPrice: int
    skus: List[str] = []


class ProductPhoto(BaseModel):
    """Product photo"""
    big: str
    small: str


class ProductCharacteristic(BaseModel):
    """Product characteristic"""
    name: str
    value: Union[str, List[str]]


class Product(BaseModel):
    """Product card"""
    nmID: int
    imtID: int
    vendorCode: str
    brand: str
    title: str
    description: str
    subjectName: str
    sizes: List[ProductSize]
    photos: List[ProductPhoto]
    characteristics: List[ProductCharacteristic]


class ProductsListResponse(BaseModel):
    """Response for products list"""
    cursor: dict
    cards: List[Product]
