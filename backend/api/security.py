"""
Temporary API security layer.

Current default mode is allow-all for development/manual testing.
Can be switched to token mode via settings without changing routes.
"""

from typing import Dict, Any, Optional

from fastapi import Header, HTTPException

from config import settings


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    token = authorization[len(prefix):].strip()
    return token or None


async def require_api_access(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """
    Global API access dependency.

    Modes:
    - auth_allow_all=True  -> allow any request (temporary dev mode)
    - auth_allow_all=False -> require Bearer token equal to auth_test_token
    """
    if settings.auth_allow_all:
        return {
            "access_mode": "allow_all",
            "user_id": 0,
            "role": "developer",
        }

    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization Bearer token is required")

    if token != settings.auth_test_token:
        raise HTTPException(status_code=403, detail="Invalid API token")

    return {
        "access_mode": "token",
        "user_id": 1,
        "role": "tester",
    }

