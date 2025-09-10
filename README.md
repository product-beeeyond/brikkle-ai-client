# Brikkle Chatbot API

A RAG-powered chatbot for Brikkle, Nigeria's first blockchain-powered real estate investment platform. This FastAPI application uses LangChain, Google Generative AI, and FAISS for intelligent document retrieval and response generation.

## Features

- **RAG System**: Retrieval-Augmented Generation using FAISS vector search
- **Google Generative AI**: Powered by Gemini Pro for natural language understanding and embeddings
- **LangChain Integration**: ChatPromptTemplate and Google embedding models
- **Persistent Vector Store**: FAISS index that persists between runs
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Comprehensive Error Handling**: Robust error handling and logging

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

<!-- pip3 install faiss-cpu==1.10.0 --only-binary=:all:
pip3 install -r requirements.txt -->

### 2. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` and add your Google Generative AI API key:

```env
GOOGLE_API_KEY=your_google_generative_ai_api_key_here
```

### 3. Run the Application

```bash
python app.py
```
<!-- python3 app.py -->
The API will be available at `http://localhost:8000`

### 4. Access API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat` - Main chat endpoint with full conversation support
- `POST /api/v1/chat/simple` - Simplified chat endpoint for basic queries
- `GET /api/v1/conversation/summary` - Get conversation summary

### Utility Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Service statistics
- `GET /` - API information

## Usage Examples

### Simple Chat Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/simple" \
     -H "Content-Type: application/json" \
     -d '"How does Brikkle work?"'
```

### Full Chat Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the minimum investment amount?",
       "conversation_history": [],
       "include_sources": true
     }'
```

### Python Client Example

```python
import requests

# Simple chat
response = requests.post(
    "http://localhost:8000/api/v1/chat/simple",
    json="How do I create an account on Brikkle?"
)
print(response.json())

# Full chat with conversation history
chat_data = {
    "message": "What documents do I need for verification?",
    "conversation_history": [
        {"role": "user", "content": "How do I create an account?"},
        {"role": "assistant", "content": "You can create an account at app.brikkle.ai..."}
    ],
    "include_sources": True
}

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json=chat_data
)
print(response.json())
```

## Architecture

### Components

1. **RAG Service** (`service.py`): Handles document embedding and FAISS vector search
2. **Chat Service** (`chat_service.py`): Manages conversation and response generation
3. **API Routes** (`routes.py`): FastAPI endpoints and request handling
4. **Schemas** (`schema.py`): Pydantic models for request/response validation
5. **Main App** (`app.py`): FastAPI application configuration and startup

### RAG Pipeline

1. **Document Processing**: The knowledge base (`data/data.txt`) is split into chunks
2. **Embedding Generation**: Text chunks are embedded using Google Generative AI embedding models
3. **Vector Storage**: Embeddings are stored in a FAISS index for fast similarity search
4. **Retrieval**: User queries are embedded and similar documents are retrieved
5. **Generation**: Retrieved context is used with Google Generative AI to generate responses

### Vector Store Persistence

- FAISS vectorstore is saved to `data/faiss_vectorstore/` directory
- The vectorstore includes both the FAISS index and document metadata
- If the directory exists, the system will load it instead of re-embedding
- To force re-embedding, delete the existing vectorstore directory

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Generative AI API key | Required |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `EMBEDDING_MODEL` | Google embedding model | `models/embedding-001` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `MAX_RETRIEVAL_DOCS` | Max documents to retrieve | `5` |
| `SIMILARITY_THRESHOLD` | Similarity threshold | `0.6` |

### Customization

You can customize the chatbot's behavior by modifying:

- **System Prompt**: Edit the prompt in `chat_service.py`
- **Retrieval Parameters**: Adjust `k` and `score_threshold` in the RAG service
- **Model Settings**: Change temperature, max tokens, etc. in the chat service
- **Chunking Strategy**: Modify text splitter parameters in the RAG service

## Development

### Project Structure

```
brikkle/
├── app.py                 # FastAPI application
├── routes.py              # API routes
├── schema.py              # Pydantic schemas
├── service.py             # RAG service
├── chat_service.py        # Chat service
├── requirements.txt       # Dependencies
├── env.example           # Environment variables example
├── README.md             # This file
└── data/
    ├── data.txt          # Knowledge base
    └── faiss_vectorstore/ # FAISS vectorstore (generated)
```

### Adding New Knowledge

1. Update `data/data.txt` with new information
2. Delete the existing `data/faiss_vectorstore/` directory
3. Restart the application to re-embed the documents

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test simple chat
curl -X POST "http://localhost:8000/api/v1/chat/simple" \
     -H "Content-Type: application/json" \
     -d '"What is Brikkle?"'
```

## Production Deployment

### Security Considerations

1. Set proper CORS origins in production
2. Use environment variables for all sensitive data
3. Implement rate limiting
4. Add authentication/authorization if needed
5. Use HTTPS in production

### Performance Optimization

1. Use GPU-accelerated FAISS for large datasets
2. Implement caching for frequent queries
3. Use a production ASGI server like Gunicorn
4. Consider load balancing for high traffic

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **Google API Key Error**: Ensure `GOOGLE_API_KEY` is set correctly
2. **FAISS Index Error**: Delete existing vectorstore directory to force re-creation
3. **Memory Issues**: Reduce chunk size or adjust embedding model parameters
4. **Slow Responses**: Check network connectivity to Google AI services

### Logs

The application logs important events. Check the console output for:
- Service initialization status
- RAG service statistics
- Chat request processing
- Error messages

## License

This project is part of the Brikkle platform. Please refer to Brikkle's terms of service for usage rights.
