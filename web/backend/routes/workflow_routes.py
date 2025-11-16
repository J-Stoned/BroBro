"""
Workflow Routes - Epic 12
Advanced workflow endpoints for conditions, variables, triggers, etc.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import logging
import html

from workflow_features.conditions import evaluate_condition_group
from workflow_features.variables import resolve_variables_in_text, Variable, VariableManager
from workflow_features.templates import TemplateManager
from workflow_features.testing import WorkflowTester, TestResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Initialize managers
template_manager = TemplateManager()


# Request/Response Models
class EvaluateConditionRequest(BaseModel):
    conditions: List[Dict[str, Any]] = Field(..., max_items=100, description="Maximum 100 conditions allowed")
    logicOperator: str = Field("and", pattern="^(and|or)$", description="Logic operator: 'and' or 'or'")
    context: Dict[str, Any] = Field(..., description="Context data for condition evaluation")

    @validator('conditions')
    def validate_conditions(cls, v):
        """Validate condition structure to prevent injection attacks"""
        if not v:
            raise ValueError("Conditions list cannot be empty")
        for i, condition in enumerate(v):
            if not isinstance(condition, dict):
                raise ValueError(f"Condition {i} must be a dictionary")
            # Ensure condition has required fields
            if not all(key in condition for key in ['field', 'operator', 'value']):
                raise ValueError(f"Condition {i} must have 'field', 'operator', and 'value' keys")
        return v

    @validator('context')
    def validate_context(cls, v):
        """Validate context data"""
        if len(str(v)) > 1000000:  # 1MB limit
            raise ValueError("Context data too large (max 1MB)")
        return v


class EvaluateConditionResponse(BaseModel):
    success: bool
    result: Optional[bool] = None
    message: str = Field(..., max_length=500)
    error: Optional[str] = Field(None, max_length=500)


@router.post("/evaluate-condition", response_model=EvaluateConditionResponse)
async def evaluate_condition_endpoint(request: EvaluateConditionRequest):
    """
    Test condition evaluation with sample data

    Example request:
    {
        "conditions": [{
            "field": "contact.email",
            "operator": "contains",
            "value": "@gmail.com"
        }],
        "logicOperator": "and",
        "context": {
            "contact": {"email": "user@gmail.com"}
        }
    }
    """
    try:
        result = evaluate_condition_group(
            request.conditions,
            request.logicOperator,
            request.context
        )

        return EvaluateConditionResponse(
            success=True,
            result=result,
            message=f"Condition {'passed' if result else 'failed'}"
        )

    except Exception as e:
        logger.error(f"Condition evaluation error: {e}")
        return EvaluateConditionResponse(
            success=False,
            message="Condition evaluation failed",
            error=str(e)
        )


# Variable Resolution Models
class ResolveVariablesRequest(BaseModel):
    text: str
    context: Dict[str, Any]


class ResolveVariablesResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    message: str
    error: Optional[str] = None


@router.post("/resolve-variables", response_model=ResolveVariablesResponse)
async def resolve_variables_endpoint(request: ResolveVariablesRequest):
    """
    Resolve variable references in text

    Example request:
    {
        "text": "Hello {{customerName}}, your order is {{orderStatus}}",
        "context": {
            "customerName": "John",
            "orderStatus": "shipped"
        }
    }

    Returns: "Hello John, your order is shipped"
    """
    try:
        result = resolve_variables_in_text(request.text, request.context)

        return ResolveVariablesResponse(
            success=True,
            result=result,
            message="Variables resolved successfully"
        )

    except Exception as e:
        logger.error(f"Variable resolution error: {e}")
        return ResolveVariablesResponse(
            success=False,
            message="Variable resolution failed",
            error=str(e)
        )


# Variable Validation Models
class ValidateVariableRequest(BaseModel):
    name: str
    type: str
    value: Any


class ValidateVariableResponse(BaseModel):
    success: bool
    valid: bool
    message: str
    error: Optional[str] = None


@router.post("/validate-variable", response_model=ValidateVariableResponse)
async def validate_variable_endpoint(request: ValidateVariableRequest):
    """
    Validate a variable value matches its type

    Example request:
    {
        "name": "age",
        "type": "number",
        "value": 25
    }
    """
    try:
        variable = Variable(
            name=request.name,
            var_type=request.type,
            default_value=None
        )

        is_valid = variable.validate_value(request.value)

        return ValidateVariableResponse(
            success=True,
            valid=is_valid,
            message=f"Value is {'valid' if is_valid else 'invalid'} for type {request.type}"
        )

    except Exception as e:
        logger.error(f"Variable validation error: {e}")
        return ValidateVariableResponse(
            success=False,
            valid=False,
            message="Variable validation failed",
            error=str(e)
        )


# Template Endpoints
@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
):
    """List workflow templates with optional filtering"""
    try:
        templates = template_manager.list_templates(
            category=category,
            difficulty=difficulty,
            search=search
        )

        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }

    except Exception as e:
        logger.error(f"Template list error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template"""
    try:
        template = template_manager.get_template(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "success": True,
            "template": template.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template get error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Testing Endpoints
class TestWorkflowRequest(BaseModel):
    workflow: Dict[str, Any]
    testData: Dict[str, Any]


@router.post("/test")
async def test_workflow(request: TestWorkflowRequest):
    """Test workflow execution with sample data"""
    try:
        tester = WorkflowTester(request.workflow)
        tester.set_test_data(request.testData)

        result = tester.run_test()

        return {
            "success": True,
            "result": result.to_dict()
        }

    except Exception as e:
        logger.error(f"Workflow test error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/debug-node")
async def debug_node(request: Dict[str, Any]):
    """Debug a specific node"""
    try:
        workflow = request.get("workflow", {})
        node_id = request.get("nodeId")
        test_data = request.get("testData", {})

        tester = WorkflowTester(workflow)
        tester.set_test_data(test_data)

        result = tester.debug_node(node_id)

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error(f"Node debug error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Smart Suggestions Models - Enhancement 2
class WorkflowContext(BaseModel):
    last_node: Optional[Dict[str, Any]] = None
    all_nodes: List[Dict[str, Any]] = []
    workflow_type: Optional[str] = None
    workflow_goal: Optional[str] = None


class Suggestion(BaseModel):
    command_id: str
    title: str
    description: str
    category: str
    reason: str
    relevance_score: float
    icon: str


@router.post("/suggest-next")
async def suggest_next_commands(context: WorkflowContext):
    """
    Enhancement 2: Smart Command Suggestions

    Suggests next workflow commands based on current context using:
    - Semantic search on ghl-knowledge-base collection
    - Pattern-based suggestion rules
    - Context analysis (last node type, workflow pattern)

    Returns top 5 contextually relevant commands with reasoning.

    Example request:
    {
        "last_node": {
            "type": "action",
            "data": {"action_type": "send_email"}
        },
        "all_nodes": [...],
        "workflow_type": "marketing",
        "workflow_goal": "Lead nurture sequence"
    }
    """
    try:
        import chromadb
        import os

        # Initialize ChromaDB
        client = chromadb.HttpClient(
            host=os.getenv('CHROMA_HOST', 'localhost'),
            port=int(os.getenv('CHROMA_PORT', '8001'))
        )

        try:
            kb_collection = client.get_collection("ghl-knowledge-base")
        except Exception as e:
            logger.warning(f"Could not access ghl-knowledge-base: {e}")
            return {
                "success": True,
                "data": _get_default_suggestions(context)
            }

        # Analyze context and build search query
        search_query, boost_categories = _analyze_workflow_context(context)

        # Search for relevant commands
        results = kb_collection.query(
            query_texts=[search_query],
            n_results=20  # Get more, then filter
        )

        if not results or not results['ids'][0]:
            return {
                "success": True,
                "data": _get_default_suggestions(context)
            }

        # Score and rank suggestions
        suggestions = []
        for i in range(len(results['ids'][0])):
            cmd_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]

            # Calculate relevance score
            base_score = (1 - distance) * 100

            # Apply context-based boosts
            boost = 0
            if metadata.get('category') in boost_categories:
                boost += 20

            # Apply pattern-based rules
            pattern_boost, reason = _apply_suggestion_rules(
                last_node=context.last_node,
                candidate_cmd=metadata,
                all_nodes=context.all_nodes
            )
            boost += pattern_boost

            final_score = min(base_score + boost, 100)  # Cap at 100

            suggestions.append({
                "command_id": cmd_id,
                "title": metadata.get('title', 'Unknown'),
                "description": metadata.get('purpose', '')[:100],
                "category": metadata.get('category', 'general'),
                "reason": reason or f"Related to {context.last_node.get('type') if context.last_node else 'workflow'}",
                "relevance_score": round(final_score, 1),
                "icon": _get_category_icon(metadata.get('category', 'general'))
            })

        # Sort by relevance and take top 5
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        top_suggestions = suggestions[:5]

        return {
            "success": True,
            "data": {
                "suggestions": top_suggestions,
                "context_summary": f"Based on your {context.last_node.get('type', 'workflow') if context.last_node else 'workflow'}"
            }
        }

    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "data": _get_default_suggestions(context)
        }


def _analyze_workflow_context(context: WorkflowContext) -> tuple:
    """
    Analyze workflow context to build search query and boost categories

    Returns: (search_query, boost_categories)
    """
    if not context.last_node:
        # No nodes yet - suggest common triggers
        return "trigger form submission contact created", ["trigger"]

    last_type = context.last_node.get('type', '')
    last_action = context.last_node.get('data', {}).get('action_type', '')

    # Build search query based on last node
    if last_type == 'action':
        if 'email' in last_action.lower():
            query = "wait delay check email opened sms follow-up"
            boost = ["delay", "condition", "lead"]
        elif 'sms' in last_action.lower():
            query = "wait delay check sms replied email follow-up"
            boost = ["delay", "condition", "lead"]
        elif 'tag' in last_action.lower():
            query = "condition check tag workflow automation"
            boost = ["condition", "workflow"]
        else:
            query = "next step follow-up automation"
            boost = ["delay", "condition"]

    elif last_type == 'delay':
        query = "send email sms follow-up check condition"
        boost = ["lead", "condition"]

    elif last_type == 'condition':
        query = "send email sms add tag create task"
        boost = ["lead", "tag", "task"]

    elif last_type == 'trigger':
        query = "send email sms add tag create contact"
        boost = ["lead", "contact", "tag"]

    else:
        query = "automation workflow next step"
        boost = ["general"]

    return query, boost


def _apply_suggestion_rules(last_node: Optional[Dict], candidate_cmd: Dict, all_nodes: List[Dict]) -> tuple:
    """
    Apply pattern-based rules to boost/penalize suggestions

    Returns: (boost_amount, reason)
    """
    if not last_node:
        return 0, "Common starting action"

    last_type = last_node.get('type', '')
    last_action = last_node.get('data', {}).get('action_type', '').lower()
    candidate_title = candidate_cmd.get('title', '').lower()

    # Rule 1: After email, suggest wait/check/sms
    if 'email' in last_action:
        if 'wait' in candidate_title or 'delay' in candidate_title:
            return 30, "Common: Wait after sending email"
        if 'sms' in candidate_title:
            return 25, "Alternative channel: Follow up via SMS"
        if 'open' in candidate_title or 'check' in candidate_title:
            return 20, "Track engagement: Check if email opened"

    # Rule 2: After wait, suggest action
    if last_type == 'delay':
        if 'send' in candidate_title or 'email' in candidate_title or 'sms' in candidate_title:
            return 30, "Next step: Send follow-up message"
        if 'check' in candidate_title or 'condition' in candidate_title:
            return 25, "Check status before continuing"

    # Rule 3: After SMS, suggest wait/check
    if 'sms' in last_action:
        if 'wait' in candidate_title:
            return 25, "Give time for response"
        if 'check' in candidate_title or 'replied' in candidate_title:
            return 30, "Check if contact responded"

    # Rule 4: After condition, suggest actions for both paths
    if last_type == 'condition':
        if 'tag' in candidate_title:
            return 20, "Organize contacts with tags"
        if 'send' in candidate_title or 'email' in candidate_title:
            return 25, "Take action based on condition"

    # Rule 5: Avoid duplicate similar actions
    used_commands = [n.get('data', {}).get('command_id', '') for n in all_nodes]
    if candidate_cmd.get('command_id') in used_commands:
        return -20, "Already used in workflow"

    return 0, "Contextually relevant"


def _get_default_suggestions(context: WorkflowContext) -> Dict:
    """Return default suggestions when no specific context"""
    return {
        "suggestions": [
            {
                "command_id": "default-1",
                "title": "Send Email",
                "description": "Send an email to contact",
                "category": "lead",
                "reason": "Common starting action",
                "relevance_score": 90.0,
                "icon": "[MAIL]"
            },
            {
                "command_id": "default-2",
                "title": "Send SMS",
                "description": "Send SMS message to contact",
                "category": "lead",
                "reason": "Quick communication",
                "relevance_score": 85.0,
                "icon": "[MSG]"
            },
            {
                "command_id": "default-3",
                "title": "Add Tag",
                "description": "Add tag to contact",
                "category": "tag",
                "reason": "Organize and segment",
                "relevance_score": 80.0,
                "icon": "[TAG]"
            },
            {
                "command_id": "default-4",
                "title": "Wait",
                "description": "Add time delay",
                "category": "delay",
                "reason": "Pace your automation",
                "relevance_score": 75.0,
                "icon": "[TIME]"
            },
            {
                "command_id": "default-5",
                "title": "Create Task",
                "description": "Create task for team",
                "category": "task",
                "reason": "Assign follow-up",
                "relevance_score": 70.0,
                "icon": "[TASK]"
            }
        ],
        "context_summary": "Start your workflow with these common actions"
    }


def _get_category_icon(category: str) -> str:
    """Get text icon for category (Windows console safe)"""
    icons = {
        "lead": "[MAIL]",
        "contact": "[USER]",
        "tag": "[TAG]",
        "delay": "[TIME]",
        "condition": "[BRANCH]",
        "task": "[TASK]",
        "opportunity": "[MONEY]",
        "calendar": "[CAL]",
        "workflow": "[FLOW]",
        "trigger": "[BOLT]",
        "general": "[DOC]"
    }
    return icons.get(category.lower(), "[DOC]")


# Enhancement 4: Workflow Validation
from utils.workflow_validator import WorkflowValidator

# Initialize validator
workflow_validator = WorkflowValidator()


class WorkflowValidationRequest(BaseModel):
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


@router.post("/validate")
async def validate_workflow(request: WorkflowValidationRequest):
    """
    Enhancement 4: Workflow Validator & Best Practices Checker

    Validates workflows against 20+ best practice rules including:
    - Error handling
    - Follow-up actions
    - Timing issues
    - Personalization
    - Email/SMS best practices
    - And more...

    Returns:
    - is_valid: bool (no errors)
    - score: int (0-100)
    - issues: list with severity, description, fix suggestions
    - stats: error/warning/suggestion counts
    - best_practices_met: percentage

    Example:
    {
        "nodes": [...],
        "connections": [...],
        "metadata": {"goal": "30% open rate"}
    }
    """
    try:
        workflow = {
            'nodes': request.nodes,
            'connections': request.connections,
            'metadata': request.metadata
        }

        validation_result = workflow_validator.validate(workflow)

        return {
            "success": True,
            "data": validation_result
        }

    except Exception as e:
        logger.error(f"Validation error: {e}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e),
            "data": {
                'is_valid': False,
                'score': 0,
                'issues': [],
                'stats': {'errors': 0, 'warnings': 0, 'suggestions': 0},
                'best_practices_met': 0
            }
        }
