from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Multi-tenant middleware to handle company context"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Extract tenant/company information from headers or subdomain
            company_id = None
            
            # Method 1: From X-Company-ID header
            company_header = request.headers.get("X-Company-ID")
            if company_header:
                try:
                    company_id = int(company_header)
                except ValueError:
                    pass
            
            # Method 2: From subdomain (e.g., company1.hrms.com)
            if not company_id:
                host = request.headers.get("host", "")
                if "." in host:
                    subdomain = host.split(".")[0]
                    # You could implement subdomain to company_id mapping here
                    # For now, we'll skip this implementation
                    pass
            
            # Method 3: From URL path parameter
            if not company_id:
                path_parts = request.url.path.split("/")
                if len(path_parts) > 3 and path_parts[1] == "api" and path_parts[2] == "v1":
                    # Look for company context in specific endpoints
                    pass
            
            # Add company context to request state
            request.state.company_id = company_id
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            return await call_next(request)
