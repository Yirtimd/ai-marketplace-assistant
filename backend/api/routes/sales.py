"""
Sales and Reports routes for Wildberries data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from backend.config.dependencies import get_wb_sales_service
from backend.services.wildberries import WBSalesService, WildberriesServiceError
router = APIRouter(prefix="/sales", tags=["Sales & Reports"])


@router.get("/", response_model=dict)
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
        # Normalize response shape for both mock and real providers.
        if "data" in data:
            return data
        if "sales" in data:
            return {"data": data["sales"], "total": data.get("total", len(data["sales"]))}
        return {"data": [], "total": 0, "raw": data}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=dict)
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
        if "data" in data:
            return data
        if "orders" in data:
            return {"data": data["orders"], "total": data.get("total", len(data["orders"]))}
        return {"data": [], "total": 0, "raw": data}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks", response_model=dict)
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
        if "data" in data:
            return data
        if "stocks" in data:
            return {"data": data["stocks"], "total": data.get("total", len(data["stocks"]))}
        return {"data": [], "total": 0, "raw": data}
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
