"""
Wildberries exceptions
"""


class WildberriesServiceError(Exception):
    """Base exception for Wildberries service errors"""
    pass


class WildberriesAuthError(WildberriesServiceError):
    """Authentication error"""
    pass


class WildberriesAPIError(WildberriesServiceError):
    """API request error"""
    pass


class WildberriesRateLimitError(WildberriesAPIError):
    """Rate limit exceeded"""
    pass


class WildberriesNotFoundError(WildberriesAPIError):
    """Resource not found"""
    pass
