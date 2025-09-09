"""
FastAPI routes for the Brikkle chatbot API.
Simplified to have only one main chat endpoint with automatic session management.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from schema import (
    ChatRequest, 
    ChatResponse, 
    HealthResponse, 
    ErrorResponse,
    ChatMessage
)
from services.chat_service import get_chat_service
from services.service import get_rag_service
from services.chat_history_service import get_chat_history_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["chatbot"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service is unhealthy"
        )


@router.post("/chat", response_model=Dict[str, Any])
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for interacting with the Brikkle chatbot.
    
    This endpoint:
    1. Automatically manages sessions (creates new session if none provided)
    2. Takes a user message and optional session_id
    3. Retrieves last 5 messages for context
    4. Generates response using RAG and Google Generative AI
    5. Stores both user message and AI response
    6. Returns response with session_id for frontend to track
    
    The frontend should store the session_id and pass it with each request.
    If no session_id is provided, a new session is automatically created.
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Get services
        chat_service = get_chat_service()
        history_service = get_chat_history_service()
        
        # Get or create session
        session_id = getattr(request, 'session_id', None)
        if not session_id:
            session_id = history_service.create_session()
            logger.info(f"Created new session: {session_id}")
        
        # Get last 5 messages for context
        conversation_history = history_service.get_session_history(session_id, limit=5)
        
        # Generate response
        response = chat_service.generate_response(
            message=request.message,
            conversation_history=conversation_history,
            include_sources=getattr(request, 'include_sources', False)
        )
        
        # Store user message
        history_service.add_message(
            session_id=session_id,
            role="user",
            content=request.message
        )
        
        # Store assistant response
        history_service.add_message(
            session_id=session_id,
            role="assistant",
            content=response.message,
            metadata={"sources_count": len(response.sources) if response.sources else 0}
        )
        
        # Return simplified response with session_id
        return {
            "message": response.message,
            "session_id": session_id,
            "timestamp": response.timestamp.isoformat(),
            "sources": response.sources if getattr(request, 'include_sources', False) else None
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_service_stats():
    """
    Get statistics about the RAG service, vector store, and chat history.
    """
    try:
        rag_service = get_rag_service()
        history_service = get_chat_history_service()
        
        rag_stats = rag_service.get_stats()
        memory_stats = history_service.get_memory_stats()
        
        return {
            "rag_service": rag_stats,
            "chat_history": memory_stats,
            "timestamp": datetime.now().isoformat(),
            "status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service statistics"
        )
