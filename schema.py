"""
Pydantic schemas for the Brikkle chatbot API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message schema."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request schema for chat endpoint with automatic session management."""
    message: str = Field(..., description="User's message", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Session ID (creates new if not provided)")
    include_sources: Optional[bool] = Field(
        default=False, 
        description="Whether to include source documents in response"
    )


class SourceDocument(BaseModel):
    """Source document schema for RAG responses."""
    content: str = Field(..., description="Relevant document content")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")
    score: Optional[float] = Field(None, description="Relevance score")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    message: str = Field(..., description="Assistant's response")
    sources: Optional[List[SourceDocument]] = Field(
        default=None, 
        description="Source documents used for the response"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    conversation_id: Optional[str] = Field(None, description="Unique conversation identifier")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class ChatSessionRequest(BaseModel):
    """Request schema for creating a new chat session."""
    pass  # No fields needed for simple session creation


class ChatSessionResponse(BaseModel):
    """Response schema for chat session operations."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    is_active: bool = Field(..., description="Whether session is still active")


class ChatHistoryRequest(BaseModel):
    """Request schema for chat with session management."""
    message: str = Field(..., description="User's message", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Session ID (creates new if not provided)")
    include_sources: Optional[bool] = Field(default=True, description="Whether to include source documents")


class ChatHistoryResponse(BaseModel):
    """Response schema for chat with session management."""
    message: str = Field(..., description="Assistant's response")
    session_id: str = Field(..., description="Session identifier")
    sources: Optional[List[SourceDocument]] = Field(default=None, description="Source documents used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class SessionListResponse(BaseModel):
    """Response schema for listing sessions."""
    sessions: List[ChatSessionResponse] = Field(..., description="List of chat sessions")
    total_count: int = Field(..., description="Total number of sessions")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
