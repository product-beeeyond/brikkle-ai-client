"""
RAG (Retrieval-Augmented Generation) service for the Brikkle chatbot.
Handles document embedding, FAISS vector store, and document retrieval.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from schema import SourceDocument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG service that handles document embedding, FAISS vector store,
    and document retrieval for the Brikkle knowledge base.
    """
    
    def __init__(self, 
                 data_file_path: str = "data/data.txt",
                 vectorstore_path: str = "data/faiss_vectorstore",
                 api_key: Optional[str] = "AIzaSyCjIx6uWt01fHKwiaFY2HwJiXqL6ExO0_8",
                 embedding_model: str = "models/embedding-001"):
        """
        Initialize the RAG service.
        
        Args:
            data_file_path: Path to the knowledge base text file
            vectorstore_path: Path to save/load FAISS vectorstore
            api_key: Google API key (if not provided, will use env var)
            embedding_model: Name of the Google embedding model
        """
        self.data_file_path = data_file_path
        self.vectorstore_path = vectorstore_path
        self.embedding_model_name = embedding_model
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize components
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=self.api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize vectorstore
        self.vectorstore = None
        
        # Load or create vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> None:
        """Initialize the FAISS vector store, loading existing or creating new."""
        try:
            if self._vector_store_exists():
                logger.info("Loading existing FAISS vector store...")
                self._load_vector_store()
            else:
                logger.info("Creating new FAISS vector store...")
                self._create_vector_store()
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _vector_store_exists(self) -> bool:
        """Check if FAISS vectorstore directory exists."""
        return os.path.exists(self.vectorstore_path) and os.path.isdir(self.vectorstore_path)
    
    def _load_vector_store(self) -> None:
        """Load existing FAISS vectorstore."""
        try:
            self.vectorstore = FAISS.load_local(
                self.vectorstore_path, 
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Loaded vector store with {self.vectorstore.index.ntotal} documents")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            # If loading fails, create a new one
            logger.info("Creating new vector store due to loading error...")
            self._create_vector_store()
    
    def _create_vector_store(self) -> None:
        """Create new FAISS vector store from the knowledge base."""
        try:
            # Read and process the knowledge base
            documents = self._load_and_split_documents()
            
            if not documents:
                raise ValueError("No documents found in the knowledge base")
            
            # Create FAISS vectorstore from documents
            logger.info("Creating FAISS vectorstore from documents...")
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
            
            # Save to disk
            self._save_vector_store()
            
            logger.info(f"Created vector store with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def _load_and_split_documents(self) -> List[Document]:
        """Load and split the knowledge base document."""
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a single document
            doc = Document(
                page_content=content,
                metadata={"source": self.data_file_path, "title": "Brikkle Knowledge Base"}
            )
            
            # Split into chunks
            documents = self.text_splitter.split_documents([doc])
            
            # Add metadata to each chunk
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "chunk_id": i,
                    "chunk_size": len(doc.page_content)
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise
    
    def _save_vector_store(self) -> None:
        """Save FAISS vectorstore to disk."""
        try:
            # Ensure directory exists
            os.makedirs(self.vectorstore_path, exist_ok=True)
            
            # Save FAISS vectorstore
            self.vectorstore.save_local(self.vectorstore_path)
            
            logger.info("Vector store saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise
    
    def retrieve_documents(self, 
                          query: str, 
                          k: int = 5, 
                          score_threshold: float = 0.7) -> List[SourceDocument]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of relevant source documents
        """
        try:
            if self.vectorstore is None:
                raise ValueError("Vector store not initialized")
            
            # Search using LangChain FAISS similarity search with scores
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filter by score threshold and create source documents
            source_docs = []
            for doc, score in docs_with_scores:
                # FAISS returns distance scores (lower is better), convert to similarity
                similarity_score = 1 / (1 + score) if score > 0 else 1.0
                
                if similarity_score >= score_threshold:
                    source_doc = SourceDocument(
                        content=doc.page_content,
                        metadata=doc.metadata,
                        score=float(similarity_score)
                    )
                    source_docs.append(source_doc)
            
            logger.info(f"Retrieved {len(source_docs)} documents for query: {query[:50]}...")
            return source_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": self.vectorstore.index.ntotal if self.vectorstore else 0,
            "embedding_dimension": self.vectorstore.index.d if self.vectorstore else 0,
            "model_name": self.embedding_model_name,
            "index_type": "LangChain FAISS"
        }


# Global RAG service instance
rag_service = None


def get_rag_service() -> RAGService:
    """Get the global RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
