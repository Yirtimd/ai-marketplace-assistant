"""
Sales, orders, and stocks schemas for Wildberries API
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Sale(BaseModel):
    """Sale record"""
    saleID: str
    orderID: str
    nmID: int
    vendorCode: str
    date: datetime
    quantity: int
    price: float
    discount: float
    totalPrice: float
    warehouseName: str
    oblast: str
    region: str


class SalesListResponse(BaseModel):
    """Response for sales list"""
    data: list[Sale]
    total: int


class Order(BaseModel):
    """Order record"""
    orderID: str
    nmID: int
    vendorCode: str
    date: datetime
    quantity: int
    price: float
    warehouseName: str
    oblast: str
    region: str
    status: str = "NEW"


class OrdersListResponse(BaseModel):
    """Response for orders list"""
    data: list[Order]
    total: int


class Stock(BaseModel):
    """Stock record"""
    nmID: int
    vendorCode: str
    warehouseId: int
    warehouseName: str
    quantity: int
    quantityFull: int
    inWayToClient: int
    inWayFromClient: int
    date: datetime


class StocksListResponse(BaseModel):
    """Response for stocks list"""
    data: list[Stock]
    total: int
