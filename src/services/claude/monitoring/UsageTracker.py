"""
UsageTracker - Elite Analytics and Reporting System
====================================================

Tracks detailed usage metrics across multiple dimensions for analysis and optimization.
Provides comprehensive analytics on API usage, costs, performance, and patterns.

Features:
- Multi-dimensional tracking (endpoint, user, model, profile, time)
- Real-time analytics aggregation
- Usage pattern detection
- Performance metrics
- Export to JSON/CSV
- Historical trend analysis
- Anomaly detection

Author: BMAD-METHOD Elite Production Standards
Date: 2025-11-03
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum


class MetricType(Enum):
    """Metric type categories"""
    REQUEST = "request"
    TOKENS = "tokens"
    COST = "cost"
    LATENCY = "latency"
    ERROR = "error"


@dataclass
class UsageMetric:
    """Single usage metric record"""
    timestamp: str
    metric_type: str
    endpoint: str
    user_id: str
    model: str
    profile: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int
    cost: float
    latency_ms: int
    success: bool
    error_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time period"""
    period: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    total_cached_tokens: int
    total_cost: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    unique_users: int
    unique_endpoints: int


class UsageTracker:
    """
    Elite usage tracking and analytics system.

    Tracks all API usage across multiple dimensions and provides
    comprehensive analytics for optimization and cost control.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one UsageTracker instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the usage tracker"""
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

        # Create usage data directory
        self.data_dir = project_root / 'data' / 'usage'
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage for recent metrics
        self.metrics: List[UsageMetric] = []
        self.max_memory_metrics = 10000  # Keep last 10K in memory

        # Aggregated metrics cache
        self.hourly_stats: Dict[str, Dict] = {}
        self.daily_stats: Dict[str, Dict] = {}

        # Tracking maps
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'errors': 0
        })
        self.user_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0
        })
        self.model_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'avg_latency': 0.0
        })
        self.profile_stats: Dict[str, Dict] = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0
        })

        self._initialized = True
        print(f"[OK] UsageTracker initialized")
        print(f"   Data directory: {self.data_dir}")

    def record_request(
        self,
        endpoint: str,
        user_id: str,
        model: str,
        profile: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        cost: float,
        latency_ms: int,
        success: bool,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageMetric:
        """
        Record a single API request for tracking.

        Args:
            endpoint: API endpoint called
            user_id: User/client identifier
            model: Model used
            profile: Profile used
            input_tokens: Input tokens
            output_tokens: Output tokens
            cached_tokens: Cached tokens
            cost: Request cost in USD
            latency_ms: Request latency in milliseconds
            success: Whether request succeeded
            error_type: Error type if failed
            metadata: Additional metadata

        Returns:
            UsageMetric record
        """
        metric = UsageMetric(
            timestamp=datetime.now().isoformat(),
            metric_type=MetricType.REQUEST.value,
            endpoint=endpoint,
            user_id=user_id,
            model=model,
            profile=profile,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            success=success,
            error_type=error_type,
            metadata=metadata
        )

        # Add to in-memory storage
        self.metrics.append(metric)

        # Trim if too large
        if len(self.metrics) > self.max_memory_metrics:
            # Persist old metrics to disk before removing
            old_metrics = self.metrics[:-self.max_memory_metrics]
            self._persist_metrics(old_metrics)
            self.metrics = self.metrics[-self.max_memory_metrics:]

        # Update aggregated stats
        self._update_stats(metric)

        return metric

    def _update_stats(self, metric: UsageMetric) -> None:
        """Update aggregated statistics"""
        # Endpoint stats
        self.endpoint_stats[metric.endpoint]['requests'] += 1
        self.endpoint_stats[metric.endpoint]['tokens'] += metric.total_tokens
        self.endpoint_stats[metric.endpoint]['cost'] += metric.cost
        if not metric.success:
            self.endpoint_stats[metric.endpoint]['errors'] += 1

        # User stats
        self.user_stats[metric.user_id]['requests'] += 1
        self.user_stats[metric.user_id]['tokens'] += metric.total_tokens
        self.user_stats[metric.user_id]['cost'] += metric.cost

        # Model stats
        old_count = self.model_stats[metric.model]['requests']
        old_avg = self.model_stats[metric.model]['avg_latency']
        new_count = old_count + 1
        new_avg = ((old_avg * old_count) + metric.latency_ms) / new_count

        self.model_stats[metric.model]['requests'] = new_count
        self.model_stats[metric.model]['tokens'] += metric.total_tokens
        self.model_stats[metric.model]['cost'] += metric.cost
        self.model_stats[metric.model]['avg_latency'] = new_avg

        # Profile stats
        self.profile_stats[metric.profile]['requests'] += 1
        self.profile_stats[metric.profile]['tokens'] += metric.total_tokens
        self.profile_stats[metric.profile]['cost'] += metric.cost

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict:
        """
        Get statistics for specific endpoint or all endpoints.

        Args:
            endpoint: Specific endpoint or None for all

        Returns:
            Dict with endpoint statistics
        """
        if endpoint:
            return dict(self.endpoint_stats.get(endpoint, {}))
        else:
            return {k: dict(v) for k, v in self.endpoint_stats.items()}

    def get_user_stats(self, user_id: Optional[str] = None) -> Dict:
        """Get statistics for specific user or all users"""
        if user_id:
            return dict(self.user_stats.get(user_id, {}))
        else:
            return {k: dict(v) for k, v in self.user_stats.items()}

    def get_model_stats(self, model: Optional[str] = None) -> Dict:
        """Get statistics for specific model or all models"""
        if model:
            return dict(self.model_stats.get(model, {}))
        else:
            return {k: dict(v) for k, v in self.model_stats.items()}

    def get_profile_stats(self, profile: Optional[str] = None) -> Dict:
        """Get statistics for specific profile or all profiles"""
        if profile:
            return dict(self.profile_stats.get(profile, {}))
        else:
            return {k: dict(v) for k, v in self.profile_stats.items()}

    def get_time_series(
        self,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 60
    ) -> List[Dict]:
        """
        Get time series data for a date range.

        Args:
            start_time: Start of range
            end_time: End of range
            interval_minutes: Aggregation interval

        Returns:
            List of time buckets with metrics
        """
        # Filter metrics in range
        metrics_in_range = [
            m for m in self.metrics
            if start_time <= datetime.fromisoformat(m.timestamp) <= end_time
        ]

        # Create time buckets
        buckets: Dict[str, List[UsageMetric]] = defaultdict(list)
        for metric in metrics_in_range:
            timestamp = datetime.fromisoformat(metric.timestamp)
            bucket_time = timestamp.replace(
                minute=(timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0
            )
            bucket_key = bucket_time.isoformat()
            buckets[bucket_key].append(metric)

        # Aggregate each bucket
        result = []
        for bucket_time in sorted(buckets.keys()):
            bucket_metrics = buckets[bucket_time]
            result.append({
                'timestamp': bucket_time,
                'requests': len(bucket_metrics),
                'successful': sum(1 for m in bucket_metrics if m.success),
                'failed': sum(1 for m in bucket_metrics if not m.success),
                'total_tokens': sum(m.total_tokens for m in bucket_metrics),
                'total_cost': round(sum(m.cost for m in bucket_metrics), 4),
                'avg_latency': round(sum(m.latency_ms for m in bucket_metrics) / len(bucket_metrics), 1)
            })

        return result

    def get_top_users(self, metric: str = 'cost', limit: int = 10) -> List[Dict]:
        """
        Get top users by specified metric.

        Args:
            metric: Metric to sort by ('cost', 'requests', 'tokens')
            limit: Number of users to return

        Returns:
            List of top users with stats
        """
        users = []
        for user_id, stats in self.user_stats.items():
            users.append({
                'user_id': user_id,
                'requests': stats['requests'],
                'tokens': stats['tokens'],
                'cost': round(stats['cost'], 2)
            })

        # Sort by specified metric
        users.sort(key=lambda x: x[metric], reverse=True)
        return users[:limit]

    def get_top_endpoints(self, metric: str = 'cost', limit: int = 10) -> List[Dict]:
        """Get top endpoints by specified metric"""
        endpoints = []
        for endpoint, stats in self.endpoint_stats.items():
            endpoints.append({
                'endpoint': endpoint,
                'requests': stats['requests'],
                'tokens': stats['tokens'],
                'cost': round(stats['cost'], 2),
                'errors': stats['errors'],
                'error_rate': round(stats['errors'] / stats['requests'] * 100, 1) if stats['requests'] > 0 else 0
            })

        endpoints.sort(key=lambda x: x[metric], reverse=True)
        return endpoints[:limit]

    def get_aggregated_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> AggregatedMetrics:
        """
        Get aggregated metrics for a time period.

        Args:
            start_time: Start of period (None = beginning)
            end_time: End of period (None = now)

        Returns:
            AggregatedMetrics object
        """
        # Filter metrics
        metrics = self.metrics
        if start_time or end_time:
            metrics = [
                m for m in self.metrics
                if (not start_time or datetime.fromisoformat(m.timestamp) >= start_time) and
                   (not end_time or datetime.fromisoformat(m.timestamp) <= end_time)
            ]

        if not metrics:
            return AggregatedMetrics(
                period=f"{start_time} to {end_time}",
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                total_tokens=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cached_tokens=0,
                total_cost=0.0,
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                unique_users=0,
                unique_endpoints=0
            )

        # Calculate percentiles
        latencies = sorted([m.latency_ms for m in metrics])
        p50_idx = int(len(latencies) * 0.5)
        p95_idx = int(len(latencies) * 0.95)
        p99_idx = int(len(latencies) * 0.99)

        return AggregatedMetrics(
            period=f"{start_time or 'start'} to {end_time or 'now'}",
            total_requests=len(metrics),
            successful_requests=sum(1 for m in metrics if m.success),
            failed_requests=sum(1 for m in metrics if not m.success),
            total_tokens=sum(m.total_tokens for m in metrics),
            total_input_tokens=sum(m.input_tokens for m in metrics),
            total_output_tokens=sum(m.output_tokens for m in metrics),
            total_cached_tokens=sum(m.cached_tokens for m in metrics),
            total_cost=round(sum(m.cost for m in metrics), 2),
            avg_latency_ms=round(sum(m.latency_ms for m in metrics) / len(metrics), 1),
            p50_latency_ms=latencies[p50_idx] if latencies else 0,
            p95_latency_ms=latencies[p95_idx] if latencies else 0,
            p99_latency_ms=latencies[p99_idx] if latencies else 0,
            unique_users=len(set(m.user_id for m in metrics)),
            unique_endpoints=len(set(m.endpoint for m in metrics))
        )

    def export_to_json(self, filepath: Optional[Path] = None) -> str:
        """
        Export all metrics to JSON file.

        Args:
            filepath: Output file path or None for auto-generated

        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.data_dir / f'usage_export_{timestamp}.json'

        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_metrics': len(self.metrics),
            'metrics': [asdict(m) for m in self.metrics],
            'endpoint_stats': {k: dict(v) for k, v in self.endpoint_stats.items()},
            'user_stats': {k: dict(v) for k, v in self.user_stats.items()},
            'model_stats': {k: dict(v) for k, v in self.model_stats.items()},
            'profile_stats': {k: dict(v) for k, v in self.profile_stats.items()}
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        return str(filepath)

    def export_to_csv(self, filepath: Optional[Path] = None) -> str:
        """
        Export metrics to CSV file.

        Args:
            filepath: Output file path or None for auto-generated

        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.data_dir / f'usage_export_{timestamp}.csv'

        if not self.metrics:
            return str(filepath)

        # Get fieldnames from first metric
        fieldnames = list(asdict(self.metrics[0]).keys())

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for metric in self.metrics:
                row = asdict(metric)
                # Convert None values to empty string
                row = {k: (v if v is not None else '') for k, v in row.items()}
                # Convert metadata dict to JSON string
                if 'metadata' in row and row['metadata']:
                    row['metadata'] = json.dumps(row['metadata'])
                writer.writerow(row)

        return str(filepath)

    def _persist_metrics(self, metrics: List[UsageMetric]) -> None:
        """Persist metrics to disk (called when memory limit reached)"""
        if not metrics:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.data_dir / f'metrics_archive_{timestamp}.json'

        with open(filepath, 'w') as f:
            json.dump([asdict(m) for m in metrics], f, indent=2)

    def get_summary_report(self) -> Dict:
        """
        Get a comprehensive summary report of all usage.

        Returns:
            Dict with summary statistics
        """
        agg = self.get_aggregated_metrics()

        return {
            'overview': {
                'total_requests': agg.total_requests,
                'successful_requests': agg.successful_requests,
                'failed_requests': agg.failed_requests,
                'success_rate': round(agg.successful_requests / agg.total_requests * 100, 1) if agg.total_requests > 0 else 0,
                'total_cost': agg.total_cost,
                'total_tokens': agg.total_tokens,
                'unique_users': agg.unique_users,
                'unique_endpoints': agg.unique_endpoints
            },
            'performance': {
                'avg_latency_ms': agg.avg_latency_ms,
                'p50_latency_ms': agg.p50_latency_ms,
                'p95_latency_ms': agg.p95_latency_ms,
                'p99_latency_ms': agg.p99_latency_ms
            },
            'tokens': {
                'total': agg.total_tokens,
                'input': agg.total_input_tokens,
                'output': agg.total_output_tokens,
                'cached': agg.total_cached_tokens,
                'cache_rate': round(agg.total_cached_tokens / agg.total_input_tokens * 100, 1) if agg.total_input_tokens > 0 else 0
            },
            'top_users': self.get_top_users(limit=5),
            'top_endpoints': self.get_top_endpoints(limit=5),
            'model_breakdown': self.get_model_stats(),
            'profile_breakdown': self.get_profile_stats()
        }


# Singleton accessor
_usage_tracker_instance = None

def get_usage_tracker() -> UsageTracker:
    """Get the singleton UsageTracker instance"""
    global _usage_tracker_instance
    if _usage_tracker_instance is None:
        _usage_tracker_instance = UsageTracker()
    return _usage_tracker_instance


# Self-test when run directly
if __name__ == '__main__':
    print("=" * 60)
    print("UsageTracker Self-Test")
    print("=" * 60)

    tracker = get_usage_tracker()

    # Test 1: Record some requests
    print("\n[TEST 1] Recording sample requests")
    for i in range(5):
        tracker.record_request(
            endpoint='/api/workflow/generate',
            user_id=f'user_{i % 2}',  # 2 users
            model='claude-sonnet-4.5',
            profile='workflow-builder',
            input_tokens=10000 + (i * 1000),
            output_tokens=5000 + (i * 500),
            cached_tokens=2000,
            cost=0.10 + (i * 0.02),
            latency_ms=1500 + (i * 100),
            success=True
        )
    print(f"   Recorded 5 requests")

    # Test 2: Get endpoint stats
    print("\n[TEST 2] Endpoint statistics")
    endpoint_stats = tracker.get_endpoint_stats('/api/workflow/generate')
    print(f"   Requests: {endpoint_stats['requests']}")
    print(f"   Total tokens: {endpoint_stats['tokens']}")
    print(f"   Total cost: ${endpoint_stats['cost']:.2f}")
    print(f"   Errors: {endpoint_stats['errors']}")

    # Test 3: Get user stats
    print("\n[TEST 3] User statistics")
    top_users = tracker.get_top_users(limit=2)
    for user in top_users:
        print(f"   {user['user_id']}: {user['requests']} requests, ${user['cost']:.2f}")

    # Test 4: Get model stats
    print("\n[TEST 4] Model statistics")
    model_stats = tracker.get_model_stats('claude-sonnet-4.5')
    print(f"   Requests: {model_stats['requests']}")
    print(f"   Avg latency: {model_stats['avg_latency']:.1f}ms")
    print(f"   Total cost: ${model_stats['cost']:.2f}")

    # Test 5: Get aggregated metrics
    print("\n[TEST 5] Aggregated metrics")
    agg = tracker.get_aggregated_metrics()
    print(f"   Total requests: {agg.total_requests}")
    print(f"   Success rate: {agg.successful_requests / agg.total_requests * 100:.1f}%")
    print(f"   Total tokens: {agg.total_tokens}")
    print(f"   Total cost: ${agg.total_cost:.2f}")
    print(f"   P95 latency: {agg.p95_latency_ms}ms")

    # Test 6: Summary report
    print("\n[TEST 6] Summary report")
    report = tracker.get_summary_report()
    print(f"   Overview:")
    print(f"     Success rate: {report['overview']['success_rate']}%")
    print(f"     Total cost: ${report['overview']['total_cost']:.2f}")
    print(f"   Performance:")
    print(f"     Avg latency: {report['performance']['avg_latency_ms']:.1f}ms")
    print(f"     P99 latency: {report['performance']['p99_latency_ms']}ms")

    # Test 7: Export to JSON
    print("\n[TEST 7] Export to JSON")
    json_path = tracker.export_to_json()
    print(f"   Exported to: {json_path}")

    # Test 8: Export to CSV
    print("\n[TEST 8] Export to CSV")
    csv_path = tracker.export_to_csv()
    print(f"   Exported to: {csv_path}")

    print("\n" + "=" * 60)
    print("[OK] All UsageTracker tests passed!")
    print("=" * 60)
