"""
Simple test script for the Brikkle Chatbot API.
Run this after starting the server to test the endpoints.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_simple_chat():
    """Test the simple chat endpoint."""
    print("\nTesting simple chat endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/chat/simple",
            json="What is Brikkle?"
        )
        if response.status_code == 200:
            print("✅ Simple chat test passed")
            data = response.json()
            print(f"Response: {data['message'][:100]}...")
        else:
            print(f"❌ Simple chat failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Simple chat error: {e}")

def test_full_chat():
    """Test the full chat endpoint."""
    print("\nTesting full chat endpoint...")
    try:
        chat_data = {
            "message": "How do I create an account on Brikkle?",
            "conversation_history": [],
            "include_sources": True
        }
        
        response = requests.post(
            f"{API_BASE}/chat",
            json=chat_data
        )
        
        if response.status_code == 200:
            print("✅ Full chat test passed")
            data = response.json()
            print(f"Response: {data['message'][:100]}...")
            if data.get('sources'):
                print(f"Sources found: {len(data['sources'])}")
        else:
            print(f"❌ Full chat failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Full chat error: {e}")

def test_stats():
    """Test the stats endpoint."""
    print("\nTesting stats endpoint...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            print("✅ Stats test passed")
            data = response.json()
            print(f"RAG Service Stats: {data['rag_service']}")
        else:
            print(f"❌ Stats test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats test error: {e}")

def test_conversation():
    """Test conversation with history."""
    print("\nTesting conversation with history...")
    try:
        # First message
        chat_data = {
            "message": "What is the minimum investment amount?",
            "conversation_history": [],
            "include_sources": True
        }
        
        response1 = requests.post(f"{API_BASE}/chat", json=chat_data)
        
        if response1.status_code == 200:
            data1 = response1.json()
            print("✅ First message successful")
            
            # Second message with history
            chat_data2 = {
                "message": "What documents do I need for verification?",
                "conversation_history": [
                    {"role": "user", "content": "What is the minimum investment amount?"},
                    {"role": "assistant", "content": data1['message'][:100] + "..."}
                ],
                "include_sources": True
            }
            
            response2 = requests.post(f"{API_BASE}/chat", json=chat_data2)
            
            if response2.status_code == 200:
                print("✅ Conversation with history test passed")
                data2 = response2.json()
                print(f"Response: {data2['message'][:100]}...")
            else:
                print(f"❌ Conversation test failed: {response2.status_code}")
        else:
            print(f"❌ First message failed: {response1.status_code}")
            
    except Exception as e:
        print(f"❌ Conversation test error: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Brikkle Chatbot API Tests")
    print("=" * 50)
    print("Note: This test uses Google Generative AI embeddings")
    print("Make sure GOOGLE_API_KEY is set in your environment")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(3)  # Give more time for Google embeddings initialization
    
    # Run tests
    test_health()
    test_simple_chat()
    test_full_chat()
    test_stats()
    test_conversation()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\nTo run the server:")
    print("python app.py")
    print("\nTo view API documentation:")
    print(f"Open {BASE_URL}/docs in your browser")

if __name__ == "__main__":
    main()
