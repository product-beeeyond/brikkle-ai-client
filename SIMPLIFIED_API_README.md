# Brikkle Chatbot - Simplified API

This document describes the simplified Brikkle chatbot API that has been streamlined to use only one main endpoint with automatic session management.

## 🎯 Key Features

- **Single Chat Endpoint**: Only one main endpoint for all chat interactions
- **Automatic Session Management**: Sessions are created automatically on first request
- **Context Limitation**: Only keeps the last 5 messages for context to avoid token limits
- **Simplified Frontend Integration**: Easy to integrate with any frontend framework

## 📡 API Endpoints

### 1. Chat Endpoint (Main)
**POST** `/api/v1/chat`

The primary endpoint for all chat interactions. Automatically manages sessions and conversation history.

#### Request Body
```json
{
  "message": "How do I invest in real estate through Brikkle?",
  "session_id": "optional-session-id",  // Optional - creates new session if not provided
  "include_sources": false              // Optional - defaults to false
}
```

#### Response
```json
{
  "message": "Brikkle is Nigeria's first blockchain-powered real estate investment platform...",
  "session_id": "uuid-session-id",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "sources": null  // Only included if include_sources is true
}
```

### 2. Health Check
**GET** `/api/v1/health`

Check if the API is running and healthy.

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

### 3. Service Stats
**GET** `/api/v1/stats`

Get statistics about the RAG service and vector store.

#### Response
```json
{
  "rag_service": {
    "total_documents": 150,
    "vector_store_size": "2.5MB"
  },
  "timestamp": "2024-01-15T10:30:00.000Z",
  "status": "operational"
}
```

## 🔄 How Session Management Works

1. **First Request**: When you send a message without a `session_id`, the API automatically creates a new session
2. **Session Continuation**: Include the returned `session_id` in subsequent requests to continue the conversation
3. **In-Memory Storage**: Chat history is stored in server memory (not files) for better performance
4. **Context Limitation**: Only the last 5 messages are kept in memory and used for LLM context
5. **Session Persistence**: Sessions are maintained until the page is refreshed or manually cleared
6. **Frontend Storage**: The frontend stores the `session_id` in localStorage to persist across page interactions
7. **Automatic Cleanup**: Old sessions are automatically cleaned up from memory after 24 hours

## 💻 Frontend Integration

### JavaScript Example
```javascript
class BrikkleChat {
    constructor() {
        this.sessionId = localStorage.getItem('brikkle_session_id');
        this.apiUrl = 'http://localhost:8000/api/v1';
    }
    
    async sendMessage(message) {
        const requestBody = {
            message: message,
            include_sources: false
        };
        
        // Add session_id if we have one
        if (this.sessionId) {
            requestBody.session_id = this.sessionId;
        }
        
        const response = await fetch(`${this.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        // Store session_id for future requests (persists until page refresh)
        if (data.session_id) {
            this.sessionId = data.session_id;
            localStorage.setItem('brikkle_session_id', this.sessionId);
        }
        
        return data.message;
    }
}
```

### React Example
```jsx
import { useState, useEffect } from 'react';

function BrikkleChat() {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    
    useEffect(() => {
        // Load session from localStorage
        const storedSessionId = localStorage.getItem('brikkle_session_id');
        if (storedSessionId) {
            setSessionId(storedSessionId);
        }
    }, []);
    
    const sendMessage = async () => {
        if (!input.trim()) return;
        
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        
        const requestBody = {
            message: input,
            include_sources: false
        };
        
        if (sessionId) {
            requestBody.session_id = sessionId;
        }
        
        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            
            if (data.session_id) {
                setSessionId(data.session_id);
                localStorage.setItem('brikkle_session_id', data.session_id);
            }
            
            setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
        } catch (error) {
            console.error('Error:', error);
        }
    };
    
    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask about Brikkle..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}
```

## 🧪 Testing

Run the test script to verify the API is working:

```bash
python test_simplified_api.py
```

This will test:
- Health check endpoint
- Chat endpoint with session management
- Stats endpoint
- New session creation and continuation

## 🚀 Running the API

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   cp env.example .env
   # Edit .env with your Google API key
   ```

3. **Start the Server**:
   ```bash
   python app.py
   ```

4. **Test with Frontend**:
   Open `simple_frontend_example.html` in your browser

## 📝 Key Changes from Previous Version

### Removed Endpoints
- `/api/v1/chat/simple` - No longer needed
- `/api/v1/sessions` - Session management is now automatic
- `/api/v1/sessions/{session_id}` - Not needed for basic chat
- `/api/v1/sessions/{session_id}/history` - History is managed internally
- `/api/v1/chat/history` - Replaced by main chat endpoint
- `/api/v1/conversation/summary` - Removed for simplicity
- `/api/v1/cleanup/sessions` - Cleanup happens automatically

### Simplified Request/Response
- **Request**: Only needs `message`, optional `session_id` and `include_sources`
- **Response**: Returns `message`, `session_id`, `timestamp`, and optional `sources`
- **Session Management**: Completely automatic - no manual session creation needed

### Benefits
- **Easier Integration**: Frontend developers only need to know one endpoint
- **Automatic Context**: Last 5 messages are automatically used for context
- **Session Persistence**: Sessions are automatically created and managed
- **Reduced Complexity**: No need to manage conversation history manually

## 🔧 Configuration

The API uses the same configuration as before:
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)

## 📚 What the Chatbot Can Help With

The Brikkle chatbot can assist with:
- **Investment Opportunities**: Property tokenization and investment options
- **Account Setup**: Registration, verification, and KYC processes
- **Payment Processes**: Deposits, withdrawals, and transaction fees
- **Property Due Diligence**: Research and analysis of investment properties
- **Technical Support**: Platform features and troubleshooting
- **General Information**: About Brikkle's services and blockchain technology

## 🛡️ Security Notes

- Sessions are stored in server memory (not files) for better security
- No sensitive data is logged in chat history
- API keys should be kept secure and not exposed to frontend
- Consider implementing rate limiting for production use
- Sessions automatically expire after 24 hours of inactivity
- Chat history is automatically cleaned up from memory

## 🔄 Session Persistence Details

### How Sessions Persist
- **Page Interactions**: Sessions are maintained across all page interactions (clicking, typing, etc.)
- **Browser Storage**: Session ID is stored in localStorage and persists until:
  - Page is refreshed/reloaded
  - Browser is closed and reopened
  - localStorage is manually cleared
  - "New Chat" button is clicked
- **Server Storage**: Chat history is stored in server memory (not files) and linked to the session ID
- **Memory Management**: Only the last 5 messages are kept in memory for LLM context

### Session Lifecycle
1. **Page Load**: Check localStorage for existing session ID
2. **First Message**: Create new session if none exists
3. **Subsequent Messages**: Continue using existing session ID
4. **Page Refresh**: Session ID is cleared from localStorage (new session will be created)
5. **Manual Reset**: "New Chat" button clears current session

### Benefits of This Approach
- **Conversation Continuity**: Users can have long conversations without losing context
- **Fresh Start on Refresh**: Each page load starts with a clean slate
- **Manual Control**: Users can start new conversations when needed
- **Memory Efficient**: Only last 5 messages are kept in memory for AI context
- **Fast Performance**: In-memory storage is faster than file-based storage
- **Automatic Cleanup**: Old sessions are automatically removed from memory
