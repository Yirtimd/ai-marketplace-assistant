"""
Wildberries Products Service

Handles all product-related operations with WB API.
"""

from typing import List, Dict, Any, Optional
from .base import WBBaseService
from backend.config import get_logger

logger = get_logger(__name__)


class WBProductsService(WBBaseService):
    """Service for products operations"""
    
    async def get_products(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of products
        
        Args:
            limit: Maximum number of products to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with products list and cursor
        """
        logger.info(f"Getting products: limit={limit}, offset={offset}")
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/get/cards/list",
            params={"limit": limit, "offset": offset}
        )
        
        return response
    
    async def get_product_by_id(self, nm_id: int) -> Dict[str, Any]:
        """Get product by nmID"""
        logger.info(f"Getting product by ID: {nm_id}")
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/content/v2/cards/{nm_id}"
        )
        
        return response
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        logger.info("Getting categories")
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/object/parent/all"
        )
        
        return response
    
    async def get_subjects(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all subjects"""
        logger.info(f"Getting subjects: name={name}")
        
        params = {"name": name} if name else None
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/object/all",
            params=params
        )
        
        return response
    
    async def get_brands(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all brands"""
        logger.info(f"Getting brands: name={name}")
        
        params = {"name": name} if name else None
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/directory/brands",
            params=params
        )
        
        return response
