"""
Sales and Reports routes for Wildberries data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from backend.config.dependencies import get_wb_sales_service
from backend.services.wildberries import WBSalesService, WildberriesServiceError
from backend.schemas.wb import (
    SalesListResponse, OrdersListResponse, StocksListResponse
)

router = APIRouter(prefix="/sales", tags=["Sales & Reports"])


@router.get("/", response_model=SalesListResponse)
async def get_sales(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of sales"),
    wb: WBSalesService = Depends(get_wb_sales_service)
):
    """
    Get sales report
    
    Returns list of sales with optional date filtering.
    """
    try:
        data = await wb.get_sales(date_from=date_from, date_to=date_to, limit=limit)
        return SalesListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=OrdersListResponse)
async def get_orders(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of orders"),
    wb: WBSalesService = Depends(get_wb_sales_service)
):
    """
    Get orders report
    
    Returns list of orders with optional date filtering.
    """
    try:
        data = await wb.get_orders(date_from=date_from, date_to=date_to, limit=limit)
        return OrdersListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks", response_model=StocksListResponse)
async def get_stocks(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    wb: WBSalesService = Depends(get_wb_sales_service)
):
    """
    Get stocks report
    
    Returns list of stock levels for all products.
    """
    try:
        data = await wb.get_stocks(date_from=date_from)
        return StocksListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
