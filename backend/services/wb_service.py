"""
Wildberries API Service

Service for interacting with Wildberries API (or Mock API for development).
Handles all communication with WB API endpoints.
"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.config import get_logger, settings

logger = get_logger(__name__)


class WildberriesServiceError(Exception):
    """Base exception for Wildberries service errors"""
    pass


class WildberriesAuthError(WildberriesServiceError):
    """Authentication error"""
    pass


class WildberriesAPIError(WildberriesServiceError):
    """API request error"""
    pass


class WildberriesService:
    """
    Service for Wildberries API integration
    
    Supports both real WB API and Mock API for development.
    Switch between them by changing WB_API_URL in settings.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Wildberries service
        
        Args:
            api_key: Wildberries API key (from settings if not provided)
            base_url: Base URL for API (from settings if not provided)
        """
        self.api_key = api_key or settings.wb_api_key
        self.base_url = base_url or settings.wb_api_url
        
        if not self.api_key:
            logger.warning("WB API key not set. Some operations may fail.")
        
        logger.info(f"WildberriesService initialized with base_url: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to WB API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body
            
        Returns:
            Response data
            
        Raises:
            WildberriesAuthError: If authentication fails
            WildberriesAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data
                )
                
                # Check for authentication errors
                if response.status_code == 401:
                    logger.error("WB API authentication failed")
                    raise WildberriesAuthError("Invalid API key or unauthorized")
                
                # Check for rate limiting
                if response.status_code == 429:
                    logger.warning("WB API rate limit exceeded")
                    raise WildberriesAPIError("Rate limit exceeded")
                
                # Check for other errors
                if response.status_code >= 400:
                    error_text = response.text
                    logger.error(f"WB API request failed: {response.status_code} - {error_text}")
                    raise WildberriesAPIError(f"API request failed: {error_text}")
                
                return response.json()
        
        except httpx.TimeoutException:
            logger.error(f"WB API request timeout: {url}")
            raise WildberriesAPIError("Request timeout")
        except httpx.RequestError as e:
            logger.error(f"WB API request error for {url}: {e}")
            raise WildberriesAPIError(
                f"Request error: {str(e)}. Check WB_API_URL={self.base_url}"
            )
    
    # ============================================
    # Products Methods
    # ============================================
    
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
        """
        Get product by nmID
        
        Args:
            nm_id: Nomenclature ID
            
        Returns:
            Product data
        """
        logger.info(f"Getting product by ID: {nm_id}")
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/content/v2/cards/{nm_id}"
        )
        
        return response
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories
        
        Returns:
            List of categories
        """
        logger.info("Getting categories")
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/object/parent/all"
        )
        
        return response
    
    async def get_subjects(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all subjects (предметы)
        
        Args:
            name: Filter by name
            
        Returns:
            List of subjects
        """
        logger.info(f"Getting subjects: name={name}")
        
        params = {"name": name} if name else None
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/object/all",
            params=params
        )
        
        return response
    
    async def get_brands(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all brands
        
        Args:
            name: Filter by name
            
        Returns:
            List of brands
        """
        logger.info(f"Getting brands: name={name}")
        
        params = {"name": name} if name else None
        
        response = await self._make_request(
            method="GET",
            endpoint="/content/v2/directory/brands",
            params=params
        )
        
        return response
    
    # ============================================
    # Feedbacks Methods
    # ============================================
    
    async def get_feedbacks(
        self,
        is_answered: Optional[bool] = None,
        take: int = 10000,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of feedbacks
        
        Args:
            is_answered: Filter by answered status
            take: Maximum number of feedbacks
            skip: Offset for pagination
            
        Returns:
            Dictionary with feedbacks list
        """
        logger.info(f"Getting feedbacks: is_answered={is_answered}, take={take}, skip={skip}")
        
        params = {"take": take, "skip": skip}
        if is_answered is not None:
            params["is_answered"] = is_answered
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/feedbacks",
            params=params
        )
        
        return response
    
    async def get_feedback_by_id(self, feedback_id: str) -> Dict[str, Any]:
        """
        Get feedback by ID
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            Feedback data
        """
        logger.info(f"Getting feedback by ID: {feedback_id}")
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/feedback",
            params={"id": feedback_id}
        )
        
        return response
    
    async def answer_feedback(self, feedback_id: str, text: str) -> Dict[str, Any]:
        """
        Reply to feedback
        
        Args:
            feedback_id: Feedback ID
            text: Answer text
            
        Returns:
            Response data
        """
        logger.info(f"Answering feedback: {feedback_id}")
        
        response = await self._make_request(
            method="POST",
            endpoint="/api/v1/feedbacks/answer",
            json_data={"id": feedback_id, "text": text}
        )
        
        return response
    
    async def get_unanswered_feedbacks_count(self) -> int:
        """
        Get count of unanswered feedbacks
        
        Returns:
            Count of unanswered feedbacks
        """
        logger.info("Getting unanswered feedbacks count")
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/feedbacks/count-unanswered"
        )
        
        return response.get("countUnanswered", 0)
    
    # ============================================
    # Questions Methods
    # ============================================
    
    async def get_questions(
        self,
        is_answered: Optional[bool] = None,
        take: int = 10000,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of questions
        
        Args:
            is_answered: Filter by answered status
            take: Maximum number of questions
            skip: Offset for pagination
            
        Returns:
            Dictionary with questions list
        """
        logger.info(f"Getting questions: is_answered={is_answered}, take={take}, skip={skip}")
        
        params = {"take": take, "skip": skip}
        if is_answered is not None:
            params["is_answered"] = is_answered
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/questions",
            params=params
        )
        
        return response
    
    async def answer_question(self, question_id: str, text: str) -> Dict[str, Any]:
        """
        Answer question
        
        Args:
            question_id: Question ID
            text: Answer text
            
        Returns:
            Response data
        """
        logger.info(f"Answering question: {question_id}")
        
        response = await self._make_request(
            method="PATCH",
            endpoint="/api/v1/questions",
            json_data={"id": question_id, "text": text}
        )
        
        return response
    
    async def get_new_feedbacks_questions(self) -> Dict[str, Any]:
        """
        Get counts of new feedbacks and questions
        
        Returns:
            Dictionary with counts
        """
        logger.info("Getting new feedbacks and questions counts")
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/new-feedbacks-questions"
        )
        
        return response
    
    # ============================================
    # Sales Methods
    # ============================================
    
    async def get_sales(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get sales report
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Maximum number of sales
            
        Returns:
            Dictionary with sales list
        """
        logger.info(f"Getting sales: date_from={date_from}, date_to={date_to}, limit={limit}")
        
        params = {"limit": limit}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        
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
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get orders report
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Maximum number of orders
            
        Returns:
            Dictionary with orders list
        """
        logger.info(f"Getting orders: date_from={date_from}, date_to={date_to}, limit={limit}")
        
        params = {"limit": limit}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/supplier/orders",
            params=params
        )
        
        return response
    
    async def get_stocks(
        self,
        date_from: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get stocks report
        
        Args:
            date_from: Start date
            
        Returns:
            Dictionary with stocks list
        """
        logger.info(f"Getting stocks: date_from={date_from}")
        
        params = {}
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        
        response = await self._make_request(
            method="GET",
            endpoint="/api/v1/supplier/stocks",
            params=params
        )
        
        return response

    # ============================================
    # Action Layer Methods (Stage 9)
    # ============================================

    async def create_product_card(self, card_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create product card in Wildberries API.

        Note:
            Mock API accepts this endpoint without strict body schema.
        """
        logger.info("Creating product card via WB API")
        return await self._make_request(
            method="POST",
            endpoint="/content/v2/cards/upload",
            json_data=card_payload,
        )

    async def update_product_card(self, card_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update product card in Wildberries API.
        """
        logger.info("Updating product card via WB API")
        return await self._make_request(
            method="POST",
            endpoint="/content/v2/cards/update",
            json_data=card_payload,
        )

    async def update_price(self, nm_id: int, new_price: float, discount: Optional[float] = None) -> Dict[str, Any]:
        """
        Update product price through card update endpoint.

        For mock API this is represented as card update.
        """
        logger.info("Updating product price nm_id=%s -> %s", nm_id, new_price)
        payload: Dict[str, Any] = {
            "nmID": nm_id,
            "price": new_price,
        }
        if discount is not None:
            payload["discount"] = discount

        response = await self.update_product_card(payload)
        response.update(
            {
                "nm_id": nm_id,
                "new_price": new_price,
                "discount": discount,
            }
        )
        return response

    async def reply_to_review(self, review_id: str, reply_text: str) -> Dict[str, Any]:
        """
        Publish reply to review via WB feedback endpoint.
        """
        logger.info("Replying to review id=%s", review_id)
        return await self.answer_feedback(review_id, reply_text)


# Singleton instance
_wb_service_instance: Optional[WildberriesService] = None


def get_wb_service() -> WildberriesService:
    """
    Get WildberriesService singleton instance
    
    Returns:
        WildberriesService instance
    """
    global _wb_service_instance
    
    if _wb_service_instance is None:
        _wb_service_instance = WildberriesService()
    
    return _wb_service_instance
