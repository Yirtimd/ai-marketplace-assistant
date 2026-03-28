"""
Main FastAPI application for Wildberries Mock API
"""

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .routers import products, feedbacks, sales

# Create FastAPI app
app = FastAPI(
    title="Wildberries Mock API",
    description="Mock API server for Wildberries API development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Authentication Middleware
# ============================================

VALID_TOKENS = [
    "test-api-key-12345",
    "Bearer test-api-key-12345"
]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Check authorization token"""
    
    # Skip auth for docs
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/"]:
        return await call_next(request)
    
    # Get auth header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"error": True, "errorText": "Authorization header required"}
        )
    
    # Validate token
    token = auth_header.replace("Bearer ", "")
    if token not in VALID_TOKENS and auth_header not in VALID_TOKENS:
        return JSONResponse(
            status_code=401,
            content={"error": True, "errorText": "Invalid authorization token"}
        )
    
    response = await call_next(request)
    return response


# ============================================
# Rate Limiting Middleware
# ============================================

request_times = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting"""
    
    # Skip rate limit for docs
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/"]:
        return await call_next(request)
    
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests (older than 1 second)
    if client_ip in request_times:
        request_times[client_ip] = [
            t for t in request_times[client_ip] 
            if current_time - t < 1
        ]
    else:
        request_times[client_ip] = []
    
    # Check rate limit (3 requests per second)
    if len(request_times[client_ip]) >= 3:
        return JSONResponse(
            status_code=429,
            content={"error": True, "errorText": "Rate limit exceeded. Max 3 requests per second."}
        )
    
    # Add current request
    request_times[client_ip].append(current_time)
    
    response = await call_next(request)
    return response


# ============================================
# Include Routers
# ============================================

app.include_router(products.router)
app.include_router(feedbacks.router)
app.include_router(sales.router)


# ============================================
# Root Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Wildberries Mock API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "message": "Mock API server for Wildberries API development"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "products": "available",
        "feedbacks": "available",
        "sales": "available"
    }


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "errorText": exc.detail,
            "data": {}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "errorText": f"Internal server error: {str(exc)}",
            "data": {}
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
