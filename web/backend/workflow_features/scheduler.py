"""
Workflow Scheduler - Epic 12: Story 12.7
Schedule workflows with cron expressions and timezone support
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import re


class ScheduleType(Enum):
    """Schedule types"""
    ONCE = "once"
    RECURRING = "recurring"
    CRON = "cron"


class Schedule:
    """Represents a workflow schedule"""

    def __init__(
        self,
        schedule_type: str,
        config: Dict[str, Any] = None,
        timezone: str = "UTC"
    ):
        self.type = ScheduleType(schedule_type) if isinstance(schedule_type, str) else schedule_type
        self.config = config or {}
        self.timezone = timezone
        self.enabled = True

    def get_next_run(self) -> Optional[datetime]:
        """Calculate next run time"""
        if not self.enabled:
            return None

        if self.type == ScheduleType.ONCE:
            run_at = self.config.get("runAt")
            if run_at:
                return datetime.fromisoformat(run_at)

        elif self.type == ScheduleType.RECURRING:
            interval = self.config.get("interval", 60)  # minutes
            last_run = self.config.get("lastRun")

            if last_run:
                last_run_dt = datetime.fromisoformat(last_run)
                return last_run_dt + timedelta(minutes=interval)
            else:
                return datetime.now()

        elif self.type == ScheduleType.CRON:
            # Parse cron expression (simplified)
            cron = self.config.get("cron", "0 * * * *")
            # For production, use a cron parsing library
            return datetime.now() + timedelta(hours=1)

        return None

    def should_run_now(self) -> bool:
        """Check if schedule should run now"""
        if not self.enabled:
            return False

        next_run = self.get_next_run()
        if next_run:
            return datetime.now() >= next_run

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "config": self.config,
            "timezone": self.timezone,
            "enabled": self.enabled,
            "nextRun": self.get_next_run().isoformat() if self.get_next_run() else None
        }


class ScheduleManager:
    """Manages workflow schedules"""

    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}

    def add_schedule(self, workflow_id: str, schedule: Schedule) -> bool:
        """Add a schedule"""
        self.schedules[workflow_id] = schedule
        return True

    def remove_schedule(self, workflow_id: str) -> bool:
        """Remove a schedule"""
        if workflow_id in self.schedules:
            del self.schedules[workflow_id]
            return True
        return False

    def get_schedule(self, workflow_id: str) -> Optional[Schedule]:
        """Get a schedule"""
        return self.schedules.get(workflow_id)

    def get_due_workflows(self) -> List[str]:
        """Get workflows that are due to run"""
        due_workflows = []

        for workflow_id, schedule in self.schedules.items():
            if schedule.should_run_now():
                due_workflows.append(workflow_id)

        return due_workflows

    def enable_schedule(self, workflow_id: str) -> bool:
        """Enable a schedule"""
        schedule = self.schedules.get(workflow_id)
        if schedule:
            schedule.enabled = True
            return True
        return False

    def disable_schedule(self, workflow_id: str) -> bool:
        """Disable a schedule"""
        schedule = self.schedules.get(workflow_id)
        if schedule:
            schedule.enabled = False
            return True
        return False


def validate_cron_expression(cron: str) -> Dict[str, Any]:
    """Validate cron expression"""
    errors = []

    # Basic cron format: minute hour day month weekday
    parts = cron.split()

    if len(parts) != 5:
        errors.append("Cron expression must have 5 parts: minute hour day month weekday")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def parse_schedule_description(schedule: Schedule) -> str:
    """Generate human-readable schedule description"""
    if schedule.type == ScheduleType.ONCE:
        run_at = schedule.config.get("runAt")
        return f"Run once at {run_at}"

    elif schedule.type == ScheduleType.RECURRING:
        interval = schedule.config.get("interval", 60)
        unit = schedule.config.get("unit", "minutes")
        return f"Run every {interval} {unit}"

    elif schedule.type == ScheduleType.CRON:
        cron = schedule.config.get("cron", "0 * * * *")
        return f"Run on schedule: {cron}"

    return "No schedule"
