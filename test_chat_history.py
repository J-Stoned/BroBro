#!/usr/bin/env python3
"""
Test script for Chat History Feature
Tests all endpoints to verify implementation
"""

import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/conversations"
SESSION_ID = str(uuid4())

def test_create_conversation():
    """Test creating a conversation"""
    print("\n1. Testing CREATE conversation...")
    payload = {
        "session_id": SESSION_ID,
        "title": "Test Conversation"
    }

    response = requests.post(BASE_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            conversation_id = data['data']['id']
            print(f"   SUCCESS: Created conversation {conversation_id}")
            return conversation_id
        else:
            print(f"   FAILED: {data.get('error')}")
            return None
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return None

def test_list_conversations(session_id):
    """Test listing conversations"""
    print("\n2. Testing LIST conversations...")
    params = {
        "session_id": session_id,
        "limit": 10,
        "offset": 0
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            count = len(data.get('conversations', []))
            print(f"   SUCCESS: Found {count} conversations")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def test_get_conversation(conversation_id):
    """Test getting a conversation"""
    print(f"\n3. Testing GET conversation {conversation_id}...")

    response = requests.get(f"{BASE_URL}/{conversation_id}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   SUCCESS: Retrieved conversation")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def test_add_message(conversation_id):
    """Test adding a message"""
    print(f"\n4. Testing ADD message to {conversation_id}...")
    payload = {
        "role": "user",
        "content": "Hello, this is a test message!",
        "metadata": {"source": "test_script"}
    }

    response = requests.post(f"{BASE_URL}/{conversation_id}/messages", json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   SUCCESS: Added message")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def test_get_messages(conversation_id):
    """Test getting messages"""
    print(f"\n5. Testing GET messages from {conversation_id}...")

    response = requests.get(f"{BASE_URL}/{conversation_id}/messages")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            count = len(data.get('data', {}).get('messages', []))
            print(f"   SUCCESS: Retrieved {count} messages")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def test_update_conversation(conversation_id):
    """Test updating a conversation"""
    print(f"\n6. Testing UPDATE conversation {conversation_id}...")
    payload = {
        "title": "Updated Test Conversation"
    }

    response = requests.put(f"{BASE_URL}/{conversation_id}", json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   SUCCESS: Updated conversation title")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def test_delete_conversation(conversation_id):
    """Test deleting a conversation"""
    print(f"\n7. Testing DELETE conversation {conversation_id}...")

    response = requests.delete(f"{BASE_URL}/{conversation_id}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   SUCCESS: Deleted conversation")
            return True
        else:
            print(f"   FAILED: {data.get('error')}")
            return False
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        return False

def main():
    print("=" * 60)
    print("Chat History Feature - API Test Suite")
    print("=" * 60)
    print(f"Session ID: {SESSION_ID}")
    print(f"Base URL: {BASE_URL}")

    try:
        # Test sequence
        conversation_id = test_create_conversation()
        if not conversation_id:
            print("\nFAILED: Could not create conversation, stopping tests")
            return

        test_list_conversations(SESSION_ID)
        test_get_conversation(conversation_id)
        test_add_message(conversation_id)
        test_get_messages(conversation_id)
        test_update_conversation(conversation_id)
        test_delete_conversation(conversation_id)

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except requests.ConnectionError:
        print("\nERROR: Could not connect to backend at http://localhost:8000")
        print("Make sure the backend is running: python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()
