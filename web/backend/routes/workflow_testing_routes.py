"""
Enhancement 5: Workflow Testing Routes
API endpoints for testing workflows with mock contact data
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
from pathlib import Path
from utils.workflow_simulator import WorkflowSimulator

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize simulator
workflow_simulator = WorkflowSimulator()
MOCK_CONTACTS_FILE = Path('web/backend/data/mock_contacts.json')


class TestWorkflowRequest(BaseModel):
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    mock_contact_id: str = 'mock-1'
    speed_multiplier: int = 1000


@router.get('/api/workflows/mock-contacts')
async def get_mock_contacts():
    """
    Get available mock contact personas for testing

    Returns 5 realistic contact personas with different engagement levels:
    - Engaged Lead (high engagement)
    - Moderate Lead (medium engagement)
    - Cold Lead (low engagement)
    - Existing Customer (high engagement, already purchased)
    - Small Business Owner (medium engagement, budget-conscious)
    """
    try:
        if not MOCK_CONTACTS_FILE.exists():
            logger.error(f'Mock contacts file not found: {MOCK_CONTACTS_FILE}')
            return {
                'success': False,
                'error': 'Mock contacts file not found'
            }

        with open(MOCK_CONTACTS_FILE, 'r', encoding='utf-8') as f:
            contacts = json.load(f)

        logger.info(f'Loaded {len(contacts)} mock contacts')

        return {
            'success': True,
            'data': {
                'contacts': contacts
            }
        }
    except Exception as e:
        logger.error(f'Error loading mock contacts: {e}')
        return {
            'success': False,
            'error': str(e)
        }


@router.post('/api/workflows/test')
async def test_workflow(request: TestWorkflowRequest):
    """
    Enhancement 5: Test workflow with mock contact data

    Simulates step-by-step execution with:
    - Variable substitution ({{contact.name}}, etc.)
    - Conditional logic evaluation
    - Fast-forwarded delays (1000x speed)
    - Contact state tracking

    Returns detailed execution log with results for each node
    """
    try:
        # Load mock contacts
        if not MOCK_CONTACTS_FILE.exists():
            return {
                'success': False,
                'error': 'Mock contacts file not found'
            }

        with open(MOCK_CONTACTS_FILE, 'r', encoding='utf-8') as f:
            mock_contacts = json.load(f)

        # Find requested contact
        mock_contact = next(
            (c for c in mock_contacts if c['id'] == request.mock_contact_id),
            None
        )

        if not mock_contact:
            return {
                'success': False,
                'error': f'Mock contact not found: {request.mock_contact_id}'
            }

        # Build workflow
        workflow = {
            'nodes': request.nodes,
            'connections': request.connections,
            'metadata': request.metadata
        }

        logger.info(f'Testing workflow with contact: {mock_contact["name"]} ({mock_contact["persona"]})')
        logger.info(f'Workflow has {len(request.nodes)} nodes, {len(request.connections)} connections')

        # Simulate execution
        result = workflow_simulator.simulate(
            workflow,
            mock_contact,
            request.speed_multiplier
        )

        logger.info(f'Test complete: {result["nodes_executed"]} nodes executed')

        return {
            'success': True,
            'data': result
        }

    except Exception as e:
        logger.error(f'Test execution error: {e}', exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'data': {
                'execution_log': [],
                'nodes_executed': 0,
                'total_time_simulated': '0 minutes',
                'execution_time_actual': '0s'
            }
        }
