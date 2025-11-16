"""
Condition Evaluation Engine - Epic 12: Story 12.1
Evaluates workflow conditions with multiple operators and logic
"""

from typing import Dict, Any, List
from enum import Enum
import re


class ConditionType(Enum):
    """Available condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    MATCHES_REGEX = "matches_regex"


class LogicOperator(Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"


def get_nested_value(data: Dict, path: str) -> Any:
    """
    Get nested value using dot notation.
    Example: "contact.email" from {"contact": {"email": "test@test.com"}}

    Args:
        data: Dictionary to extract from
        path: Dot-separated path (e.g., "contact.email")

    Returns:
        Value at path, or None if not found
    """
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


def evaluate_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """
    Evaluate a single condition against context data.

    Args:
        condition: {
            "field": "contact.email",
            "operator": "contains",
            "value": "@gmail.com"
        }
        context: {"contact": {"email": "user@gmail.com"}}

    Returns:
        bool: True if condition passes
    """
    try:
        field_path = condition.get("field", "")
        operator_str = condition.get("operator", "equals")
        expected_value = condition.get("value")

        # Get actual value from context
        actual_value = get_nested_value(context, field_path)

        # Parse operator
        try:
            operator = ConditionType(operator_str)
        except ValueError:
            # Default to equals if invalid operator
            operator = ConditionType.EQUALS

        # Evaluate based on operator
        if operator == ConditionType.EQUALS:
            return actual_value == expected_value

        elif operator == ConditionType.NOT_EQUALS:
            return actual_value != expected_value

        elif operator == ConditionType.CONTAINS:
            if actual_value is None:
                return False
            return expected_value in str(actual_value)

        elif operator == ConditionType.NOT_CONTAINS:
            if actual_value is None:
                return True
            return expected_value not in str(actual_value)

        elif operator == ConditionType.GREATER_THAN:
            try:
                return float(actual_value) > float(expected_value)
            except (TypeError, ValueError):
                return False

        elif operator == ConditionType.LESS_THAN:
            try:
                return float(actual_value) < float(expected_value)
            except (TypeError, ValueError):
                return False

        elif operator == ConditionType.STARTS_WITH:
            if actual_value is None:
                return False
            return str(actual_value).startswith(str(expected_value))

        elif operator == ConditionType.ENDS_WITH:
            if actual_value is None:
                return False
            return str(actual_value).endswith(str(expected_value))

        elif operator == ConditionType.IS_EMPTY:
            return not actual_value or actual_value == "" or actual_value == []

        elif operator == ConditionType.IS_NOT_EMPTY:
            return bool(actual_value) and actual_value != "" and actual_value != []

        elif operator == ConditionType.MATCHES_REGEX:
            if actual_value is None:
                return False
            try:
                return bool(re.match(str(expected_value), str(actual_value)))
            except re.error:
                return False

        return False

    except Exception as e:
        print(f"Error evaluating condition: {e}")
        return False


def evaluate_condition_group(
    conditions: List[Dict[str, Any]],
    logic_operator: str,
    context: Dict[str, Any]
) -> bool:
    """
    Evaluate multiple conditions with AND/OR logic.

    Args:
        conditions: List of condition dicts
        logic_operator: "and" or "or"
        context: Data to evaluate against

    Returns:
        bool: True if condition group passes
    """
    if not conditions:
        return True  # Empty conditions default to true

    try:
        # Parse logic operator
        try:
            operator = LogicOperator(logic_operator.lower())
        except ValueError:
            operator = LogicOperator.AND  # Default to AND

        # Evaluate all conditions
        results = [evaluate_condition(cond, context) for cond in conditions]

        if operator == LogicOperator.AND:
            return all(results)
        elif operator == LogicOperator.OR:
            return any(results)

        return False

    except Exception as e:
        print(f"Error evaluating condition group: {e}")
        return False
