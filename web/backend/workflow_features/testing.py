"""
Workflow Testing Suite - Epic 12: Story 12.9
Debug and test workflows with sample data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class TestResult:
    """Result of a workflow test"""

    def __init__(
        self,
        test_id: str,
        status: TestStatus,
        steps: List[Dict[str, Any]] = None,
        errors: List[str] = None,
        duration_ms: int = 0
    ):
        self.test_id = test_id
        self.status = status
        self.steps = steps or []
        self.errors = errors or []
        self.duration_ms = duration_ms
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "testId": self.test_id,
            "status": self.status.value,
            "steps": self.steps,
            "errors": self.errors,
            "durationMs": self.duration_ms,
            "timestamp": self.timestamp
        }


class WorkflowTester:
    """Test workflow execution"""

    def __init__(self, workflow: Dict[str, Any]):
        self.workflow = workflow
        self.test_data: Dict[str, Any] = {}

    def set_test_data(self, data: Dict[str, Any]):
        """Set sample data for testing"""
        self.test_data = data

    def run_test(self, test_id: str = None) -> TestResult:
        """Execute workflow test"""
        if not test_id:
            test_id = f"test_{datetime.now().timestamp()}"

        start_time = datetime.now()
        steps = []
        errors = []

        try:
            # Validate workflow structure
            validation = self._validate_workflow()
            if not validation["valid"]:
                return TestResult(
                    test_id=test_id,
                    status=TestStatus.FAILED,
                    errors=validation["errors"]
                )

            # Execute each node
            for node in self.workflow.get("nodes", []):
                step_result = self._execute_node(node)
                steps.append(step_result)

                if step_result.get("status") == "error":
                    errors.append(step_result.get("error", "Unknown error"))

            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Determine overall status
            if errors:
                status = TestStatus.FAILED
            else:
                status = TestStatus.PASSED

            return TestResult(
                test_id=test_id,
                status=status,
                steps=steps,
                errors=errors,
                duration_ms=duration_ms
            )

        except Exception as e:
            return TestResult(
                test_id=test_id,
                status=TestStatus.ERROR,
                errors=[str(e)]
            )

    def _validate_workflow(self) -> Dict[str, Any]:
        """Validate workflow structure"""
        errors = []

        if not self.workflow.get("nodes"):
            errors.append("Workflow has no nodes")

        # Check for trigger
        triggers = [n for n in self.workflow.get("nodes", []) if n.get("type") == "trigger"]
        if not triggers:
            errors.append("Workflow must have at least one trigger")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _execute_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node (simulated)"""
        node_type = node.get("type")
        node_id = node.get("id")

        # Simulate execution
        result = {
            "nodeId": node_id,
            "type": node_type,
            "status": "success",
            "output": self.test_data,
            "timestamp": datetime.now().isoformat()
        }

        # Add type-specific simulation
        if node_type == "condition":
            result["conditionMet"] = True
        elif node_type == "action":
            result["actionCompleted"] = True
        elif node_type == "delay":
            result["delayMs"] = node.get("params", {}).get("delay", 1000)

        return result

    def debug_node(self, node_id: str) -> Dict[str, Any]:
        """Debug a specific node"""
        node = next((n for n in self.workflow.get("nodes", []) if n.get("id") == node_id), None)

        if not node:
            return {
                "success": False,
                "error": f"Node {node_id} not found"
            }

        result = self._execute_node(node)

        return {
            "success": True,
            "node": node,
            "execution": result,
            "context": self.test_data
        }


class TestCaseManager:
    """Manage test cases"""

    def __init__(self):
        self.test_cases: Dict[str, Dict[str, Any]] = {}

    def add_test_case(self, test_id: str, test_case: Dict[str, Any]) -> bool:
        """Add a test case"""
        self.test_cases[test_id] = {
            **test_case,
            "createdAt": datetime.now().isoformat()
        }
        return True

    def get_test_case(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get a test case"""
        return self.test_cases.get(test_id)

    def list_test_cases(self) -> List[Dict[str, Any]]:
        """List all test cases"""
        return list(self.test_cases.values())

    def run_test_case(self, test_id: str, workflow: Dict[str, Any]) -> TestResult:
        """Run a specific test case"""
        test_case = self.get_test_case(test_id)
        if not test_case:
            return TestResult(
                test_id=test_id,
                status=TestStatus.ERROR,
                errors=[f"Test case {test_id} not found"]
            )

        tester = WorkflowTester(workflow)
        tester.set_test_data(test_case.get("testData", {}))

        return tester.run_test(test_id)
