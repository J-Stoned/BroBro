"""
Performance Analysis Engine - Epic 13: Story 13.2
Analyze workflow performance, detect bottlenecks, and identify patterns
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class BottleneckDetector:
    """Detects performance bottlenecks in workflows"""

    def __init__(self, threshold_percentile: float = 95):
        """
        Initialize bottleneck detector

        Args:
            threshold_percentile: Percentile to use for bottleneck detection (default: 95)
        """
        self.threshold_percentile = threshold_percentile

    def analyze_workflow(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow for bottlenecks"""
        if not executions:
            return {"bottlenecks": [], "recommendations": []}

        # Collect step durations
        step_durations = defaultdict(list)

        for execution in executions:
            for step in execution.get("steps", []):
                if step.get("durationMs"):
                    step_durations[step["stepId"]].append({
                        "duration": step["durationMs"],
                        "name": step["stepName"],
                        "type": step["stepType"]
                    })

        # Calculate statistics and find bottlenecks
        bottlenecks = []

        for step_id, durations in step_durations.items():
            if len(durations) < 3:  # Need at least 3 samples
                continue

            duration_values = [d["duration"] for d in durations]
            avg_duration = statistics.mean(duration_values)
            p95_duration = self._percentile(duration_values, self.threshold_percentile)

            # Consider it a bottleneck if p95 > 2x average
            if p95_duration > avg_duration * 2:
                bottlenecks.append({
                    "stepId": step_id,
                    "stepName": durations[0]["name"],
                    "stepType": durations[0]["type"],
                    "averageDurationMs": int(avg_duration),
                    "p95DurationMs": int(p95_duration),
                    "maxDurationMs": max(duration_values),
                    "executionCount": len(durations),
                    "severity": self._calculate_severity(avg_duration, p95_duration)
                })

        # Sort by severity
        bottlenecks.sort(key=lambda x: x["p95DurationMs"], reverse=True)

        # Generate recommendations
        recommendations = self._generate_recommendations(bottlenecks)

        return {
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "totalStepsAnalyzed": len(step_durations)
        }

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _calculate_severity(self, avg: float, p95: float) -> str:
        """Calculate bottleneck severity"""
        ratio = p95 / avg if avg > 0 else 0

        if ratio > 5:
            return "critical"
        elif ratio > 3:
            return "high"
        elif ratio > 2:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        for bottleneck in bottlenecks[:5]:  # Top 5 bottlenecks
            step_type = bottleneck["stepType"]
            step_name = bottleneck["stepName"]

            if step_type == "http_request":
                recommendations.append(
                    f"Consider caching results or using async processing for '{step_name}' HTTP requests"
                )
            elif step_type == "transform_data":
                recommendations.append(
                    f"Optimize data transformation logic in '{step_name}' to reduce processing time"
                )
            elif step_type == "delay":
                recommendations.append(
                    f"Review delay configuration in '{step_name}' - consider if delay is necessary"
                )
            else:
                recommendations.append(
                    f"Investigate slow execution of '{step_name}' ({step_type})"
                )

        return recommendations


class PerformanceAnalyzer:
    """Analyzes workflow performance and trends"""

    def __init__(self):
        self.bottleneck_detector = BottleneckDetector()

    def analyze_trends(
        self,
        executions: List[Dict[str, Any]],
        interval: str = "daily"
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            executions: List of execution dictionaries
            interval: Grouping interval ('hourly', 'daily', 'weekly')
        """
        if not executions:
            return {"trends": [], "summary": {}}

        # Group executions by time interval
        grouped = self._group_by_interval(executions, interval)

        trends = []
        for period, period_executions in grouped.items():
            total = len(period_executions)
            successful = sum(1 for e in period_executions if e["status"] == "completed")
            failed = sum(1 for e in period_executions if e["status"] == "failed")

            durations = [e["durationMs"] for e in period_executions if e.get("durationMs")]
            avg_duration = statistics.mean(durations) if durations else 0

            trends.append({
                "period": period,
                "totalExecutions": total,
                "successfulExecutions": successful,
                "failedExecutions": failed,
                "successRate": (successful / total * 100) if total > 0 else 0,
                "averageDurationMs": int(avg_duration)
            })

        # Calculate summary statistics
        all_success_rates = [t["successRate"] for t in trends]
        all_durations = [t["averageDurationMs"] for t in trends if t["averageDurationMs"] > 0]

        summary = {
            "averageSuccessRate": statistics.mean(all_success_rates) if all_success_rates else 0,
            "successRateTrend": self._calculate_trend(all_success_rates),
            "averageDuration": int(statistics.mean(all_durations)) if all_durations else 0,
            "durationTrend": self._calculate_trend(all_durations)
        }

        return {
            "trends": trends,
            "summary": summary
        }

    def detect_error_patterns(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect common error patterns"""
        error_executions = [e for e in executions if e["status"] == "failed"]

        if not error_executions:
            return {"patterns": [], "totalErrors": 0}

        # Group errors by message
        error_groups = defaultdict(list)

        for execution in error_executions:
            error_msg = execution.get("errorMessage", "Unknown error")
            # Extract key part of error message
            error_key = self._extract_error_key(error_msg)
            error_groups[error_key].append(execution)

        # Create pattern list
        patterns = []
        for error_key, error_list in error_groups.items():
            patterns.append({
                "errorPattern": error_key,
                "occurrences": len(error_list),
                "percentage": (len(error_list) / len(error_executions) * 100),
                "firstSeen": min(e["startedAt"] for e in error_list),
                "lastSeen": max(e["startedAt"] for e in error_list),
                "affectedWorkflows": list(set(e["workflowId"] for e in error_list))
            })

        # Sort by occurrences
        patterns.sort(key=lambda x: x["occurrences"], reverse=True)

        return {
            "patterns": patterns,
            "totalErrors": len(error_executions),
            "uniquePatterns": len(patterns)
        }

    def calculate_success_rate_by_trigger(
        self,
        executions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate success rates grouped by trigger type"""
        trigger_groups = defaultdict(list)

        for execution in executions:
            trigger_type = execution.get("triggerType", "unknown")
            trigger_groups[trigger_type].append(execution)

        results = {}
        for trigger_type, trigger_executions in trigger_groups.items():
            total = len(trigger_executions)
            successful = sum(1 for e in trigger_executions if e["status"] == "completed")

            results[trigger_type] = {
                "totalExecutions": total,
                "successfulExecutions": successful,
                "successRate": (successful / total * 100) if total > 0 else 0
            }

        return results

    def identify_slow_steps(
        self,
        executions: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Identify the slowest workflow steps"""
        all_steps = []

        for execution in executions:
            for step in execution.get("steps", []):
                if step.get("durationMs"):
                    all_steps.append(step)

        # Sort by duration
        all_steps.sort(key=lambda x: x["durationMs"], reverse=True)

        return all_steps[:top_n]

    def _group_by_interval(
        self,
        executions: List[Dict[str, Any]],
        interval: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group executions by time interval"""
        grouped = defaultdict(list)

        for execution in executions:
            started_at = datetime.fromisoformat(execution["startedAt"].replace('Z', '+00:00'))

            if interval == "hourly":
                period = started_at.strftime("%Y-%m-%d %H:00")
            elif interval == "daily":
                period = started_at.strftime("%Y-%m-%d")
            elif interval == "weekly":
                period = started_at.strftime("%Y-W%W")
            else:
                period = started_at.strftime("%Y-%m-%d")

            grouped[period].append(execution)

        return grouped

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if trend is increasing, decreasing, or stable"""
        if len(values) < 2:
            return "stable"

        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"

    def _extract_error_key(self, error_message: str) -> str:
        """Extract key part of error message for grouping"""
        # Remove specific values/IDs to group similar errors
        import re

        # Remove numbers
        key = re.sub(r'\d+', 'N', error_message)

        # Remove quotes
        key = re.sub(r'["\']', '', key)

        # Take first 100 chars
        key = key[:100]

        return key
