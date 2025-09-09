"""
Services package for the Brikkle chatbot.
Contains all service modules for RAG, chat, and history management.
"""

from .service import get_rag_service
from .chat_service import get_chat_service
from .chat_history_service import get_chat_history_service

__all__ = [
    'get_rag_service',
    'get_chat_service', 
    'get_chat_history_service'
]
