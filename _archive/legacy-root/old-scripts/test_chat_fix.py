#!/usr/bin/env python3
"""
Quick Health Check Script for BroBro Chat Fix
Tests the chat API after applying the fixes
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_chat_api():
    """Test the chat endpoint with a simple message"""
    
    print("🔍 Testing BroBro Chat API...")
    print(f"📍 Endpoint: {API_URL}/api/chat\n")
    
    # Test payload
    payload = {
        "query": "Hello, are you working?",
        "n_results": 5,
        "conversation_history": []
    }
    
    try:
        print("📤 Sending test message...")
        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS! Chat API is working correctly")
            print(f"   - Answer length: {len(data.get('answer', ''))} characters")
            print(f"   - Sources found: {len(data.get('sources', []))}")
            print(f"   - Search time: {data.get('search_time_ms', 0):.2f}ms")
            print(f"   - Generation time: {data.get('generation_time_ms', 0):.2f}ms")
            print(f"   - Total time: {data.get('total_time_ms', 0):.2f}ms")
            
            return True
            
        elif response.status_code == 400:
            print("❌ FAILED - API Error 400")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            return False
            
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED - Cannot connect to backend")
        print(f"   Make sure the backend is running at {API_URL}")
        return False
        
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {str(e)}")
        return False


def test_health():
    """Test backend health endpoint"""
    
    print("\n🏥 Testing backend health...")
    
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot reach backend: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("BroBro Chat Fix - Health Check")
    print("=" * 60)
    print()
    
    # Test health first
    health_ok = test_health()
    
    if not health_ok:
        print("\n⚠️  Backend is not responding. Please:")
        print("   1. Start the backend: python web/backend/main.py")
        print("   2. Wait 5 seconds for initialization")
        print("   3. Run this script again")
        sys.exit(1)
    
    # Test chat API
    chat_ok = test_chat_api()
    
    print("\n" + "=" * 60)
    if chat_ok:
        print("✅ All tests passed! The fix is working correctly.")
        print("   You can now use the chat interface without errors.")
    else:
        print("❌ Tests failed. Check the errors above.")
        print("   If you need help, check BUG_FIX_IMAGE_SIZE_ERROR_2025-11-03.md")
    print("=" * 60)
    
    sys.exit(0 if chat_ok else 1)
