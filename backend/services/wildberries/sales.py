"""
Wildberries Sales Service

Handles all sales, orders, and stocks operations with WB API.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .base import WBBaseService
from backend.config import get_logger

logger = get_logger(__name__)


class WBSalesService(WBBaseService):
    """Service for sales, orders, and stocks operations"""
    
    async def get_sales(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get sales report"""
        logger.info(f"Getting sales: date_from={date_from}, date_to={date_to}, limit={limit}")
        
        params = {}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        if limit is not None:
            params["limit"] = limit
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/supplier/sales",
            params=params
        )
        
        return response
    
    async def get_orders(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get orders list"""
        logger.info(f"Getting orders: date_from={date_from}, date_to={date_to}, limit={limit}")
        
        params = {}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        if limit is not None:
            params["limit"] = limit
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/supplier/orders",
            params=params
        )
        
        return response
    
    async def get_stocks(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get stocks report"""
        logger.info(f"Getting stocks: date_from={date_from}, date_to={date_to}")
        
        params = {}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/supplier/stocks",
            params=params
        )
        
        return response
    
    async def get_stocks_by_warehouse(self, warehouse_id: int) -> Dict[str, Any]:
        """Get stocks by warehouse"""
        logger.info(f"Getting stocks by warehouse: {warehouse_id}")
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/api/v3/stocks/{warehouse_id}"
        )
        
        return response
