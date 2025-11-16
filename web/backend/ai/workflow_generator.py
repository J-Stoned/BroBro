"""
Enhancement 8: AI-powered workflow generator using natural language
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import anthropic

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import elite Claude API manager
try:
    from src.services.claude import ClaudeAPIManager
    ELITE_API_AVAILABLE = True
except ImportError:
    ELITE_API_AVAILABLE = False

class WorkflowGenerator:
    """
    Generate workflows from natural language descriptions
    """

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        if api_key:
            # Use elite API manager if available
            if ELITE_API_AVAILABLE:
                self.api_manager = ClaudeAPIManager(api_key)
                self.use_elite = True
            else:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.use_elite = False
        else:
            self.client = None
            self.use_elite = False
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load workflow generation system prompt"""
        return """You are an expert workflow automation designer for GoHighLevel (GHL).
Your job is to convert natural language descriptions into complete, production-ready workflows.

You have access to these GHL action types:
- send_email: Send email to contact
- send_sms: Send SMS message
- add_tag: Add tag to contact
- remove_tag: Remove tag from contact
- create_task: Create task for team
- create_opportunity: Create sales opportunity
- wait: Add time delay
- condition: Branch based on criteria
- webhook: Call external API

WORKFLOW STRUCTURE:
A workflow is JSON with:
{
  "nodes": [
    {
      "id": "unique-id",
      "type": "trigger|action|delay|condition",
      "position": {"x": number, "y": number},
      "data": {
        "title": "Human readable name",
        "action_type": "send_email|send_sms|etc",
        ... action-specific fields
      }
    }
  ],
  "connections": [
    {
      "source": "node-id",
      "target": "node-id",
      "label": "optional (Yes/No for conditions)"
    }
  ],
  "metadata": {
    "name": "Workflow Name",
    "description": "What this workflow does"
  }
}

BEST PRACTICES:
1. Always start with a trigger node
2. Add delays between email sends (2-3 days minimum)
3. Use conditions to personalize paths based on engagement
4. Add tags to track progress
5. Include error handling for critical actions
6. Personalize messages with {{contact.first_name}}
7. Position nodes vertically with 200px spacing
8. Use clear, descriptive node titles

TIMING GUIDELINES:
- Email follow-ups: 2-3 days apart
- SMS follow-ups: 1-2 days apart
- Initial response: Same day or 1 hour
- Nurture sequences: 5-7 days total
- Re-engagement: 7-14 days after inactivity

When generating workflows:
1. Parse the user's intent carefully
2. Create appropriate trigger (form submission, tag added, etc.)
3. Build logical sequence of actions
4. Add proper delays
5. Include conditional branches when appropriate
6. Add tracking tags
7. Return ONLY valid JSON, no explanations

If the description is ambiguous, respond with:
{
  "clarification_needed": true,
  "questions": ["What should trigger this workflow?", "How many emails?"]
}

Otherwise, respond with the complete workflow JSON."""

    def generate_workflow(
        self,
        description: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate workflow from natural language description

        Args:
            description: User's description of desired workflow
            context: Optional context (business type, existing workflows, etc.)

        Returns:
            Either:
            - Complete workflow JSON
            - Clarification questions if description is ambiguous
        """

        # Check if API key is available
        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic API key not configured',
                'details': 'Set ANTHROPIC_API_KEY environment variable'
            }

        try:
            # Build user message
            user_message = f"""Generate a GHL workflow for the following:

DESCRIPTION: {description}"""

            if context:
                user_message += f"\n\nCONTEXT: {json.dumps(context, indent=2)}"

            # Call Claude API
            if self.use_elite:
                # Use elite API manager
                response = self.api_manager.send_message(
                    messages=[{"role": "user", "content": user_message}],
                    profile="workflow-builder",  # Specialized for workflow generation
                    system_prompt=self.system_prompt,
                    user_id="workflow_generator",
                    endpoint="/api/workflow/generate"
                )

                if not response.success:
                    raise Exception(f"Elite API failed: {response.error}")

                workflow_json = response.content
            else:
                # Standard client
                message = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=24000,
                    system=self.system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ]
                )
                workflow_json = message.content[0].text

            # Parse workflow_json (moved outside to work with both paths)
            # Extract response
            response_text = workflow_json.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            workflow_data = json.loads(response_text)

            # Check if clarification needed
            if workflow_data.get('clarification_needed'):
                return {
                    'success': True,
                    'clarification_needed': True,
                    'questions': workflow_data.get('questions', [])
                }

            # Validate workflow structure
            validation_result = self._validate_workflow(workflow_data)

            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Generated workflow is invalid',
                    'details': validation_result['errors']
                }

            return {
                'success': True,
                'workflow': workflow_data,
                'clarification_needed': False
            }

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': 'Failed to parse AI response',
                'details': str(e),
                'raw_response': response_text[:500] if 'response_text' in locals() else 'N/A'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Workflow generation failed',
                'details': str(e)
            }

    def _validate_workflow(self, workflow: Dict) -> Dict:
        """Validate generated workflow structure"""
        errors = []

        # Check required fields
        if 'nodes' not in workflow:
            errors.append('Missing nodes array')
        if 'connections' not in workflow:
            errors.append('Missing connections array')

        # Validate nodes
        if 'nodes' in workflow:
            for i, node in enumerate(workflow['nodes']):
                if 'id' not in node:
                    errors.append(f'Node {i} missing id')
                if 'type' not in node:
                    errors.append(f'Node {i} missing type')
                if 'data' not in node:
                    errors.append(f'Node {i} missing data')

        # Validate connections
        if 'connections' in workflow and 'nodes' in workflow:
            node_ids = {node['id'] for node in workflow['nodes']}
            for i, conn in enumerate(workflow['connections']):
                if 'source' not in conn or conn['source'] not in node_ids:
                    errors.append(f'Connection {i} has invalid source')
                if 'target' not in conn or conn['target'] not in node_ids:
                    errors.append(f'Connection {i} has invalid target')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def refine_workflow(
        self,
        workflow: Dict,
        refinement: str
    ) -> Dict:
        """
        Refine existing workflow based on user feedback

        Args:
            workflow: Current workflow structure
            refinement: User's refinement request

        Returns:
            Updated workflow
        """

        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic API key not configured'
            }

        try:
            user_message = f"""Here is an existing workflow:

{json.dumps(workflow, indent=2)}

The user wants to refine it as follows:
{refinement}

Return the updated workflow JSON. Maintain all existing nodes unless the refinement specifically asks to change them."""

            if self.use_elite:
                # Use elite API manager
                response = self.api_manager.send_message(
                    messages=[{"role": "user", "content": user_message}],
                    profile="workflow-builder",  # Specialized for workflow refinement
                    system_prompt=self.system_prompt,
                    user_id="workflow_generator",
                    endpoint="/api/workflow/refine"
                )

                if not response.success:
                    raise Exception(f"Elite API failed: {response.error}")

                refined_json = response.content
            else:
                # Standard client
                message = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=24000,
                    system=self.system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ]
                )
                refined_json = message.content[0].text

            # Extract response (works with both paths)
            response_text = refined_json.strip()

            # Parse JSON
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            refined_workflow = json.loads(response_text)

            return {
                'success': True,
                'workflow': refined_workflow
            }

        except Exception as e:
            return {
                'success': False,
                'error': 'Workflow refinement failed',
                'details': str(e)
            }

# Singleton instance - Initialize lazily on first use
_workflow_generator = None

def get_workflow_generator():
    """Lazy-load the workflow generator to avoid hanging on import"""
    global _workflow_generator
    if _workflow_generator is None:
        _workflow_generator = WorkflowGenerator()
    return _workflow_generator

# For backward compatibility, keep this as a lazy property
workflow_generator = None  # Will be set via get_workflow_generator()
