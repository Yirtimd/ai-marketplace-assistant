"""
Base service for Wildberries API integration

Provides common HTTP client functionality for all WB services.
"""

import httpx
from typing import Dict, Any, Optional
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


class WBBaseService:
    """
    Base service with HTTP client for Wildberries API
    
    All specialized WB services inherit from this class.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize base service
        
        Args:
            api_key: Wildberries API key (from settings if not provided)
            base_url: Base URL for API (from settings if not provided)
        """
        self.api_key = api_key or settings.wb_api_key
        self.base_url = base_url or settings.wb_api_url
        
        if not self.api_key:
            logger.warning("WB API key not set. Some operations may fail.")
        
        # Log mode
        mode = "Mock" if "localhost" in self.base_url else "Real"
        logger.info(f"WB Service initialized: {mode} API at {self.base_url}")
    
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
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"WB API rate limit exceeded, retry after {retry_after}s")
                    # Raise specific exception for Celery autoretry
                    raise WildberriesRateLimitError(f"Rate limit exceeded, retry after {retry_after}s")
                
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
            logger.error(f"WB API request error: {e}")
            raise WildberriesAPIError(f"Request error: {str(e)}")
