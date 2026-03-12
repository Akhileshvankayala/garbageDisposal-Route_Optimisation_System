from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

# Import configuration and database
from config import ALLOWED_ORIGINS
from database import init_db

# Import logging configuration
from middleware.logging_config import logger

# Import route handlers
from routes import nodes, edges, auth, analytics, route_management, vehicle_tracking, driver_operations
from routes.routes import router as routes_router

# Import exception handlers
from middleware.error_handler import global_exception_handler, validation_exception_handler

# Initialize FastAPI app
app = FastAPI(
    title="MediTrack API",
    description="Biomedical waste collection route optimization system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include route routers
app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(routes_router)
app.include_router(route_management.router)
app.include_router(vehicle_tracking.router)
app.include_router(driver_operations.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    logger.info("=" * 80)
    logger.info("MediTrack API Starting...")
    logger.info("=" * 80)

    init_db()

    logger.info("[OK] Database initialized")
    logger.info("[OK] Application ready to serve requests")


@app.on_event("shutdown")
def shutdown_event():
    """Log shutdown."""
    logger.info("=" * 80)
    logger.info("MediTrack API Shutting down...")
    logger.info("=" * 80)


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MediTrack API",
        "version": "1.0.0",
    }


@app.get("/", tags=["root"])
def root():
    """Root endpoint with API information."""
    return {
        "name": "MediTrack API",
        "description": "Biomedical waste collection route optimization system",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "nodes": "/api/nodes",
            "edges": "/api/edges",
            "routes": "/api/route/compute",
            "auth": "/api/auth",
            "reports": "/api/reports",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
