#!/usr/bin/env python3
"""
Test script for the simplified Brikkle chatbot API.
Tests the single chat endpoint with automatic session management.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_MESSAGES = [
    "Hello, what is Brikkle?",
    "How do I invest in real estate through Brikkle?",
    "What are the minimum investment amounts?",
    "How does property tokenization work?",
    "What fees are involved?"
]

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_endpoint():
    """Test the simplified chat endpoint with session management."""
    print("\n💬 Testing chat endpoint with session management...")
    
    session_id = None
    
    for i, message in enumerate(TEST_MESSAGES, 1):
        print(f"\n--- Test {i}: {message[:50]}... ---")
        
        # Prepare request
        request_data = {
            "message": message,
            "include_sources": False
        }
        
        # Add session_id if we have one (for continuation)
        if session_id:
            request_data["session_id"] = session_id
        
        try:
            # Send request
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract session_id for next request
                if "session_id" in data:
                    session_id = data["session_id"]
                    print(f"📝 Session ID: {session_id[:8]}...")
                
                print(f"🤖 Bot Response: {data['message'][:100]}...")
                print(f"⏰ Timestamp: {data['timestamp']}")
                
                if data.get('sources'):
                    print(f"📚 Sources: {len(data['sources'])} documents")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return False
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n✅ All chat tests passed! Final session ID: {session_id[:8] if session_id else 'None'}...")
    return True

def test_stats_endpoint():
    """Test the stats endpoint."""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved successfully")
            print(f"📈 RAG Service Status: {data['status']}")
            if 'rag_service' in data:
                rag_stats = data['rag_service']
                print(f"📄 Total Documents: {rag_stats.get('total_documents', 'N/A')}")
                print(f"🔍 Vector Store Size: {rag_stats.get('vector_store_size', 'N/A')}")
            return True
        else:
            print(f"❌ Stats request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_new_session_creation():
    """Test that a new session is created when no session_id is provided."""
    print("\n🆕 Testing new session creation...")
    
    try:
        # First request without session_id
        request_data = {
            "message": "Hello, I'm starting a new conversation",
            "include_sources": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            
            if session_id:
                print(f"✅ New session created: {session_id[:8]}...")
                
                # Second request with the same session_id to test continuation
                request_data["session_id"] = session_id
                request_data["message"] = "This is a follow-up message in the same session"
                
                response2 = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get("session_id") == session_id:
                        print(f"✅ Session continuation works: {session_id[:8]}...")
                        
                        # Third request to test that context is maintained (last 5 messages)
                        request_data["message"] = "What was my previous question?"
                        response3 = requests.post(
                            f"{API_BASE_URL}/chat",
                            json=request_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if response3.status_code == 200:
                            data3 = response3.json()
                            if data3.get("session_id") == session_id:
                                print(f"✅ Context maintained across multiple messages: {session_id[:8]}...")
                                return True
                            else:
                                print(f"❌ Session ID changed on third request")
                                return False
                        else:
                            print(f"❌ Third request failed: {response3.status_code}")
                            return False
                    else:
                        print(f"❌ Session ID changed unexpectedly")
                        return False
                else:
                    print(f"❌ Second request failed: {response2.status_code}")
                    return False
            else:
                print(f"❌ No session_id returned")
                return False
        else:
            print(f"❌ First request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Session creation test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Brikkle Chatbot API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Endpoint", test_chat_endpoint),
        ("Stats Endpoint", test_stats_endpoint),
        ("Session Management", test_new_session_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simplified API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server and try again.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
