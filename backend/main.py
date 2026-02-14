# CHECKPOINT_9_API_INTEGRATION
"""
FastAPI Main Application
=========================
Entry point for the expense tracking REST API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from backend.config import settings, validate_config, print_config_summary
# from backend.api import auth, expenses, budgets, voice, cost_of_living
from backend.utils.logger import setup_logging

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs startup and shutdown logic.
    """
    # Startup
    logger.info("🚀 Starting LLM Expense Tracker API...")
    
    try:
        validate_config()
        print_config_summary()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"✗ Configuration error: {e}")
        raise
    
    # TODO: Initialize database connection pool
    # TODO: Verify Supabase connection
    # TODO: Check LLM availability
    
    logger.info("✓ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")
    # TODO: Close database connections
    # TODO: Cleanup resources


# ============================================
# Create FastAPI App
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LLM-powered expense tracking API with multimodal input",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================
# Middleware
# ============================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )


# ============================================
# Root Endpoint
# ============================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "expenses": "/api/v1/expenses",
            "budgets": "/api/v1/budgets",
            "voice": "/api/v1/voice",
            "cost-of-living": "/api/v1/cost-of-living",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "version": settings.APP_VERSION
    }


# ============================================
# API Routers
# ============================================
# TODO: Uncomment as routers are implemented

# app.include_router(
#     auth.router,
#     prefix=f"{settings.API_PREFIX}/auth",
#     tags=["Authentication"]
# )
#
# app.include_router(
#     expenses.router,
#     prefix=f"{settings.API_PREFIX}/expenses",
#     tags=["Expenses"]
# )
#
# app.include_router(
#     budgets.router,
#     prefix=f"{settings.API_PREFIX}/budgets",
#     tags=["Budgets"]
# )
#
# app.include_router(
#     voice.router,
#     prefix=f"{settings.API_PREFIX}/voice",
#     tags=["Voice Input"]
# )
#
# app.include_router(
#     cost_of_living.router,
#     prefix=f"{settings.API_PREFIX}/cost-of-living",
#     tags=["Cost of Living"]
# )


# ============================================
# Development Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
