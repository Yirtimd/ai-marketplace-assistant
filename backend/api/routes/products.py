"""
Products routes for Wildberries data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.config.dependencies import get_wb_products_service
from backend.services.wildberries import WBProductsService, WildberriesServiceError
from backend.schemas.wb import (
    ProductsListResponse, Product, Category, Subject, Brand
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=ProductsListResponse)
async def get_products(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    wb: WBProductsService = Depends(get_wb_products_service)
):
    """
    Get list of products from Wildberries
    
    Returns paginated list of product cards.
    """
    try:
        data = await wb.get_products(limit=limit, offset=offset)
        return ProductsListResponse(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{nm_id}", response_model=Product)
async def get_product_by_id(
    nm_id: int,
    wb: WBProductsService = Depends(get_wb_products_service)
):
    """
    Get product by nmID
    
    Returns detailed information about a specific product.
    """
    try:
        data = await wb.get_product_by_id(nm_id)
        return Product(**data)
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reference/categories", response_model=list[Category])
async def get_categories(
    wb: WBProductsService = Depends(get_wb_products_service)
):
    """
    Get all product categories
    
    Returns list of available product categories.
    """
    try:
        data = await wb.get_categories()
        return [Category(**cat) for cat in data]
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reference/subjects", response_model=list[Subject])
async def get_subjects(
    name: Optional[str] = Query(None, description="Filter by name"),
    wb: WBProductsService = Depends(get_wb_products_service)
):
    """
    Get all product subjects
    
    Returns list of available product subjects (предметы).
    """
    try:
        data = await wb.get_subjects(name=name)
        return [Subject(**subj) for subj in data]
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reference/brands", response_model=list[Brand])
async def get_brands(
    name: Optional[str] = Query(None, description="Filter by name"),
    wb: WBProductsService = Depends(get_wb_products_service)
):
    """
    Get all brands
    
    Returns list of available brands.
    """
    try:
        data = await wb.get_brands(name=name)
        return [Brand(**brand) for brand in data]
    except WildberriesServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
