"""
FastAPI application for the Brikkle chatbot with RAG system.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from routes import router
from schema import ErrorResponse
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Brikkle Chatbot API...")
    
    # Initialize services
    try:
        from services.service import get_rag_service
        from services.chat_service import get_chat_service
        
        # Initialize RAG service (this will create/load FAISS index)
        logger.info("Initializing RAG service...")
        rag_service = get_rag_service()
        logger.info(f"RAG service initialized with {rag_service.get_stats()['total_documents']} documents")
        
        # Initialize chat service
        logger.info("Initializing chat service...")
        chat_service = get_chat_service()
        logger.info("Chat service initialized successfully")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Brikkle Chatbot API...")


# Create FastAPI application
app = FastAPI(
    title="Brikkle Chatbot API",
    description="""
    A RAG-powered chatbot for Brikkle, Nigeria's first blockchain-powered real estate investment platform.
    
    This API provides intelligent responses about:
    - Brikkle's platform and services
    - Real estate investment opportunities
    - Account setup and verification
    - Payment and transaction processes
    - Property due diligence
    - Technical support and troubleshooting
    
    The chatbot uses Retrieval-Augmented Generation (RAG) with FAISS vector search
    and Google Generative AI to provide accurate, context-aware responses.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Brikkle Chatbot API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "chatbot",
            "description": "Chatbot endpoints for interacting with the Brikkle AI assistant"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Include routers
app.include_router(router)


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to Brikkle Chatbot API",
        "version": "1.0.0",
        "description": "RAG-powered chatbot for Brikkle real estate investment platform",
        "endpoints": {
            "health": "/api/v1/health",
            "chat": "/api/v1/chat",
            "stats": "/api/v1/stats",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with custom error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"HTTP {exc.status_code} error",
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred. Please try again later.",
            timestamp=datetime.now()
        ).dict()
    )


# Health check endpoint (additional to the one in routes)
@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
