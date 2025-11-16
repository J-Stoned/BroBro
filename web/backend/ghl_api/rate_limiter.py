"""
Rate Limiter - Epic 11: Story 11.1
100 requests per minute per API key
"""

import time
from collections import defaultdict
from typing import Dict, List

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()

        # Clean old requests outside window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]

        # Check if under limit
        if len(self.requests[key]) >= self.max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window"""
        now = time.time()
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]
        return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> float:
        """Get seconds until rate limit resets"""
        if not self.requests[key]:
            return 0

        now = time.time()
        oldest = min(self.requests[key])
        reset_time = oldest + self.window_seconds - now
        return max(0, reset_time)
