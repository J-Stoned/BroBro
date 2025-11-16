"""
Variable System - Epic 12: Story 12.2
Manage workflow variables with type validation and resolution
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import re


class VariableType(Enum):
    """Available variable types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class Variable:
    """Represents a workflow variable"""

    def __init__(
        self,
        name: str,
        var_type: str,
        default_value: Any = None,
        description: str = ""
    ):
        self.name = name
        self.type = VariableType(var_type) if isinstance(var_type, str) else var_type
        self.default_value = default_value
        self.description = description

    def validate_value(self, value: Any) -> bool:
        """Validate value matches variable type"""
        if value is None:
            return True  # None is valid for any type

        if self.type == VariableType.TEXT:
            return isinstance(value, str)
        elif self.type == VariableType.NUMBER:
            return isinstance(value, (int, float))
        elif self.type == VariableType.DATE:
            # Check if valid date string or datetime object
            if isinstance(value, datetime):
                return True
            try:
                datetime.fromisoformat(str(value))
                return True
            except:
                return False
        elif self.type == VariableType.BOOLEAN:
            return isinstance(value, bool)
        elif self.type == VariableType.ARRAY:
            return isinstance(value, list)
        elif self.type == VariableType.OBJECT:
            return isinstance(value, dict)

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type.value,
            "defaultValue": self.default_value,
            "description": self.description
        }


class VariableManager:
    """Manages workflow variables"""

    def __init__(self):
        self.variables: Dict[str, Variable] = {}

    def add_variable(self, variable: Variable) -> bool:
        """Add a variable to the manager"""
        if variable.name in self.variables:
            return False  # Already exists

        self.variables[variable.name] = variable
        return True

    def remove_variable(self, name: str) -> bool:
        """Remove a variable"""
        if name in self.variables:
            del self.variables[name]
            return True
        return False

    def get_variable(self, name: str) -> Optional[Variable]:
        """Get a variable by name"""
        return self.variables.get(name)

    def list_variables(self) -> List[Dict[str, Any]]:
        """List all variables"""
        return [v.to_dict() for v in self.variables.values()]

    def load_from_list(self, variables_list: List[Dict[str, Any]]) -> None:
        """Load variables from a list of dicts"""
        self.variables = {}
        for var_dict in variables_list:
            try:
                variable = Variable(
                    name=var_dict.get("name", ""),
                    var_type=var_dict.get("type", "text"),
                    default_value=var_dict.get("defaultValue"),
                    description=var_dict.get("description", "")
                )
                self.variables[variable.name] = variable
            except Exception as e:
                print(f"Error loading variable: {e}")

    def resolve_variable_references(self, text: str, context: Dict[str, Any]) -> str:
        """
        Replace variable references like {{variableName}} with actual values.

        Example:
            text: "Hello {{contact.firstName}}, your order is {{orderStatus}}"
            context: {"contact": {"firstName": "John"}, "orderStatus": "shipped"}
            returns: "Hello John, your order is shipped"
        """
        if not text:
            return text

        # Find all {{variableName}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, text)

        result = text
        for match in matches:
            # Get value from context using dot notation
            value = self._get_nested_value(context, match.strip())
            if value is not None:
                result = result.replace(f"{{{{{match}}}}}", str(value))

        return result

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value using dot notation"""
        if not path or not isinstance(data, dict):
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


def resolve_variables_in_text(text: str, context: Dict[str, Any]) -> str:
    """
    Standalone function to resolve variables in text.
    Useful for quick variable resolution without VariableManager instance.

    Args:
        text: Text containing {{variable}} references
        context: Dictionary with variable values

    Returns:
        Text with variables replaced by their values
    """
    if not text:
        return text

    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, text)

    result = text
    for match in matches:
        # Get value from context
        keys = match.strip().split(".")
        value = context

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

            if value is None:
                break

        if value is not None:
            result = result.replace(f"{{{{{match}}}}}", str(value))

    return result
