"""
Performance Monitoring Middleware
Tracks response times, identifies slow endpoints, and monitors resource usage
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.error_logger import StructuredLogger
from collections import defaultdict
from datetime import datetime, timedelta

logger = StructuredLogger('performance_middleware')


class PerformanceMetrics:
    """
    In-memory metrics tracker for endpoint performance
    """

    def __init__(self):
        self.endpoint_times = defaultdict(list)
        self.slow_request_threshold = 1000  # ms
        self.last_report = datetime.now()
        self.report_interval = 3600  # seconds (1 hour)

    def record_request(self, endpoint: str, duration_ms: float) -> None:
        """Record a request duration for an endpoint"""
        self.endpoint_times[endpoint].append({
            'duration_ms': duration_ms,
            'timestamp': datetime.now(),
            'is_slow': duration_ms > self.slow_request_threshold
        })

        # Cleanup old entries (keep last 1000 requests per endpoint)
        if len(self.endpoint_times[endpoint]) > 1000:
            self.endpoint_times[endpoint] = self.endpoint_times[endpoint][-1000:]

    def get_endpoint_stats(self, endpoint: str) -> dict:
        """Get performance statistics for an endpoint"""
        times = self.endpoint_times.get(endpoint, [])
        if not times:
            return {}

        durations = [t['duration_ms'] for t in times]
        slow_count = sum(1 for t in times if t['is_slow'])

        return {
            'endpoint': endpoint,
            'request_count': len(durations),
            'avg_duration_ms': round(sum(durations) / len(durations), 2),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'p95_duration_ms': self._percentile(durations, 0.95),
            'p99_duration_ms': self._percentile(durations, 0.99),
            'slow_request_count': slow_count,
            'slow_request_percentage': round((slow_count / len(durations)) * 100, 2) if durations else 0
        }

    @staticmethod
    def _percentile(data: list, percentile: float) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return float(sorted_data[min(index, len(sorted_data) - 1)])

    def should_report(self) -> bool:
        """Check if enough time has passed to report metrics"""
        return (datetime.now() - self.last_report).total_seconds() >= self.report_interval

    def get_all_stats(self) -> list:
        """Get statistics for all endpoints"""
        return [self.get_endpoint_stats(ep) for ep in self.endpoint_times.keys()]

    def reset_reports(self) -> None:
        """Reset the report timer"""
        self.last_report = datetime.now()


# Global metrics instance
metrics = PerformanceMetrics()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking endpoint performance and identifying bottlenecks
    """

    EXCLUDED_PATHS = {
        '/health',
        '/api/health',
        '/docs',
        '/openapi.json',
        '/favicon.ico'
    }

    async def dispatch(self, request: Request, call_next):
        """
        Track performance of all requests
        """
        # Skip performance tracking for health checks
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()
        endpoint_key = f"{request.method} {request.url.path}"

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            metrics.record_request(endpoint_key, duration_ms)

            # Log slow requests
            if duration_ms > metrics.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {endpoint_key}",
                    error_type='SLOW_REQUEST',
                    context={
                        'endpoint': endpoint_key,
                        'duration_ms': round(duration_ms, 2),
                        'threshold_ms': metrics.slow_request_threshold,
                        'status_code': response.status_code
                    }
                )

            # Log periodic metrics if interval exceeded
            if metrics.should_report():
                stats = metrics.get_all_stats()
                logger.info(
                    "Performance report",
                    context={
                        'metrics': {
                            'endpoints': stats,
                            'report_timestamp': datetime.now().isoformat()
                        }
                    }
                )
                metrics.reset_reports()

            # Add performance headers
            response.headers['X-Response-Time'] = str(round(duration_ms, 2))

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Error in request: {endpoint_key}",
                error_type='REQUEST_ERROR',
                context={
                    'endpoint': endpoint_key,
                    'duration_ms': round(duration_ms, 2),
                    'error': str(e)
                },
                exc_info=True
            )
            raise


def get_performance_stats():
    """
    Endpoint to retrieve current performance statistics
    Useful for monitoring/debugging
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'endpoints': metrics.get_all_stats()
    }
