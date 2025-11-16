"""
Custom Trigger System - Epic 12: Story 12.3
Support for webhook, form, tag, and event-based triggers
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class TriggerType(Enum):
    """Available trigger types"""
    WEBHOOK = "webhook"
    FORM_SUBMISSION = "form_submission"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    CONTACT_CREATED = "contact_created"
    OPPORTUNITY_CREATED = "opportunity_created"
    APPOINTMENT_BOOKED = "appointment_booked"
    CUSTOM_EVENT = "custom_event"


class Trigger:
    """Represents a workflow trigger"""

    def __init__(
        self,
        trigger_type: str,
        config: Dict[str, Any] = None,
        filters: List[Dict[str, Any]] = None
    ):
        self.type = TriggerType(trigger_type) if isinstance(trigger_type, str) else trigger_type
        self.config = config or {}
        self.filters = filters or []
        self.created_at = datetime.now().isoformat()

    def matches_event(self, event_data: Dict[str, Any]) -> bool:
        """Check if event matches this trigger"""
        if not self.filters:
            return True  # No filters = match all

        for filter_rule in self.filters:
            field = filter_rule.get("field")
            operator = filter_rule.get("operator")
            value = filter_rule.get("value")

            event_value = self._get_nested_value(event_data, field)

            if operator == "equals" and event_value != value:
                return False
            elif operator == "contains" and value not in str(event_value):
                return False
            elif operator == "starts_with" and not str(event_value).startswith(value):
                return False

        return True

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value using dot notation"""
        if not path:
            return None

        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

            if value is None:
                return None

        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "config": self.config,
            "filters": self.filters,
            "createdAt": self.created_at
        }


class TriggerManager:
    """Manages workflow triggers"""

    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}

    def add_trigger(self, trigger_id: str, trigger: Trigger) -> bool:
        """Add a trigger"""
        self.triggers[trigger_id] = trigger
        return True

    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger"""
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
            return True
        return False

    def get_trigger(self, trigger_id: str) -> Optional[Trigger]:
        """Get a trigger by ID"""
        return self.triggers.get(trigger_id)

    def find_matching_triggers(self, event_data: Dict[str, Any]) -> List[str]:
        """Find all triggers that match the event"""
        matching_ids = []

        for trigger_id, trigger in self.triggers.items():
            if trigger.matches_event(event_data):
                matching_ids.append(trigger_id)

        return matching_ids


def validate_webhook_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate webhook trigger configuration"""
    errors = []

    if not config.get("url"):
        errors.append("Webhook URL is required")

    method = config.get("method", "POST")
    if method not in ["GET", "POST", "PUT", "DELETE"]:
        errors.append("Invalid HTTP method")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_form_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate form submission trigger configuration"""
    errors = []

    if not config.get("formId"):
        errors.append("Form ID is required")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
