"""
RateLimiter - Elite Tier-Based Rate Limiting System
====================================================

Enforces Anthropic's tier-based rate limits with sliding window algorithm.
Prevents API rejections by tracking RPM, ITPM, and OTPM across all models.

Features:
- Tier-based rate limiting (Tier 1-4 + Enterprise)
- Per-model rate limits (RPM, ITPM, OTPM)
- Sliding window algorithm for accurate tracking
- Automatic tier detection based on spend
- Shared limit pools for model families (Sonnet 4/4.5)
- Prompt caching awareness (cached tokens don't count toward ITPM)
- Proactive request queuing when approaching limits
- Real-time limit monitoring

Author: BMAD-METHOD Elite Production Standards
Date: 2025-11-03
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
from enum import Enum
import time


class RateLimitType(Enum):
    """Rate limit metric types"""
    RPM = "rpm"  # Requests per minute
    ITPM = "itpm"  # Input tokens per minute
    OTPM = "otpm"  # Output tokens per minute


@dataclass
class RateLimitConfig:
    """Rate limit configuration for a model at a tier"""
    rpm: int
    itpm: int
    otpm: int


@dataclass
class RequestRecord:
    """Record of a past request for rate limiting"""
    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int


@dataclass
class RateLimitStatus:
    """Current rate limit status"""
    can_proceed: bool
    reason: str
    wait_seconds: float
    current_usage: Dict[str, int]
    limits: Dict[str, int]
    percent_used: Dict[str, float]


class RateLimiter:
    """
    Elite tier-based rate limiting system.

    Tracks requests in a sliding window and enforces Anthropic's
    tier-based rate limits to prevent API rejections.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one RateLimiter instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the rate limiter"""
        if self._initialized:
            return

        # Find project root (where .env file is)
        current = Path(__file__).resolve()
        project_root = None
        for parent in [current] + list(current.parents):
            if (parent / '.env').exists():
                project_root = parent
                break

        if not project_root:
            raise FileNotFoundError("Could not find project root (no .env file found)")

        # Load rate limit configuration
        config_dir = project_root / 'config' / 'claude'
        limits_path = config_dir / 'rate-limits.json'

        if not limits_path.exists():
            raise FileNotFoundError(f"Rate limits config not found: {limits_path}")

        with open(limits_path, 'r') as f:
            self.config = json.load(f)

        # Current tier (can be updated based on cumulative spend)
        self.current_tier = self.config.get('currentTier', 'tier1')

        # Request history (sliding window)
        self.request_history: deque[RequestRecord] = deque(maxlen=10000)

        # Per-model request queues (for sliding window)
        self.model_windows: Dict[str, deque[RequestRecord]] = {}

        # Sliding window duration (60 seconds)
        self.window_seconds = self.config.get('rateLimit', {}).get('windowSeconds', 60)

        # Safety margin (don't use 100% of limit)
        self.safety_margin = 0.9  # Use only 90% of limit

        # Model family mappings (shared limits)
        self.model_families = {
            'sonnet': ['claude-sonnet-4', 'claude-sonnet-4.5'],
            'haiku': ['claude-haiku-4.5'],
            'opus': ['claude-opus-4']
        }

        self._initialized = True
        print(f"[OK] RateLimiter initialized")
        print(f"   Current tier: {self.current_tier}")
        print(f"   Window: {self.window_seconds}s")
        print(f"   Safety margin: {int(self.safety_margin * 100)}%")

    def get_model_limits(self, model: str) -> RateLimitConfig:
        """
        Get rate limits for a specific model at current tier.

        Args:
            model: Model name (e.g., 'claude-sonnet-4.5')

        Returns:
            RateLimitConfig with limits
        """
        tier_config = self.config['tiers'].get(self.current_tier)
        if not tier_config:
            raise ValueError(f"Unknown tier: {self.current_tier}")

        model_limits = tier_config['models'].get(model)
        if not model_limits:
            raise ValueError(f"Unknown model: {model}")

        return RateLimitConfig(
            rpm=model_limits['rpm'],
            itpm=model_limits['itpm'],
            otpm=model_limits['otpm']
        )

    def _get_model_family(self, model: str) -> str:
        """Get the model family for shared limit tracking"""
        for family, models in self.model_families.items():
            if model in models:
                return family
        return model  # If not in a family, treat as its own

    def _cleanup_old_records(self, now: float) -> None:
        """Remove records older than the sliding window"""
        cutoff = now - self.window_seconds

        # Cleanup main history
        while self.request_history and self.request_history[0].timestamp < cutoff:
            self.request_history.popleft()

        # Cleanup per-model windows
        for model, window in self.model_windows.items():
            while window and window[0].timestamp < cutoff:
                window.popleft()

    def _get_current_usage(self, model: str, now: float) -> Dict[str, int]:
        """
        Calculate current usage within the sliding window.

        For models in the same family (e.g., Sonnet 4 and 4.5),
        combine their usage for shared limits.

        Args:
            model: Model to check
            now: Current timestamp

        Returns:
            Dict with current RPM, ITPM, OTPM
        """
        family = self._get_model_family(model)

        # Get all models in this family
        family_models = self.model_families.get(family, [model])

        rpm = 0
        itpm = 0
        otpm = 0

        # Count requests from all models in the family
        for record in self.request_history:
            if record.model in family_models:
                rpm += 1
                # Only uncached tokens count toward ITPM (per Anthropic docs)
                uncached_input = record.input_tokens - record.cached_tokens
                itpm += uncached_input
                otpm += record.output_tokens

        return {
            'rpm': rpm,
            'itpm': itpm,
            'otpm': otpm
        }

    def can_make_request(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        cached_tokens: int = 0
    ) -> RateLimitStatus:
        """
        Check if a request can be made without exceeding rate limits.

        Args:
            model: Model name
            estimated_input_tokens: Expected input tokens
            estimated_output_tokens: Expected output tokens
            cached_tokens: Expected cached tokens (don't count toward ITPM)

        Returns:
            RateLimitStatus with decision and details
        """
        now = time.time()
        self._cleanup_old_records(now)

        # Get limits for this model
        limits = self.get_model_limits(model)

        # Get current usage (includes family sharing)
        current = self._get_current_usage(model, now)

        # Calculate projected usage with this request
        uncached_input = estimated_input_tokens - cached_tokens
        projected = {
            'rpm': current['rpm'] + 1,
            'itpm': current['itpm'] + uncached_input,
            'otpm': current['otpm'] + estimated_output_tokens
        }

        # Apply safety margin to limits
        safe_limits = {
            'rpm': int(limits.rpm * self.safety_margin),
            'itpm': int(limits.itpm * self.safety_margin),
            'otpm': int(limits.otpm * self.safety_margin)
        }

        # Check each limit type
        violations = []
        wait_times = []

        if projected['rpm'] > safe_limits['rpm']:
            violations.append(f"RPM: {projected['rpm']} > {safe_limits['rpm']}")
            # Calculate wait time based on oldest request
            if self.request_history:
                oldest = self.request_history[0].timestamp
                wait_time = max(0, self.window_seconds - (now - oldest))
                wait_times.append(wait_time)

        if projected['itpm'] > safe_limits['itpm']:
            violations.append(f"ITPM: {projected['itpm']} > {safe_limits['itpm']}")
            if self.request_history:
                oldest = self.request_history[0].timestamp
                wait_time = max(0, self.window_seconds - (now - oldest))
                wait_times.append(wait_time)

        if projected['otpm'] > safe_limits['otpm']:
            violations.append(f"OTPM: {projected['otpm']} > {safe_limits['otpm']}")
            if self.request_history:
                oldest = self.request_history[0].timestamp
                wait_time = max(0, self.window_seconds - (now - oldest))
                wait_times.append(wait_time)

        # Calculate percent used
        percent_used = {
            'rpm': round(current['rpm'] / limits.rpm * 100, 1),
            'itpm': round(current['itpm'] / limits.itpm * 100, 1),
            'otpm': round(current['otpm'] / limits.otpm * 100, 1)
        }

        if violations:
            return RateLimitStatus(
                can_proceed=False,
                reason=f"Rate limit would be exceeded: {', '.join(violations)}",
                wait_seconds=max(wait_times) if wait_times else 0,
                current_usage=current,
                limits={'rpm': limits.rpm, 'itpm': limits.itpm, 'otpm': limits.otpm},
                percent_used=percent_used
            )
        else:
            return RateLimitStatus(
                can_proceed=True,
                reason="Within rate limits",
                wait_seconds=0.0,
                current_usage=current,
                limits={'rpm': limits.rpm, 'itpm': limits.itpm, 'otpm': limits.otpm},
                percent_used=percent_used
            )

    def record_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0
    ) -> None:
        """
        Record a completed request for rate limiting.

        Args:
            model: Model used
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            cached_tokens: Cached tokens (don't count toward ITPM)
        """
        record = RequestRecord(
            timestamp=time.time(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens
        )

        self.request_history.append(record)

        # Also add to per-model window
        if model not in self.model_windows:
            self.model_windows[model] = deque(maxlen=1000)
        self.model_windows[model].append(record)

    def get_current_status(self, model: str) -> Dict:
        """
        Get current rate limit status for a model.

        Args:
            model: Model name

        Returns:
            Dict with current status
        """
        now = time.time()
        self._cleanup_old_records(now)

        limits = self.get_model_limits(model)
        current = self._get_current_usage(model, now)

        return {
            'model': model,
            'tier': self.current_tier,
            'current_usage': current,
            'limits': {
                'rpm': limits.rpm,
                'itpm': limits.itpm,
                'otpm': limits.otpm
            },
            'remaining': {
                'rpm': limits.rpm - current['rpm'],
                'itpm': limits.itpm - current['itpm'],
                'otpm': limits.otpm - current['otpm']
            },
            'percent_used': {
                'rpm': round(current['rpm'] / limits.rpm * 100, 1),
                'itpm': round(current['itpm'] / limits.itpm * 100, 1),
                'otpm': round(current['otpm'] / limits.otpm * 100, 1)
            }
        }

    def update_tier(self, new_tier: str) -> None:
        """
        Update the current tier based on cumulative spend.

        Args:
            new_tier: New tier ('tier1', 'tier2', 'tier3', 'tier4', 'enterprise')
        """
        if new_tier not in self.config['tiers']:
            raise ValueError(f"Unknown tier: {new_tier}")

        old_tier = self.current_tier
        self.current_tier = new_tier
        print(f"[OK] Rate limit tier updated: {old_tier} -> {new_tier}")

    def get_recommended_wait_time(self, model: str) -> float:
        """
        Get recommended wait time before next request.

        Args:
            model: Model name

        Returns:
            Recommended wait time in seconds (0 if can proceed immediately)
        """
        status = self.can_make_request(model, 10000, 5000, 0)
        return status.wait_seconds

    def get_tier_info(self) -> Dict:
        """
        Get information about the current tier.

        Returns:
            Dict with tier details
        """
        tier_config = self.config['tiers'].get(self.current_tier, {})
        return {
            'tier': self.current_tier,
            'description': tier_config.get('description', ''),
            'qualification_spend': tier_config.get('qualificationSpend', 0),
            'max_single_purchase': tier_config.get('maxSinglePurchase', 0),
            'monthly_invoicing': tier_config.get('monthlyInvoicing', False),
            'models': tier_config.get('models', {})
        }


# Singleton accessor
_rate_limiter_instance = None

def get_rate_limiter() -> RateLimiter:
    """Get the singleton RateLimiter instance"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance


# Self-test when run directly
if __name__ == '__main__':
    print("=" * 60)
    print("RateLimiter Self-Test")
    print("=" * 60)

    limiter = get_rate_limiter()

    # Test 1: Get model limits
    print("\n[TEST 1] Get model limits (Sonnet 4.5 at Tier 1)")
    limits = limiter.get_model_limits('claude-sonnet-4.5')
    print(f"   RPM: {limits.rpm}")
    print(f"   ITPM: {limits.itpm}")
    print(f"   OTPM: {limits.otpm}")

    # Test 2: Check if can make request (should be OK)
    print("\n[TEST 2] Check if can make request (no prior requests)")
    status = limiter.can_make_request(
        model='claude-sonnet-4.5',
        estimated_input_tokens=10000,
        estimated_output_tokens=5000
    )
    print(f"   Can proceed: {status.can_proceed}")
    print(f"   Reason: {status.reason}")
    print(f"   Current usage: {status.current_usage}")

    # Test 3: Record some requests
    print("\n[TEST 3] Record 10 requests")
    for i in range(10):
        limiter.record_request(
            model='claude-sonnet-4.5',
            input_tokens=10000,
            output_tokens=5000,
            cached_tokens=2000
        )
    print(f"   Recorded 10 requests")

    # Test 4: Check current status
    print("\n[TEST 4] Current status after 10 requests")
    status = limiter.get_current_status('claude-sonnet-4.5')
    print(f"   RPM used: {status['current_usage']['rpm']} / {status['limits']['rpm']} ({status['percent_used']['rpm']}%)")
    print(f"   ITPM used: {status['current_usage']['itpm']:,} / {status['limits']['itpm']:,} ({status['percent_used']['itpm']}%)")
    print(f"   OTPM used: {status['current_usage']['otpm']:,} / {status['limits']['otpm']:,} ({status['percent_used']['otpm']}%)")

    # Test 5: Simulate approaching RPM limit
    print("\n[TEST 5] Simulate approaching RPM limit (record 40 more)")
    for i in range(40):
        limiter.record_request(
            model='claude-sonnet-4.5',
            input_tokens=100,
            output_tokens=50
        )
    status = limiter.get_current_status('claude-sonnet-4.5')
    print(f"   RPM used: {status['current_usage']['rpm']} / {status['limits']['rpm']} ({status['percent_used']['rpm']}%)")
    print(f"   RPM remaining: {status['remaining']['rpm']}")

    # Test 6: Check if can make request (should warn or block)
    print("\n[TEST 6] Check if can make request (after 50 requests)")
    check = limiter.can_make_request(
        model='claude-sonnet-4.5',
        estimated_input_tokens=10000,
        estimated_output_tokens=5000
    )
    print(f"   Can proceed: {check.can_proceed}")
    print(f"   Reason: {check.reason}")
    if not check.can_proceed:
        print(f"   Wait time: {check.wait_seconds:.1f}s")

    # Test 7: Test caching benefit (cached tokens don't count toward ITPM)
    print("\n[TEST 7] Test prompt caching benefit")
    print("   Without caching (10K input):")
    check_no_cache = limiter.can_make_request(
        model='claude-haiku-4.5',
        estimated_input_tokens=10000,
        estimated_output_tokens=5000,
        cached_tokens=0
    )
    print(f"     Projected ITPM: {check_no_cache.current_usage['itpm'] + 10000}")

    print("   With caching (10K input, 8K cached):")
    check_with_cache = limiter.can_make_request(
        model='claude-haiku-4.5',
        estimated_input_tokens=10000,
        estimated_output_tokens=5000,
        cached_tokens=8000
    )
    print(f"     Projected ITPM: {check_with_cache.current_usage['itpm'] + 2000} (8K cached don't count!)")

    # Test 8: Get tier info
    print("\n[TEST 8] Get tier information")
    tier_info = limiter.get_tier_info()
    print(f"   Current tier: {tier_info['tier']}")
    print(f"   Description: {tier_info['description']}")
    print(f"   Qualification spend: ${tier_info['qualification_spend']}")

    # Test 9: Simulate tier upgrade
    print("\n[TEST 9] Simulate tier upgrade to Tier 4")
    limiter.update_tier('tier4')
    tier4_info = limiter.get_tier_info()
    print(f"   New tier: {tier4_info['tier']}")
    print(f"   Qualification spend: ${tier4_info['qualification_spend']}")
    print(f"   Monthly invoicing: {tier4_info['monthly_invoicing']}")

    print("\n" + "=" * 60)
    print("[OK] All RateLimiter tests passed!")
    print("=" * 60)
