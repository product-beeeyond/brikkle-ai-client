"""
Chat service for the Brikkle chatbot using LangChain and Google Generative AI.
Handles conversation management and response generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from .service import get_rag_service
from schema import ChatMessage, ChatResponse, SourceDocument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat service that handles conversation management and response generation
    using LangChain and Google Generative AI.
    """
    
    def __init__(self, api_key: Optional[str] = "AIzaSyCjIx6uWt01fHKwiaFY2HwJiXqL6ExO0_8",):
        """
        Initialize the chat service.
        
        Args:
            api_key: Google Generative AI API key (if not provided, will use env var)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize the language model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # Initialize RAG service
        self.rag_service = get_rag_service()
        
        # Create the chat prompt template
        self.chat_prompt = self._create_chat_prompt()
        
        logger.info("Chat service initialized successfully")
    
    def _create_chat_prompt(self) -> ChatPromptTemplate:
        """Create the chat prompt template for the Brikkle chatbot."""
        
        system_prompt = """You are a helpful AI assistant for Brikkle, Nigeria's first blockchain-powered real estate investment platform. 

Your role is to help users understand:
- How Brikkle works and its core value proposition
- Investment opportunities and property tokenization
- Account setup, verification, and payment processes
- Property due diligence and investment strategies
- Platform features, security, and compliance
- Technical support and troubleshooting

Guidelines:
1. Always be helpful, accurate, and professional
2. Use the provided context from Brikkle's knowledge base to answer questions
3. If you don't have specific information, clearly state that and suggest contacting support
4. Focus on Nigerian real estate investment context
5. Explain complex blockchain and investment concepts in simple terms
6. Always mention relevant minimum investment amounts, fees, and requirements
7. Encourage users to verify information and do their own research

Context from Brikkle Knowledge Base:
{context}

Previous conversation:
{chat_history}

User's question: {question}

Please provide a helpful and accurate response based on the context above."""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
    
    def _format_chat_history(self, conversation_history: List[ChatMessage]) -> str:
        """Format conversation history for the prompt."""
        if not conversation_history:
            return "No previous conversation."
        
        # Keep only the last 5 messages for context to avoid token limits
        recent_messages = conversation_history[-5:]
        
        formatted_history = []
        for msg in recent_messages:
            if msg.role == "user":
                formatted_history.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted_history.append(f"Assistant: {msg.content}")
        
        return "\n".join(formatted_history)
    
    def _format_context(self, source_docs: List[SourceDocument]) -> str:
        """Format retrieved documents as context for the prompt."""
        if not source_docs:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(source_docs, 1):
            context_parts.append(f"Source {i} (Relevance: {doc.score:.2f}):\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def generate_response(self, 
                         message: str, 
                         conversation_history: List[ChatMessage] = None,
                         include_sources: bool = True) -> ChatResponse:
        """
        Generate a response to the user's message using RAG.
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages (limited to last 5 for context)
            include_sources: Whether to include source documents in response
            
        Returns:
            ChatResponse with the generated message and sources
        """
        try:
            # Retrieve relevant documents
            logger.info(f"Retrieving documents for query: {message[:50]}...")
            source_docs = self.rag_service.retrieve_documents(
                query=message,
                k=5,
                score_threshold=0.6
            )
            
            # Format context and chat history
            context = self._format_context(source_docs)
            chat_history = self._format_chat_history(conversation_history or [])
            
            # Create the prompt
            prompt = self.chat_prompt.format(
                context=context,
                chat_history=chat_history,
                question=message
            )
            
            # Generate response
            logger.info("Generating response with Google Generative AI...")
            response = self.llm.invoke(prompt)
            
            # Extract the response content
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Create the chat response
            chat_response = ChatResponse(
                message=response_content,
                sources=source_docs if include_sources else None,
                timestamp=datetime.now()
            )
            
            logger.info("Response generated successfully")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Return a fallback response
            return ChatResponse(
                message="I apologize, but I'm experiencing technical difficulties. Please try again later or contact Brikkle support for assistance.",
                sources=None,
                timestamp=datetime.now()
            )
    
    def get_conversation_summary(self, conversation_history: List[ChatMessage]) -> str:
        """Generate a summary of the conversation."""
        if not conversation_history:
            return "No conversation history available."
        
        user_messages = [msg.content for msg in conversation_history if msg.role == "user"]
        if not user_messages:
            return "No user messages in conversation history."
        
        # Simple summary based on user messages
        topics = []
        for msg in user_messages:
            if any(keyword in msg.lower() for keyword in ["investment", "property", "token"]):
                topics.append("Investment and Property")
            elif any(keyword in msg.lower() for keyword in ["account", "verification", "kyc"]):
                topics.append("Account Setup")
            elif any(keyword in msg.lower() for keyword in ["payment", "deposit", "withdraw"]):
                topics.append("Payment and Transactions")
            elif any(keyword in msg.lower() for keyword in ["help", "support", "problem"]):
                topics.append("Support and Help")
        
        if topics:
            unique_topics = list(set(topics))
            return f"Conversation covered: {', '.join(unique_topics)}"
        else:
            return "General conversation about Brikkle platform"


# Global chat service instance
chat_service = None


def get_chat_service() -> ChatService:
    """Get the global chat service instance."""
    global chat_service
    if chat_service is None:
        chat_service = ChatService()
    return chat_service
