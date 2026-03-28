"""
Sales and Reports router for Wildberries Mock API
"""

from fastapi import APIRouter, Header, HTTPException, Query
from datetime import datetime
from typing import Optional
from ..models.sale import (
    Sale, SalesReportResponse,
    Order, OrdersReportResponse,
    Stock, StocksReportResponse
)
from ..data.sales import (
    get_sales, get_orders, get_stocks
)

router = APIRouter(prefix="/api/v1", tags=["Sales & Reports"])


# ============================================
# Sales
# ============================================

@router.get("/supplier/sales", response_model=SalesReportResponse)
async def get_sales_report(
    authorization: str = Header(..., description="Bearer token"),
    dateFrom: Optional[datetime] = Query(None, description="Date from"),
    dateTo: Optional[datetime] = Query(None, description="Date to"),
    limit: int = Query(1000, ge=1, le=10000),
    rrdid: int = Query(0, description="Report ID")
):
    """
    Get sales report
    
    Получить отчет о продажах
    """
    sales = get_sales(date_from=dateFrom, date_to=dateTo)
    
    return SalesReportResponse(
        sales=sales[:limit],
        total=len(sales)
    )


# ============================================
# Orders
# ============================================

@router.get("/supplier/orders", response_model=OrdersReportResponse)
async def get_orders_report(
    authorization: str = Header(..., description="Bearer token"),
    dateFrom: Optional[datetime] = Query(None, description="Date from"),
    dateTo: Optional[datetime] = Query(None, description="Date to"),
    limit: int = Query(1000, ge=1, le=10000)
):
    """
    Get orders report
    
    Получить отчет о заказах
    """
    orders = get_orders(date_from=dateFrom, date_to=dateTo)
    
    return OrdersReportResponse(
        orders=orders[:limit],
        total=len(orders)
    )


# ============================================
# Stocks
# ============================================

@router.get("/supplier/stocks", response_model=StocksReportResponse)
async def get_stocks_report(
    authorization: str = Header(..., description="Bearer token"),
    dateFrom: Optional[datetime] = Query(None, description="Date from")
):
    """
    Get stocks report
    
    Получить отчет об остатках
    """
    stocks = get_stocks()
    
    return StocksReportResponse(
        stocks=stocks,
        total=len(stocks)
    )


# ============================================
# Analytics
# ============================================

@router.get("/supplier/reportDetailByPeriod")
async def get_report_detail_by_period(
    authorization: str = Header(..., description="Bearer token"),
    dateFrom: str = Query(..., description="Date from YYYY-MM-DD"),
    dateTo: str = Query(..., description="Date to YYYY-MM-DD"),
    limit: int = Query(100000, ge=1, le=100000),
    rrdid: int = Query(0, description="Report ID")
):
    """
    Get detailed report by period
    
    Получить детальный отчет за период
    """
    # Mock response with sample data
    return [
        {
            "realizationreport_id": 123456,
            "date_from": dateFrom,
            "date_to": dateTo,
            "create_dt": datetime.now().isoformat(),
            "nm_id": 10001,
            "brand_name": "Test Brand",
            "sa_name": "Test Article",
            "ts_name": "M",
            "barcode": "1234567890",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 1990,
            "retail_amount": 1990,
            "sale_percent": 10,
            "commission_percent": 15.0,
            "office_name": "Коледино",
            "supplier_oper_name": "Продажа",
            "order_dt": datetime.now().isoformat(),
            "sale_dt": datetime.now().isoformat(),
            "ppvz_for_pay": 1590.0
        }
    ]


# ============================================
# Warehouse Stocks
# ============================================

@router.post("/api/v3/stocks/{warehouse_id}")
async def update_warehouse_stocks(
    warehouse_id: str,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Update stocks in warehouse
    
    Обновить остатки на складе
    """
    return {
        "status": "success",
        "message": f"Stocks updated for warehouse {warehouse_id} (mock)"
    }


@router.get("/api/v3/stocks/{warehouse_id}")
async def get_warehouse_stocks(
    warehouse_id: str,
    authorization: str = Header(..., description="Bearer token"),
    skip: int = Query(0, ge=0),
    take: int = Query(1000, ge=1, le=1000)
):
    """
    Get warehouse stocks
    
    Получить остатки на складе
    """
    stocks = get_stocks()
    
    return {
        "stocks": [
            {
                "sku": stock.barcode,
                "amount": stock.quantity
            }
            for stock in stocks[skip:skip + take]
        ],
        "total": len(stocks)
    }
