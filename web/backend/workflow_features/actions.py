"""
Advanced Actions - Epic 12: Story 12.4
HTTP requests, data transformations, and custom code execution
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import json


class ActionType(Enum):
    """Available action types"""
    HTTP_REQUEST = "http_request"
    TRANSFORM_DATA = "transform_data"
    CUSTOM_CODE = "custom_code"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    UPDATE_CONTACT = "update_contact"
    CREATE_OPPORTUNITY = "create_opportunity"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    DELAY = "delay"


class Action:
    """Represents a workflow action"""

    def __init__(
        self,
        action_type: str,
        config: Dict[str, Any] = None,
        name: str = ""
    ):
        self.type = ActionType(action_type) if isinstance(action_type, str) else action_type
        self.config = config or {}
        self.name = name or action_type

    def validate(self) -> Dict[str, Any]:
        """Validate action configuration"""
        errors = []

        if self.type == ActionType.HTTP_REQUEST:
            if not self.config.get("url"):
                errors.append("URL is required for HTTP request")
            if not self.config.get("method"):
                errors.append("HTTP method is required")

        elif self.type == ActionType.SEND_EMAIL:
            if not self.config.get("to"):
                errors.append("Recipient email is required")
            if not self.config.get("subject"):
                errors.append("Email subject is required")

        elif self.type == ActionType.SEND_SMS:
            if not self.config.get("to"):
                errors.append("Phone number is required")
            if not self.config.get("message"):
                errors.append("SMS message is required")

        elif self.type == ActionType.TRANSFORM_DATA:
            if not self.config.get("transformations"):
                errors.append("Transformations are required")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "name": self.name,
            "config": self.config
        }


class DataTransformer:
    """Transform data using various operations"""

    @staticmethod
    def transform(data: Any, transformations: List[Dict[str, Any]]) -> Any:
        """Apply transformations to data"""
        result = data

        for transform in transformations:
            operation = transform.get("operation")

            if operation == "map":
                # Map object keys
                mapping = transform.get("mapping", {})
                if isinstance(result, dict):
                    result = {mapping.get(k, k): v for k, v in result.items()}

            elif operation == "filter":
                # Filter array items
                if isinstance(result, list):
                    condition = transform.get("condition", {})
                    result = [item for item in result if DataTransformer._check_condition(item, condition)]

            elif operation == "extract":
                # Extract nested value
                path = transform.get("path", "")
                result = DataTransformer._get_nested_value(result, path)

            elif operation == "format":
                # Format string
                template = transform.get("template", "")
                if isinstance(result, dict):
                    result = template.format(**result)

            elif operation == "split":
                # Split string
                delimiter = transform.get("delimiter", ",")
                if isinstance(result, str):
                    result = result.split(delimiter)

            elif operation == "join":
                # Join array
                delimiter = transform.get("delimiter", ",")
                if isinstance(result, list):
                    result = delimiter.join(str(x) for x in result)

        return result

    @staticmethod
    def _check_condition(item: Any, condition: Dict[str, Any]) -> bool:
        """Check if item matches condition"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        item_value = DataTransformer._get_nested_value(item, field)

        if operator == "equals":
            return item_value == value
        elif operator == "contains":
            return value in str(item_value)
        elif operator == "greater_than":
            return float(item_value) > float(value)

        return True

    @staticmethod
    def _get_nested_value(data: Any, path: str) -> Any:
        """Get nested value using dot notation"""
        if not path:
            return data

        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)]
            else:
                return None

            if value is None:
                return None

        return value
