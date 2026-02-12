"""
Custom middleware for rate limiting and caching
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Callable
import hashlib
import json
import time
from collections import defaultdict
from .database import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Simple in-memory rate limiter for specific endpoints
rate_limit_store = defaultdict(list)


def get_rate_limiter():
    """Get rate limiter instance"""
    return limiter


# Cache storage (in-memory, can be replaced with Redis for production)
cache_store = {}


def get_cache_key(request: Request) -> str:
    """Generate cache key from request"""
    path = request.url.path
    query_params = str(sorted(request.query_params.items()))
    return hashlib.md5(f"{path}{query_params}".encode()).hexdigest()


def check_rate_limit(client_ip: str, endpoint: str, limit: int, window: int = 60) -> bool:
    """Check if request is within rate limit"""
    current_time = time.time()
    key = f"{client_ip}:{endpoint}"
    
    # Clean old entries
    rate_limit_store[key] = [
        timestamp for timestamp in rate_limit_store[key]
        if current_time - timestamp < window
    ]
    
    # Check limit
    if len(rate_limit_store[key]) >= limit:
        return False
    
    # Add current request
    rate_limit_store[key].append(current_time)
    return True


async def cache_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for caching GET requests and rate limiting"""
    client_ip = get_remote_address(request)
    path = request.url.path
    
    # Rate limiting for specific endpoints
    if path == "/api/register" or path == "/api/login":
        if not check_rate_limit(client_ip, path, limit=5, window=60):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
    elif path == "/api/forgot-password":
        if not check_rate_limit(client_ip, path, limit=3, window=60):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
    
    # Skip caching for now to avoid issues - can be re-enabled later
    # For non-GET requests or non-API routes, just pass through
    return await call_next(request)


def clear_cache():
    """Clear all cache (useful for testing or manual cache invalidation)"""
    global cache_store
    cache_store.clear()
