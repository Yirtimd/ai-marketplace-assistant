"""
Products router for Wildberries Mock API
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import List, Optional
from ..models.product import (
    Product, ProductListResponse, Category, Subject,
    Brand, SubjectCharacteristic
)
from ..data.products import (
    get_products, get_product_by_id, get_product_by_vendor_code,
    CATEGORIES, SUBJECTS, BRANDS, SUBJECT_CHARACTERISTICS
)

router = APIRouter(prefix="/content", tags=["Products"])


@router.get("/v2/get/cards/list", response_model=ProductListResponse)
async def get_cards_list(
    authorization: str = Header(..., description="Bearer token"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get list of product cards
    
    Получить список карточек товаров
    """
    products = get_products(limit=limit, offset=offset)
    
    return ProductListResponse(
        cursor={"total": len(products), "offset": offset, "limit": limit},
        cards=products
    )


@router.get("/v2/cards/{nm_id}", response_model=Product)
async def get_card_by_id(
    nm_id: int,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get product card by nmID
    
    Получить карточку товара по nmID
    """
    product = get_product_by_id(nm_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/v2/object/parent/all", response_model=List[Category])
async def get_all_categories(
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get all categories
    
    Получить все категории
    """
    return CATEGORIES


@router.get("/v2/object/all", response_model=List[Subject])
async def get_all_subjects(
    authorization: str = Header(..., description="Bearer token"),
    name: Optional[str] = Query(None, description="Filter by name")
):
    """
    Get all subjects (предметы)
    
    Получить все предметы
    """
    subjects = SUBJECTS
    
    if name:
        subjects = [s for s in subjects if name.lower() in s.name.lower()]
    
    return subjects


@router.get("/v2/object/charcs/{subject_id}", response_model=List[SubjectCharacteristic])
async def get_subject_characteristics(
    subject_id: int,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Get characteristics for subject
    
    Получить характеристики для предмета
    """
    characteristics = SUBJECT_CHARACTERISTICS.get(subject_id, [])
    
    if not characteristics:
        raise HTTPException(status_code=404, detail="Subject not found or has no characteristics")
    
    return characteristics


@router.get("/v2/directory/brands", response_model=List[Brand])
async def get_brands(
    authorization: str = Header(..., description="Bearer token"),
    name: Optional[str] = Query(None, description="Filter by name")
):
    """
    Get all brands
    
    Получить все бренды
    """
    brands = BRANDS
    
    if name:
        brands = [b for b in brands if name.lower() in b.name.lower()]
    
    return brands


@router.post("/v2/cards/upload")
async def create_product_card(
    authorization: str = Header(..., description="Bearer token"),
):
    """
    Create new product card
    
    Создать новую карточку товара
    """
    return {
        "id": "12345-67890",
        "status": "created",
        "message": "Product card created successfully (mock)"
    }


@router.post("/v2/cards/update")
async def update_product_card(
    authorization: str = Header(..., description="Bearer token"),
):
    """
    Update product card
    
    Обновить карточку товара
    """
    return {
        "status": "updated",
        "message": "Product card updated successfully (mock)"
    }


@router.delete("/v2/cards/{nm_id}")
async def delete_product_card(
    nm_id: int,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Delete product card
    
    Удалить карточку товара
    """
    return {
        "status": "deleted",
        "nmID": nm_id,
        "message": "Product card deleted successfully (mock)"
    }
