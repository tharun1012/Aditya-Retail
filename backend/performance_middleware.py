"""
Performance Middleware for FastAPI
Adds caching headers, compression, and performance optimizations
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
import time

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add performance optimizations:
    - Cache-Control headers for static assets
    - ETag support
    - Response time tracking
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start time for response time tracking
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add caching headers based on path
        path = request.url.path
        
        # Static assets - Cache for 1 year
        if any(ext in path for ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf']):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        
        # API endpoints - Different caching strategies
        elif path.startswith('/api/'):
            # Admin-editable / dynamic data - NEVER cache.
            # Product catalogue prices change frequently from admin; caching causes
            # stale prices on storefront for up to TTL even after edits are saved.
            if any(x in path for x in ['/products', '/categories', '/cart', '/orders', '/checkout', '/auth', '/leads', '/mail-leads', '/quotations', '/invoices', '/combo-offers']):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            # Other API - Cache for 1 minute
            else:
                response.headers["Cache-Control"] = "public, max-age=60"
        
        # HTML pages - Cache for 10 minutes
        elif path.endswith('.html') or path == '/':
            response.headers["Cache-Control"] = "public, max-age=600"
        
        # Add Vary header for proper caching
        response.headers["Vary"] = "Accept-Encoding"
        
        return response


def add_performance_headers(response: Response):
    """
    Add additional performance-related headers
    """
    # Enable keep-alive
    response.headers["Connection"] = "keep-alive"
    
    # Suggest browser to prefetch DNS for external resources
    response.headers["X-DNS-Prefetch-Control"] = "on"
    
    return response
