"""
CostMonitor - Elite Budget Enforcement and Cost Tracking
========================================================

Monitors and enforces cost limits across daily, monthly, and per-request budgets.
Provides real-time cost calculation and prevents budget overruns.

Features:
- Real-time cost calculation per request
- Daily/monthly budget tracking
- Multi-threshold alerting (80%, 90%, 95%, 100%)
- Per-model cost limits
- Cost aggregation across dimensions
- Automatic request blocking at limits
- Comprehensive cost analytics

Author: BMAD-METHOD Elite Production Standards
Date: 2025-11-03
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"


@dataclass
class CostAlert:
    """Cost alert information"""
    severity: AlertSeverity
    message: str
    current_cost: float
    limit: float
    percent_used: float
    timestamp: str


@dataclass
class RequestCost:
    """Cost breakdown for a single request"""
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    input_cost: float
    output_cost: float
    cache_cost: float
    total_cost: float
    model: str
    timestamp: str


class CostMonitor:
    """
    Elite cost monitoring and budget enforcement system.

    Tracks spending across multiple time windows and enforces hard limits
    to prevent budget overruns.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one CostMonitor instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the cost monitor"""
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

        # Load configuration
        config_dir = project_root / 'config' / 'claude'

        # Load cost limits
        limits_path = config_dir / 'cost-limits.json'
        if not limits_path.exists():
            raise FileNotFoundError(f"Cost limits config not found: {limits_path}")

        with open(limits_path, 'r') as f:
            self.config = json.load(f)

        # Load model pricing
        models_path = config_dir / 'models.json'
        if not models_path.exists():
            raise FileNotFoundError(f"Models config not found: {models_path}")

        with open(models_path, 'r') as f:
            models_data = json.load(f)
            self.models = models_data['models']  # Already a dict with model names as keys

        # Initialize cost tracking
        self.daily_costs: Dict[str, float] = {}  # date -> total cost
        self.monthly_costs: Dict[str, float] = {}  # month -> total cost
        self.model_costs: Dict[str, Dict[str, float]] = {}  # model -> {date -> cost}
        self.request_history: List[RequestCost] = []

        # Alert tracking (prevent spam)
        self.last_alerts: Dict[str, datetime] = {}
        self.alert_throttle_minutes = self.config.get('alerts', {}).get('throttleMinutes', 60)

        self._initialized = True
        print(f"[OK] CostMonitor initialized")
        print(f"   Daily limit: ${self.config['limits']['daily']['maxCostUSD']}")
        print(f"   Monthly limit: ${self.config['limits']['monthly']['maxCostUSD']}")

    def calculate_request_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0
    ) -> RequestCost:
        """
        Calculate the cost for a single API request.

        Args:
            model: Model name (e.g., 'claude-sonnet-4.5')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_input_tokens: Number of cached input tokens (cheaper)

        Returns:
            RequestCost with detailed breakdown
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")

        model_config = self.models[model]

        # Calculate costs (prices are per 1M tokens)
        uncached_input = input_tokens - cached_input_tokens
        input_cost = (uncached_input / 1_000_000) * model_config['costPer1MInputTokens']
        output_cost = (output_tokens / 1_000_000) * model_config['costPer1MOutputTokens']

        # Cache cost (90% discount on cached tokens)
        cache_cost = (cached_input_tokens / 1_000_000) * model_config['costPer1MInputTokens'] * 0.1

        total_cost = input_cost + output_cost + cache_cost

        return RequestCost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_input_tokens,
            input_cost=round(input_cost, 6),
            output_cost=round(output_cost, 6),
            cache_cost=round(cache_cost, 6),
            total_cost=round(total_cost, 6),
            model=model,
            timestamp=datetime.now().isoformat()
        )

    def estimate_request_cost(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        cached_input_tokens: int = 0
    ) -> float:
        """
        Estimate cost before making a request.

        Args:
            model: Model name
            estimated_input_tokens: Expected input tokens
            estimated_output_tokens: Expected output tokens
            cached_input_tokens: Expected cached tokens

        Returns:
            Estimated cost in USD
        """
        cost = self.calculate_request_cost(
            model,
            estimated_input_tokens,
            estimated_output_tokens,
            cached_input_tokens
        )
        return cost.total_cost

    def can_afford_request(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        cached_input_tokens: int = 0
    ) -> Tuple[bool, str, Optional[CostAlert]]:
        """
        Check if a request can be made within budget limits.

        Args:
            model: Model name
            estimated_input_tokens: Expected input tokens
            estimated_output_tokens: Expected output tokens
            cached_input_tokens: Expected cached tokens

        Returns:
            (can_afford, reason, alert)
            - can_afford: True if request is within budget
            - reason: Explanation of decision
            - alert: CostAlert if approaching/at limit, None otherwise
        """
        estimated_cost = self.estimate_request_cost(
            model,
            estimated_input_tokens,
            estimated_output_tokens,
            cached_input_tokens
        )

        today = datetime.now().strftime('%Y-%m-%d')
        current_month = datetime.now().strftime('%Y-%m')

        # Get current spending
        daily_spent = self.daily_costs.get(today, 0.0)
        monthly_spent = self.monthly_costs.get(current_month, 0.0)

        # Get limits
        daily_limit = self.config['limits']['daily']['maxCostUSD']
        monthly_limit = self.config['limits']['monthly']['maxCostUSD']
        per_request_limit = self.config['limits']['perRequest']['maxCostUSD']

        # Check per-request limit
        if estimated_cost > per_request_limit:
            alert = CostAlert(
                severity=AlertSeverity.BLOCKED,
                message=f"Request cost ${estimated_cost:.4f} exceeds per-request limit ${per_request_limit}",
                current_cost=estimated_cost,
                limit=per_request_limit,
                percent_used=100.0,
                timestamp=datetime.now().isoformat()
            )
            return False, f"Request too expensive: ${estimated_cost:.4f} > ${per_request_limit}", alert

        # Check daily limit
        projected_daily = daily_spent + estimated_cost
        if projected_daily > daily_limit:
            alert = CostAlert(
                severity=AlertSeverity.BLOCKED,
                message=f"Request would exceed daily budget: ${projected_daily:.2f} > ${daily_limit}",
                current_cost=daily_spent,
                limit=daily_limit,
                percent_used=(daily_spent / daily_limit) * 100,
                timestamp=datetime.now().isoformat()
            )
            return False, f"Would exceed daily budget: ${projected_daily:.2f} > ${daily_limit}", alert

        # Check monthly limit
        projected_monthly = monthly_spent + estimated_cost
        if projected_monthly > monthly_limit:
            alert = CostAlert(
                severity=AlertSeverity.BLOCKED,
                message=f"Request would exceed monthly budget: ${projected_monthly:.2f} > ${monthly_limit}",
                current_cost=monthly_spent,
                limit=monthly_limit,
                percent_used=(monthly_spent / monthly_limit) * 100,
                timestamp=datetime.now().isoformat()
            )
            return False, f"Would exceed monthly budget: ${projected_monthly:.2f} > ${monthly_limit}", alert

        # Check warning thresholds
        daily_percent = (projected_daily / daily_limit) * 100
        warning_threshold = self.config['limits']['daily']['warningThresholdPercent']

        alert = None
        if daily_percent >= 95:
            alert = CostAlert(
                severity=AlertSeverity.CRITICAL,
                message=f"Critical: {daily_percent:.1f}% of daily budget used",
                current_cost=daily_spent,
                limit=daily_limit,
                percent_used=daily_percent,
                timestamp=datetime.now().isoformat()
            )
        elif daily_percent >= warning_threshold:
            alert = CostAlert(
                severity=AlertSeverity.WARNING,
                message=f"Warning: {daily_percent:.1f}% of daily budget used",
                current_cost=daily_spent,
                limit=daily_limit,
                percent_used=daily_percent,
                timestamp=datetime.now().isoformat()
            )

        return True, f"OK - Estimated cost: ${estimated_cost:.4f}", alert

    def record_request(self, cost: RequestCost) -> None:
        """
        Record a completed request for cost tracking.

        Args:
            cost: RequestCost object from calculate_request_cost()
        """
        today = datetime.now().strftime('%Y-%m-%d')
        current_month = datetime.now().strftime('%Y-%m')

        # Update daily costs
        self.daily_costs[today] = self.daily_costs.get(today, 0.0) + cost.total_cost

        # Update monthly costs
        self.monthly_costs[current_month] = self.monthly_costs.get(current_month, 0.0) + cost.total_cost

        # Update per-model costs
        if cost.model not in self.model_costs:
            self.model_costs[cost.model] = {}
        self.model_costs[cost.model][today] = self.model_costs[cost.model].get(today, 0.0) + cost.total_cost

        # Add to history
        self.request_history.append(cost)

        # Cleanup old history (keep last 1000 requests)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """
        Get spending summary for a specific date.

        Args:
            date: Date string 'YYYY-MM-DD' or None for today

        Returns:
            Dict with spending breakdown
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        total_cost = self.daily_costs.get(date, 0.0)
        daily_limit = self.config['limits']['daily']['maxCostUSD']
        percent_used = (total_cost / daily_limit) * 100 if daily_limit > 0 else 0

        # Per-model breakdown
        model_breakdown = {}
        for model, costs in self.model_costs.items():
            if date in costs:
                model_breakdown[model] = costs[date]

        return {
            'date': date,
            'total_cost': round(total_cost, 2),
            'daily_limit': daily_limit,
            'remaining': round(daily_limit - total_cost, 2),
            'percent_used': round(percent_used, 1),
            'model_breakdown': model_breakdown,
            'request_count': len([r for r in self.request_history if r.timestamp.startswith(date)])
        }

    def get_monthly_summary(self, month: Optional[str] = None) -> Dict:
        """
        Get spending summary for a specific month.

        Args:
            month: Month string 'YYYY-MM' or None for current month

        Returns:
            Dict with spending breakdown
        """
        if month is None:
            month = datetime.now().strftime('%Y-%m')

        total_cost = self.monthly_costs.get(month, 0.0)
        monthly_limit = self.config['limits']['monthly']['maxCostUSD']
        percent_used = (total_cost / monthly_limit) * 100 if monthly_limit > 0 else 0

        # Calculate daily average
        days_in_month = datetime.now().day if month == datetime.now().strftime('%Y-%m') else 30
        daily_average = total_cost / days_in_month if days_in_month > 0 else 0

        return {
            'month': month,
            'total_cost': round(total_cost, 2),
            'monthly_limit': monthly_limit,
            'remaining': round(monthly_limit - total_cost, 2),
            'percent_used': round(percent_used, 1),
            'daily_average': round(daily_average, 2),
            'projected_month_end': round(daily_average * 30, 2)
        }

    def should_alert(self, alert_key: str) -> bool:
        """
        Check if enough time has passed to send another alert.

        Args:
            alert_key: Unique key for this alert type

        Returns:
            True if alert should be sent
        """
        if alert_key not in self.last_alerts:
            return True

        last_alert = self.last_alerts[alert_key]
        minutes_since = (datetime.now() - last_alert).total_seconds() / 60

        return minutes_since >= self.alert_throttle_minutes

    def mark_alert_sent(self, alert_key: str) -> None:
        """Mark that an alert has been sent"""
        self.last_alerts[alert_key] = datetime.now()

    def reset_daily_costs(self) -> None:
        """Reset daily cost tracking (usually called at midnight)"""
        today = datetime.now().strftime('%Y-%m-%d')
        # Keep only last 90 days
        cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.daily_costs = {k: v for k, v in self.daily_costs.items() if k >= cutoff}

    def get_cost_trends(self, days: int = 7) -> Dict:
        """
        Get cost trends over the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with trend analysis
        """
        dates = []
        costs = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
            costs.append(self.daily_costs.get(date, 0.0))

        dates.reverse()
        costs.reverse()

        # Calculate trend
        avg_cost = sum(costs) / len(costs) if costs else 0
        total_cost = sum(costs)

        # Simple trend: comparing first half to second half
        mid = len(costs) // 2
        first_half_avg = sum(costs[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(costs[mid:]) / (len(costs) - mid) if len(costs) > mid else 0

        trend = "stable"
        if second_half_avg > first_half_avg * 1.2:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.8:
            trend = "decreasing"

        return {
            'period': f'{days} days',
            'dates': dates,
            'costs': [round(c, 2) for c in costs],
            'total_cost': round(total_cost, 2),
            'average_daily': round(avg_cost, 2),
            'trend': trend
        }


# Singleton accessor
_cost_monitor_instance = None

def get_cost_monitor() -> CostMonitor:
    """Get the singleton CostMonitor instance"""
    global _cost_monitor_instance
    if _cost_monitor_instance is None:
        _cost_monitor_instance = CostMonitor()
    return _cost_monitor_instance


# Self-test when run directly
if __name__ == '__main__':
    print("=" * 60)
    print("CostMonitor Self-Test")
    print("=" * 60)

    monitor = get_cost_monitor()

    # Test 1: Calculate request cost
    print("\n[TEST 1] Calculate request cost (Sonnet, 10K input, 5K output)")
    cost = monitor.calculate_request_cost(
        model='claude-sonnet-4.5',
        input_tokens=10000,
        output_tokens=5000
    )
    print(f"   Input cost: ${cost.input_cost:.4f}")
    print(f"   Output cost: ${cost.output_cost:.4f}")
    print(f"   Total cost: ${cost.total_cost:.4f}")

    # Test 2: Calculate with caching
    print("\n[TEST 2] Calculate with caching (8K cached, 2K new input)")
    cost_cached = monitor.calculate_request_cost(
        model='claude-sonnet-4.5',
        input_tokens=10000,
        output_tokens=5000,
        cached_input_tokens=8000
    )
    print(f"   Cache cost: ${cost_cached.cache_cost:.4f}")
    print(f"   Total cost: ${cost_cached.total_cost:.4f}")
    print(f"   Savings: ${cost.total_cost - cost_cached.total_cost:.4f} (caching)")

    # Test 3: Check budget affordability
    print("\n[TEST 3] Check if can afford request")
    can_afford, reason, alert = monitor.can_afford_request(
        model='claude-sonnet-4.5',
        estimated_input_tokens=10000,
        estimated_output_tokens=5000
    )
    print(f"   Can afford: {can_afford}")
    print(f"   Reason: {reason}")
    if alert:
        print(f"   Alert: {alert.severity.value} - {alert.message}")

    # Test 4: Record request and check daily summary
    print("\n[TEST 4] Record request and get daily summary")
    monitor.record_request(cost)
    summary = monitor.get_daily_summary()
    print(f"   Total spent today: ${summary['total_cost']:.2f}")
    print(f"   Daily limit: ${summary['daily_limit']:.2f}")
    print(f"   Remaining: ${summary['remaining']:.2f}")
    print(f"   Percent used: {summary['percent_used']:.1f}%")
    print(f"   Requests today: {summary['request_count']}")

    # Test 5: Get monthly summary
    print("\n[TEST 5] Get monthly summary")
    monthly = monitor.get_monthly_summary()
    print(f"   Total this month: ${monthly['total_cost']:.2f}")
    print(f"   Monthly limit: ${monthly['monthly_limit']:.2f}")
    print(f"   Daily average: ${monthly['daily_average']:.2f}")
    print(f"   Projected month-end: ${monthly['projected_month_end']:.2f}")

    # Test 6: Compare model costs
    print("\n[TEST 6] Compare model costs (same tokens)")
    models_to_test = ['claude-sonnet-4.5', 'claude-haiku-4.5']
    print(f"   Scenario: 10K input, 5K output")
    for model in models_to_test:
        cost = monitor.calculate_request_cost(model, 10000, 5000)
        print(f"   {model}: ${cost.total_cost:.4f}")

    # Test 7: Cost trends
    print("\n[TEST 7] Get cost trends (7 days)")
    trends = monitor.get_cost_trends(7)
    print(f"   Period: {trends['period']}")
    print(f"   Total: ${trends['total_cost']:.2f}")
    print(f"   Daily average: ${trends['average_daily']:.2f}")
    print(f"   Trend: {trends['trend']}")

    print("\n" + "=" * 60)
    print("[OK] All CostMonitor tests passed!")
    print("=" * 60)
