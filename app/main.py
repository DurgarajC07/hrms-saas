"""
HRMS SaaS Platform - Main Application Entry Point
High-performance FastAPI application for comprehensive HR management
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
import uvicorn
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import redis_manager
from app.api.v1.api import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.tenant import TenantMiddleware
from app.middleware.logging import LoggingMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## HRMS SaaS Platform
    
    A comprehensive Human Resource Management System built with FastAPI, offering:
    
    ### 🏢 Core Features
    - **Employee Management**: Complete employee lifecycle management
    - **Attendance Tracking**: GPS-based attendance with geofencing
    - **Payroll Processing**: Automated payroll with tax calculations
    - **Leave Management**: Flexible leave policies and approval workflows
    - **Performance Reviews**: 360° feedback and goal management
    
    ### 📊 Advanced Capabilities  
    - **Benefits Administration**: Health insurance, retirement plans
    - **Expense Management**: Receipt handling and reimbursements
    - **Asset Management**: IT equipment and resource tracking
    - **Document Management**: Digital signatures and compliance
    - **Onboarding**: Structured new employee workflows
    
    ### 🔒 Enterprise Features
    - **Multi-tenant Architecture**: Secure company data isolation
    - **Role-based Access Control**: Granular permission management  
    - **Audit Trails**: Complete activity logging
    - **Real-time Analytics**: Interactive dashboards and reports
    - **API Integration**: REST APIs with comprehensive documentation
    """,
    version="1.0.0",
    contact={
        "name": "HRMS Support Team",
        "email": "support@hrms-saas.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Users", "description": "User management operations"},
        {"name": "Companies", "description": "Company profile and settings"},
        {"name": "Employees", "description": "Employee management and profiles"},
        {"name": "Attendance", "description": "Time tracking and attendance management"},
        {"name": "Payroll", "description": "Payroll processing and salary management"},
        {"name": "Leaves", "description": "Leave management and approval workflows"},
        {"name": "Performance", "description": "Performance reviews and goal management"},
        {"name": "Benefits", "description": "Employee benefits and enrollment"},
        {"name": "Expenses", "description": "Expense management and reimbursements"},
        {"name": "Assets", "description": "Asset management and tracking"},
        {"name": "Documents", "description": "Document management and storage"},
        {"name": "Onboarding", "description": "Employee onboarding workflows"},
        {"name": "Compliance", "description": "Compliance management and reporting"},
        {"name": "Analytics", "description": "Reports and analytics"},
    ]
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Global exception occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": time.time()
        }
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    try:
        # Check database connection
        await init_db()
        
        # Check Redis connection
        redis_status = await redis_manager.ping()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "database": "connected",
            "redis": "connected" if redis_status else "disconnected"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Startup events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting HRMS SaaS Platform...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database connection established")
        
        # Initialize Redis
        await redis_manager.init_redis()
        logger.info("Redis connection established")
        
        logger.info("HRMS SaaS Platform started successfully!")
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise

# Shutdown events  
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down HRMS SaaS Platform...")
    
    try:
        # Close Redis connections
        await redis_manager.close()
        logger.info("Redis connections closed")
        
        logger.info("HRMS SaaS Platform shutdown complete")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to HRMS SaaS Platform",
        "description": "Comprehensive Human Resource Management System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.API_V1_STR,
        "features": [
            "Employee Management",
            "Attendance Tracking", 
            "Payroll Processing",
            "Leave Management",
            "Performance Reviews",
            "Benefits Administration",
            "Expense Management",
            "Asset Management",
            "Document Management",
            "Onboarding Workflows",
            "Compliance Management",
            "Real-time Analytics"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
