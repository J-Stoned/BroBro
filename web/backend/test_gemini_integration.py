#!/usr/bin/env python3
"""
Quick Test Script for Gemini File Search Integration
Run this after your upload completes to test the integration
"""

import os
import sys

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_gemini_integration():
    print("=" * 60)
    print("  GEMINI FILE SEARCH INTEGRATION TEST")
    print("=" * 60)
    
    # Check for API key
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: No API key found!")
        print("   Set: GOOGLE_API_KEY or GEMINI_API_KEY")
        return False
    print(f"✓ API key found: {api_key[:15]}...")
    
    # Check for store ID file
    store_file = os.path.join(os.path.dirname(__file__), '..', 'GOOGLE_FILE_SEARCH_STORE.txt')
    if not os.path.exists(store_file):
        print(f"❌ Store ID file not found: {store_file}")
        print("   Run the upload script first!")
        return False
    print(f"✓ Store ID file found")
    
    # Import and test the service
    try:
        from gemini.file_search_service import get_gemini_service
        service = get_gemini_service()
        
        if not service.is_configured():
            print("❌ Service not configured properly")
            return False
        
        print(f"✓ Service initialized")
        print(f"  Store ID: {service.store_id}")
        print(f"  Model: {service.model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return False
    
    # Test a query
    print("\n" + "-" * 60)
    print("Testing query: 'How do I set up email deliverability in GHL?'")
    print("-" * 60)
    
    try:
        result = service.query(
            "How do I set up email deliverability in GHL?",
            max_tokens=1024
        )
        
        if result.get('success'):
            print("✓ Query successful!")
            print(f"\nAnswer preview (first 500 chars):")
            print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
            
            if result.get('citations'):
                print(f"\nCitations: {len(result['citations'])} sources found")
        else:
            print(f"❌ Query failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("  ✅ ALL TESTS PASSED - INTEGRATION READY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)
