"""
Alert System - Epic 13: Story 13.8
Manage performance alerts and notifications
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum


class AlertType(Enum):
    """Types of alerts"""
    HIGH_FAILURE_RATE = "high_failure_rate"
    SLOW_EXECUTION = "slow_execution"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    ERROR_SPIKE = "error_spike"
    EXECUTION_TIMEOUT = "execution_timeout"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    """Represents a performance alert"""

    def __init__(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        workflow_id: str = None,
        workflow_name: str = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = f"alert-{datetime.now().timestamp()}"
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.acknowledged = False
        self.acknowledged_at: Optional[datetime] = None

    def acknowledge(self):
        """Mark alert as acknowledged"""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "alertType": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "workflowId": self.workflow_id,
            "workflowName": self.workflow_name,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledgedAt": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class AlertRule:
    """Defines conditions for triggering alerts"""

    def __init__(
        self,
        rule_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        condition: Callable[[Dict[str, Any]], bool],
        message_template: str
    ):
        self.rule_id = rule_id
        self.alert_type = alert_type
        self.severity = severity
        self.condition = condition
        self.message_template = message_template
        self.enabled = True

    def check(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        """Check if rule conditions are met"""
        if not self.enabled:
            return None

        if self.condition(metrics):
            message = self.message_template.format(**metrics)
            return Alert(
                alert_type=self.alert_type,
                severity=self.severity,
                message=message,
                workflow_id=metrics.get("workflowId"),
                workflow_name=metrics.get("workflowName"),
                metadata=metrics
            )

        return None


class AlertManager:
    """Manages alerts and alert rules"""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: Dict[str, AlertRule] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default alert rules"""

        # High failure rate rule
        self.add_rule(AlertRule(
            rule_id="high_failure_rate",
            alert_type=AlertType.HIGH_FAILURE_RATE,
            severity=AlertSeverity.HIGH,
            condition=lambda m: m.get("successRate", 100) < 80,
            message_template="Workflow '{workflowName}' has high failure rate: {successRate:.1f}% success"
        ))

        # Slow execution rule
        self.add_rule(AlertRule(
            rule_id="slow_execution",
            alert_type=AlertType.SLOW_EXECUTION,
            severity=AlertSeverity.MEDIUM,
            condition=lambda m: m.get("averageDurationMs", 0) > 30000,  # 30 seconds
            message_template="Workflow '{workflowName}' is running slowly: {averageDurationMs}ms average"
        ))

        # Error spike rule
        self.add_rule(AlertRule(
            rule_id="error_spike",
            alert_type=AlertType.ERROR_SPIKE,
            severity=AlertSeverity.CRITICAL,
            condition=lambda m: m.get("failedExecutions", 0) > 10 and m.get("successRate", 100) < 50,
            message_template="Error spike detected in '{workflowName}': {failedExecutions} failures"
        ))

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable an alert rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable an alert rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False

    def check_metrics(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against all rules"""
        new_alerts = []

        for rule in self.rules.values():
            alert = rule.check(metrics)
            if alert:
                self.alerts.append(alert)
                new_alerts.append(alert)

        return new_alerts

    def get_alerts(
        self,
        workflow_id: str = None,
        acknowledged: bool = None,
        severity: AlertSeverity = None
    ) -> List[Alert]:
        """Get alerts with optional filtering"""
        filtered = self.alerts

        if workflow_id:
            filtered = [a for a in filtered if a.workflow_id == workflow_id]

        if acknowledged is not None:
            filtered = [a for a in filtered if a.acknowledged == acknowledged]

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        return filtered

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                return True
        return False

    def clear_old_alerts(self, days: int = 30):
        """Clear alerts older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        self.alerts = [
            a for a in self.alerts
            if a.created_at.timestamp() > cutoff
        ]
