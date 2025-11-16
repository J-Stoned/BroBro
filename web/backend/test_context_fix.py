"""
Test script for Claude API context fix
Tests conversation history validation with and without tool blocks
"""

import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"

def test_simple_conversation():
    """Test 1: Simple text-only conversation history"""
    print("\n" + "="*60)
    print("TEST 1: Simple Text-Only Conversation")
    print("="*60)
    
    payload = {
        "query": "How do I send an SMS in GHL?",
        "conversation_history": [
            {
                "role": "user",
                "content": "Tell me about workflows"
            },
            {
                "role": "assistant",
                "content": "Workflows in GHL are powerful automation sequences that help you nurture leads and automate tasks."
            }
        ],
        "n_results": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS")
            print(f"Answer length: {len(result['answer'])} chars")
            print(f"Search time: {result['search_time_ms']}ms")
            print(f"Generation time: {result['generation_time_ms']}ms")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_with_tool_blocks():
    """Test 2: Conversation with tool_use/tool_result blocks (should be cleaned)"""
    print("\n" + "="*60)
    print("TEST 2: Conversation with Tool Blocks (Should be cleaned)")
    print("="*60)
    
    # Simulating what the API might return with tool use
    payload = {
        "query": "What about conditions in workflows?",
        "conversation_history": [
            {
                "role": "user",
                "content": "search for email automation"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I'll search for information about email automation."
                    },
                    {
                        "type": "tool_use",
                        "id": "toolu_test_123",
                        "name": "search_kb",
                        "input": {"query": "email automation"}
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_test_123",
                        "content": "Found 10 results about email automation..."
                    }
                ]
            },
            {
                "role": "assistant",
                "content": "Based on the search results, GHL email automation allows you to..."
            }
        ],
        "n_results": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Tool blocks were handled properly")
            print(f"Answer length: {len(result['answer'])} chars")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_broken_tool_blocks():
    """Test 3: Broken tool blocks (mismatched IDs)"""
    print("\n" + "="*60)
    print("TEST 3: Broken Tool Blocks (Mismatched IDs)")
    print("="*60)
    
    payload = {
        "query": "Tell me more",
        "conversation_history": [
            {
                "role": "user",
                "content": "test query"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Let me search for that."
                    },
                    {
                        "type": "tool_use",
                        "id": "toolu_correct_id",
                        "name": "search",
                        "input": {}
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_wrong_id",  # MISMATCHED!
                        "content": "Results..."
                    }
                ]
            }
        ],
        "n_results": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Broken tool blocks were cleaned/removed")
            print(f"Answer length: {len(result['answer'])} chars")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_orphaned_tool_result():
    """Test 4: Orphaned tool_result (no previous tool_use)"""
    print("\n" + "="*60)
    print("TEST 4: Orphaned Tool Result (No Previous Tool Use)")
    print("="*60)
    
    payload = {
        "query": "Continue",
        "conversation_history": [
            {
                "role": "user",
                "content": "search for something"
            },
            {
                "role": "user",  # Should be assistant but isn't!
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_orphan",
                        "content": "Some results"
                    },
                    {
                        "type": "text",
                        "text": "Here are the results"
                    }
                ]
            }
        ],
        "n_results": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Orphaned tool_result was cleaned")
            print(f"Answer length: {len(result['answer'])} chars")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("CLAUDE API CONTEXT FIX - TEST SUITE")
    print("="*60)
    print("Testing conversation history validation and cleaning...")
    print(f"Backend URL: {BASE_URL}")
    
    results = []
    
    # Run all tests
    results.append(("Simple Conversation", test_simple_conversation()))
    results.append(("With Tool Blocks", test_with_tool_blocks()))
    results.append(("Broken Tool Blocks", test_broken_tool_blocks()))
    results.append(("Orphaned Tool Result", test_orphaned_tool_result()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The fix is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        print("\nTroubleshooting:")
        print("1. Make sure backend server is running on http://localhost:8000")
        print("2. Check that ANTHROPIC_API_KEY is set in .env")
        print("3. Review backend logs for validation warnings")
        print("4. Try setting CLAUDE_FORCE_TEXT_ONLY=true in .env")


if __name__ == "__main__":
    main()