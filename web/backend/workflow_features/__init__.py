"""
Workflow Features Module - Epic 12
Advanced workflow capabilities for GHL WHIZ
"""

from .conditions import evaluate_condition, evaluate_condition_group, ConditionType, LogicOperator

__all__ = ['evaluate_condition', 'evaluate_condition_group', 'ConditionType', 'LogicOperator']
