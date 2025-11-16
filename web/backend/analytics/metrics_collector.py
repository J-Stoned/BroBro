"""
Metrics Collection Engine - Epic 13: Story 13.1
Collect and store workflow execution metrics for analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json


class ExecutionStatus(Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepExecution:
    """Represents execution of a single workflow step"""

    def __init__(
        self,
        execution_id: str,
        step_id: str,
        step_name: str,
        step_type: str,
        started_at: datetime = None
    ):
        self.execution_id = execution_id
        self.step_id = step_id
        self.step_name = step_name
        self.step_type = step_type
        self.started_at = started_at or datetime.now()
        self.completed_at: Optional[datetime] = None
        self.duration_ms: Optional[int] = None
        self.status = ExecutionStatus.RUNNING
        self.error_message: Optional[str] = None
        self.input_data: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def complete(self, status: ExecutionStatus = ExecutionStatus.COMPLETED, error: str = None):
        """Mark step as completed"""
        self.completed_at = datetime.now()
        self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.status = status
        if error:
            self.error_message = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "executionId": self.execution_id,
            "stepId": self.step_id,
            "stepName": self.step_name,
            "stepType": self.step_type,
            "startedAt": self.started_at.isoformat(),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "durationMs": self.duration_ms,
            "status": self.status.value,
            "errorMessage": self.error_message,
            "inputData": self.input_data,
            "outputData": self.output_data,
            "metadata": self.metadata
        }


class WorkflowExecution:
    """Represents a complete workflow execution"""

    def __init__(
        self,
        execution_id: str,
        workflow_id: str,
        workflow_name: str,
        trigger_type: str = "manual"
    ):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.trigger_type = trigger_type
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.duration_ms: Optional[int] = None
        self.status = ExecutionStatus.RUNNING
        self.total_steps = 0
        self.completed_steps = 0
        self.failed_steps = 0
        self.error_message: Optional[str] = None
        self.trigger_data: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.steps: List[StepExecution] = []

    def add_step(self, step: StepExecution):
        """Add a step execution"""
        self.steps.append(step)
        self.total_steps = len(self.steps)

    def complete(self, status: ExecutionStatus = ExecutionStatus.COMPLETED, error: str = None):
        """Mark execution as completed"""
        self.completed_at = datetime.now()
        self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.status = status
        if error:
            self.error_message = error

        # Count completed and failed steps
        self.completed_steps = sum(1 for s in self.steps if s.status == ExecutionStatus.COMPLETED)
        self.failed_steps = sum(1 for s in self.steps if s.status == ExecutionStatus.FAILED)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "executionId": self.execution_id,
            "workflowId": self.workflow_id,
            "workflowName": self.workflow_name,
            "triggerType": self.trigger_type,
            "startedAt": self.started_at.isoformat(),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "durationMs": self.duration_ms,
            "status": self.status.value,
            "totalSteps": self.total_steps,
            "completedSteps": self.completed_steps,
            "failedSteps": self.failed_steps,
            "errorMessage": self.error_message,
            "triggerData": self.trigger_data,
            "context": self.context,
            "steps": [s.to_dict() for s in self.steps]
        }


class MetricsCollector:
    """Collects and manages workflow execution metrics"""

    def __init__(self, retention_days: int = 90):
        """
        Initialize metrics collector

        Args:
            retention_days: Number of days to retain execution data (default: 90)
        """
        self.retention_days = retention_days
        self.executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []

    def start_execution(
        self,
        execution_id: str,
        workflow_id: str,
        workflow_name: str,
        trigger_type: str = "manual",
        trigger_data: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """Start tracking a new workflow execution"""
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            trigger_type=trigger_type
        )
        if trigger_data:
            execution.trigger_data = trigger_data

        self.executions[execution_id] = execution
        return execution

    def start_step(
        self,
        execution_id: str,
        step_id: str,
        step_name: str,
        step_type: str,
        input_data: Dict[str, Any] = None
    ) -> Optional[StepExecution]:
        """Start tracking a step execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None

        step = StepExecution(
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            step_type=step_type
        )
        if input_data:
            step.input_data = input_data

        execution.add_step(step)
        return step

    def complete_step(
        self,
        execution_id: str,
        step_id: str,
        status: ExecutionStatus = ExecutionStatus.COMPLETED,
        output_data: Dict[str, Any] = None,
        error: str = None
    ) -> bool:
        """Mark a step as completed"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False

        for step in execution.steps:
            if step.step_id == step_id:
                step.complete(status=status, error=error)
                if output_data:
                    step.output_data = output_data
                return True

        return False

    def complete_execution(
        self,
        execution_id: str,
        status: ExecutionStatus = ExecutionStatus.COMPLETED,
        error: str = None
    ) -> bool:
        """Mark an execution as completed"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False

        execution.complete(status=status, error=error)

        # Move to history
        self.execution_history.append(execution)
        del self.executions[execution_id]

        # Clean old data
        self._cleanup_old_data()

        return True

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution by ID (checks both active and history)"""
        # Check active executions
        if execution_id in self.executions:
            return self.executions[execution_id]

        # Check history
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution

        return None

    def get_workflow_metrics(
        self,
        workflow_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get aggregated metrics for a workflow"""
        # Filter executions
        executions = [
            e for e in self.execution_history
            if e.workflow_id == workflow_id
        ]

        if start_date:
            executions = [e for e in executions if e.started_at >= start_date]
        if end_date:
            executions = [e for e in executions if e.started_at <= end_date]

        if not executions:
            return {
                "workflowId": workflow_id,
                "totalExecutions": 0,
                "successfulExecutions": 0,
                "failedExecutions": 0,
                "successRate": 0,
                "averageDurationMs": 0,
                "minDurationMs": 0,
                "maxDurationMs": 0,
                "totalDurationMs": 0
            }

        # Calculate metrics
        total = len(executions)
        successful = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)

        durations = [e.duration_ms for e in executions if e.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        total_duration = sum(durations)

        return {
            "workflowId": workflow_id,
            "totalExecutions": total,
            "successfulExecutions": successful,
            "failedExecutions": failed,
            "successRate": (successful / total * 100) if total > 0 else 0,
            "averageDurationMs": int(avg_duration),
            "minDurationMs": min_duration,
            "maxDurationMs": max_duration,
            "totalDurationMs": total_duration,
            "executions": [e.to_dict() for e in executions]
        }

    def get_global_metrics(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get aggregated metrics across all workflows"""
        executions = self.execution_history.copy()

        if start_date:
            executions = [e for e in executions if e.started_at >= start_date]
        if end_date:
            executions = [e for e in executions if e.started_at <= end_date]

        if not executions:
            return {
                "totalExecutions": 0,
                "successfulExecutions": 0,
                "failedExecutions": 0,
                "runningExecutions": len(self.executions),
                "successRate": 0,
                "averageDurationMs": 0,
                "totalWorkflows": 0
            }

        # Calculate metrics
        total = len(executions)
        successful = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)

        durations = [e.duration_ms for e in executions if e.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Count unique workflows
        unique_workflows = len(set(e.workflow_id for e in executions))

        return {
            "totalExecutions": total,
            "successfulExecutions": successful,
            "failedExecutions": failed,
            "runningExecutions": len(self.executions),
            "successRate": (successful / total * 100) if total > 0 else 0,
            "averageDurationMs": int(avg_duration),
            "totalWorkflows": unique_workflows,
            "executions": [e.to_dict() for e in executions[-100:]]  # Last 100 executions
        }

    def get_step_metrics(
        self,
        workflow_id: str = None,
        step_type: str = None
    ) -> Dict[str, Any]:
        """Get metrics for workflow steps"""
        all_steps = []

        for execution in self.execution_history:
            if workflow_id and execution.workflow_id != workflow_id:
                continue
            all_steps.extend(execution.steps)

        if step_type:
            all_steps = [s for s in all_steps if s.step_type == step_type]

        if not all_steps:
            return {
                "totalSteps": 0,
                "averageDurationMs": 0,
                "stepsByType": {}
            }

        # Group by step type
        steps_by_type = {}
        for step in all_steps:
            if step.step_type not in steps_by_type:
                steps_by_type[step.step_type] = []
            steps_by_type[step.step_type].append(step)

        # Calculate metrics per type
        type_metrics = {}
        for stype, steps in steps_by_type.items():
            durations = [s.duration_ms for s in steps if s.duration_ms is not None]
            successful = sum(1 for s in steps if s.status == ExecutionStatus.COMPLETED)

            type_metrics[stype] = {
                "count": len(steps),
                "successfulCount": successful,
                "successRate": (successful / len(steps) * 100) if steps else 0,
                "averageDurationMs": int(sum(durations) / len(durations)) if durations else 0
            }

        durations = [s.duration_ms for s in all_steps if s.duration_ms is not None]

        return {
            "totalSteps": len(all_steps),
            "averageDurationMs": int(sum(durations) / len(durations)) if durations else 0,
            "stepsByType": type_metrics
        }

    def _cleanup_old_data(self):
        """Remove executions older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        self.execution_history = [
            e for e in self.execution_history
            if e.started_at >= cutoff_date
        ]
