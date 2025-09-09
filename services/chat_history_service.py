"""
Chat history service for managing conversation sessions.
Stores and retrieves chat history in memory for the Brikkle chatbot.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from schema import ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatHistoryService:
    """
    Service for managing chat history and conversation sessions.
    Stores conversations in memory with automatic cleanup.
    """
    
    def __init__(self):
        """
        Initialize the chat history service with in-memory storage.
        """
        # In-memory storage for sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Session timeout (24 hours)
        self.session_timeout = timedelta(hours=24)
        
        # Maximum messages to keep per session (for LLM context)
        self.max_messages_per_session = 5
        
        logger.info("Chat history service initialized with in-memory storage")
    
    def create_session(self) -> str:
        """
        Create a new chat session.
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "messages": []
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"Created new chat session: {session_id}")
        return session_id
    
    def add_message(self, 
                   session_id: str, 
                   role: str, 
                   content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a message to a chat session.
        Automatically limits to max_messages_per_session (5) for LLM context.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if session_id not in self.sessions:
                logger.error(f"Session not found: {session_id}")
                return False
            
            session_data = self.sessions[session_id]
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
            
            # Add message to session
            session_data["messages"].append(message)
            session_data["last_activity"] = datetime.now()
            
            # Keep only the last max_messages_per_session messages
            if len(session_data["messages"]) > self.max_messages_per_session:
                session_data["messages"] = session_data["messages"][-self.max_messages_per_session:]
                logger.info(f"Trimmed messages to last {self.max_messages_per_session} for session {session_id}")
            
            logger.info(f"Added message to session {session_id} (total: {len(session_data['messages'])})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False
    
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Get chat history for a session.
        Returns the last 5 messages by default (for LLM context).
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (defaults to max_messages_per_session)
            
        Returns:
            List of chat messages
        """
        try:
            if session_id not in self.sessions:
                logger.warning(f"Session not found: {session_id}")
                return []
            
            session_data = self.sessions[session_id]
            messages = session_data.get("messages", [])
            
            # Use default limit if not specified
            if limit is None:
                limit = self.max_messages_per_session
            
            # Apply limit if specified
            if limit and limit > 0:
                messages = messages[-limit:]
            
            # Convert to ChatMessage objects
            chat_messages = []
            for msg in messages:
                chat_message = ChatMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
                chat_messages.append(chat_message)
            
            logger.info(f"Retrieved {len(chat_messages)} messages for session {session_id}")
            return chat_messages
            
        except Exception as e:
            logger.error(f"Error retrieving session history {session_id}: {e}")
            return []
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information dictionary or None
        """
        try:
            if session_id not in self.sessions:
                return None
            
            session_data = self.sessions[session_id]
            
            return {
                "session_id": session_data["session_id"],
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
                "message_count": len(session_data.get("messages", [])),
                "is_active": self._is_session_active(session_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting session info {session_id}: {e}")
            return None
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List chat sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session information dictionaries
        """
        try:
            sessions = []
            
            # Get all sessions from memory
            for session_id, session_data in self.sessions.items():
                try:
                    session_info = {
                        "session_id": session_data["session_id"],
                        "created_at": session_data["created_at"].isoformat(),
                        "last_activity": session_data["last_activity"].isoformat(),
                        "message_count": len(session_data.get("messages", [])),
                        "is_active": self._is_session_active(session_data)
                    }
                    sessions.append(session_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing session {session_id}: {e}")
                    continue
            
            # Sort by last activity (most recent first)
            sessions.sort(key=lambda x: x["last_activity"], reverse=True)
            
            # Apply limit
            if limit > 0:
                sessions = sessions[:limit]
            
            logger.info(f"Listed {len(sessions)} sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session from memory.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                return True
            else:
                logger.warning(f"Session not found: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def cleanup_old_sessions(self, days: int = 7) -> int:
        """
        Clean up old inactive sessions from memory.
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            deleted_count = 0
            sessions_to_delete = []
            
            # Find sessions to delete
            for session_id, session_data in self.sessions.items():
                try:
                    last_activity = session_data["last_activity"]
                    
                    if last_activity < cutoff_time:
                        sessions_to_delete.append(session_id)
                        
                except Exception as e:
                    logger.warning(f"Error processing session {session_id}: {e}")
                    continue
            
            # Delete old sessions
            for session_id in sessions_to_delete:
                del self.sessions[session_id]
                deleted_count += 1
                logger.info(f"Cleaned up old session: {session_id}")
            
            logger.info(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0
    
    def _is_session_active(self, session_data: Dict[str, Any]) -> bool:
        """Check if session is still active (within timeout)."""
        try:
            last_activity = session_data["last_activity"]
            return datetime.now() - last_activity < self.session_timeout
        except Exception:
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about in-memory storage.
        
        Returns:
            Dictionary with memory usage statistics
        """
        try:
            total_sessions = len(self.sessions)
            total_messages = sum(len(session.get("messages", [])) for session in self.sessions.values())
            active_sessions = sum(1 for session in self.sessions.values() if self._is_session_active(session))
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "max_messages_per_session": self.max_messages_per_session,
                "storage_type": "in_memory"
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {}


# Global chat history service instance
chat_history_service = None


def get_chat_history_service() -> ChatHistoryService:
    """Get the global chat history service instance."""
    global chat_history_service
    if chat_history_service is None:
        chat_history_service = ChatHistoryService()
    return chat_history_service
