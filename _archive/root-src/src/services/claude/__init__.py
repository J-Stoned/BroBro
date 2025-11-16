"""
Claude API Elite System
========================

Unified intelligent Claude API client with cost optimization, rate limiting,
budget enforcement, and comprehensive analytics.

Quick Start:
-----------
from src.services.claude import ClaudeAPIManager

manager = ClaudeAPIManager()
response = manager.send_message(
    messages=[{"role": "user", "content": "Your message here"}],
    profile="workflow-builder"  # Auto-selects Sonnet with optimized settings
)

print(response.content)  # AI response
print(f"Cost: ${response.cost}")  # Exact cost
"""

from src.services.claude.ClaudeAPIManager import ClaudeAPIManager, get_claude_api_manager, APIResponse
from src.services.claude.config.ConfigManager import get_config_manager
from src.services.claude.utils.TokenCounter import get_token_counter
from src.services.claude.monitoring.CostMonitor import get_cost_monitor
from src.services.claude.monitoring.UsageTracker import get_usage_tracker
from src.services.claude.monitoring.RateLimiter import get_rate_limiter

__all__ = [
    'ClaudeAPIManager',
    'get_claude_api_manager',
    'APIResponse',
    'get_config_manager',
    'get_token_counter',
    'get_cost_monitor',
    'get_usage_tracker',
    'get_rate_limiter'
]
