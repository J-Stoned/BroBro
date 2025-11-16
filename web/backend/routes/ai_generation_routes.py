"""
Enhancement 8: AI Workflow Generation API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.workflow_generator import get_workflow_generator

router = APIRouter()

class GenerateWorkflowRequest(BaseModel):
    description: str
    context: Optional[Dict] = None

class RefineWorkflowRequest(BaseModel):
    workflow: Dict
    refinement: str

@router.post("/api/ai/generate-workflow")
async def generate_workflow(request: GenerateWorkflowRequest):
    """
    Generate workflow from natural language description

    Example descriptions:
    - "Send 3 emails over 5 days to nurture new leads"
    - "Reminder sequence for upcoming appointments"
    - "Re-engage leads who haven't opened emails in 2 weeks"
    """
    try:
        generator = get_workflow_generator()
        result = generator.generate_workflow(
            description=request.description,
            context=request.context
        )

        return {
            "success": result['success'],
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@router.post("/api/ai/refine-workflow")
async def refine_workflow(request: RefineWorkflowRequest):
    """
    Refine existing workflow based on user feedback

    Example refinements:
    - "Add a 3rd email after 5 days"
    - "Include SMS follow-up if email not opened"
    - "Add personalization to all messages"
    """
    try:
        generator = get_workflow_generator()
        result = generator.refine_workflow(
            workflow=request.workflow,
            refinement=request.refinement
        )

        return {
            "success": result['success'],
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement error: {str(e)}")

@router.post("/api/ai/explain-workflow")
async def explain_workflow(workflow: Dict):
    """
    Generate human-readable explanation of workflow
    """
    try:
        # Build explanation
        nodes_count = len(workflow.get('nodes', []))
        actions_count = sum(1 for n in workflow.get('nodes', []) if n.get('type') == 'action')
        conditions_count = sum(1 for n in workflow.get('nodes', []) if n.get('type') == 'condition')

        explanation = f"This workflow has {nodes_count} steps:\n\n"

        for i, node in enumerate(workflow.get('nodes', []), 1):
            title = node.get('data', {}).get('title', 'Unknown')
            node_type = node.get('type', 'unknown')
            explanation += f"{i}. {title} ({node_type})\n"

        explanation += f"\nIt includes {actions_count} actions and {conditions_count} decision points."

        return {
            "success": True,
            "data": {
                "explanation": explanation,
                "stats": {
                    "total_nodes": nodes_count,
                    "actions": actions_count,
                    "conditions": conditions_count
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")
