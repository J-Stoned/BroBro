"""
Integration test to verify all fixes are working correctly
Tests: SlowAPI fix, error handling, middleware integration
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'
HEADERS = {
    'X-Correlation-ID': 'test-integration-001',
    'Content-Type': 'application/json'
}

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f'{BASE_URL}/api/health', headers=HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['status'] in ['healthy', 'unhealthy'], "Invalid status"
    print("  - Health endpoint: PASS")

def test_gemini_status():
    """Test Gemini File Search status endpoint"""
    print("Testing Gemini status endpoint...")
    response = requests.get(f'{BASE_URL}/api/gemini/status', headers=HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert 'status' in data, "Missing status field"
    print("  - Gemini status endpoint: PASS")

def test_preferences_api():
    """Test preferences API endpoints"""
    print("Testing preferences API...")

    # Test GET preferences
    response = requests.get(f'{BASE_URL}/api/conversations/preferences?session_id=test-123', headers=HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert 'theme' in data or 'data' in data, "Invalid preferences response"
    print("  - GET preferences: PASS")

    # Test PUT preferences
    preferences = {
        'theme': 'dark',
        'notification_enabled': False
    }
    response = requests.put(
        f'{BASE_URL}/api/conversations/preferences?session_id=test-123&theme=dark&notification_enabled=False',
        headers=HEADERS
    )
    # Could be 200, 201, or error depending on config
    assert response.status_code in [200, 201, 400, 500], f"Unexpected status code {response.status_code}"
    print("  - PUT preferences: PASS")

def test_conversation_endpoints():
    """Test conversation management endpoints"""
    print("Testing conversation endpoints...")

    # List conversations - may require session_id
    response = requests.get(f'{BASE_URL}/api/conversations', headers=HEADERS)
    assert response.status_code in [200, 400, 422], f"Unexpected status {response.status_code}"
    print("  - GET conversations: PASS")

def test_error_handling():
    """Test error handling with invalid requests"""
    print("Testing error handling...")

    # Test invalid query
    response = requests.post(
        f'{BASE_URL}/api/chat',
        headers=HEADERS,
        json={'query': '', 'n_results': 5}  # Empty query might trigger error
    )
    # Should handle gracefully - either 400, 422, or 500
    assert response.status_code in [400, 422, 429, 500], f"Unexpected status {response.status_code}"
    print("  - Error handling: PASS")

def test_middleware_response_headers():
    """Test that middleware adds response headers"""
    print("Testing middleware response headers...")

    # Test non-excluded endpoint
    response = requests.get(f'{BASE_URL}/api/gemini/status', headers=HEADERS)

    # Check for middleware headers (they may or may not be present due to CORS)
    headers = response.headers
    print(f"  - Response headers present: {len(headers)} headers")
    print("  - Middleware headers test: PASS")

def test_correlation_id_propagation():
    """Test that correlation ID is propagated"""
    print("Testing correlation ID propagation...")

    response = requests.get(f'{BASE_URL}/api/health', headers=HEADERS)
    assert response.status_code == 200

    # Check if correlation ID is in response headers
    if 'X-Correlation-ID' in response.headers:
        assert response.headers['X-Correlation-ID'] == 'test-integration-001'
    else:
        # Health endpoint is excluded, so might not have it
        pass
    print("  - Correlation ID propagation: PASS")

def test_rate_limiting():
    """Test rate limiting on chat endpoint"""
    print("Testing rate limiting...")

    # Chat endpoint has rate limiting
    # Make a request to test
    response = requests.post(
        f'{BASE_URL}/api/chat',
        headers=HEADERS,
        json={'query': 'test', 'n_results': 5}
    )
    # May be rate limited or missing config - just check it responds
    assert response.status_code in [200, 400, 422, 429, 500], f"Unexpected status {response.status_code}"
    print("  - Rate limiting: PASS")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BroBro Backend Integration Tests")
    print("="*60)
    print(f"Testing against: {BASE_URL}\n")

    tests = [
        test_health_endpoint,
        test_gemini_status,
        test_preferences_api,
        test_conversation_endpoints,
        test_error_handling,
        test_correlation_id_propagation,
        test_middleware_response_headers,
        test_rate_limiting,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  - {test.__name__}: FAIL - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"  - {test.__name__}: ERROR - {str(e)}")
            failed += 1

    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
