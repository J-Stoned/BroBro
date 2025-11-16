"""
GHL API Client - Epic 11: Story 11.1
Wrapper for GoHighLevel API v2
"""

import httpx
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class GHLClient:
    """GoHighLevel API Client"""

    BASE_URL = "https://services.leadconnectorhq.com"

    def __init__(self, api_key: str, location_id: str):
        self.api_key = api_key
        self.location_id = location_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test API key and connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/locations/{self.location_id}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'location': data.get('location', {}),
                        'message': 'API key valid'
                    }
                elif response.status_code == 401:
                    return {
                        'success': False,
                        'error': 'Invalid API key',
                        'message': 'API key is invalid or expired'
                    }
                elif response.status_code == 404:
                    return {
                        'success': False,
                        'error': 'Location not found',
                        'message': f'Location ID {self.location_id} not found'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except httpx.TimeoutException:
            return {
                'success': False,
                'error': 'Connection timeout',
                'message': 'Failed to connect to GHL API (timeout)'
            }
        except Exception as e:
            logger.error(f"GHL API test failed: {e}")
            return {
                'success': False,
                'error': 'Connection error',
                'message': str(e)
            }

    async def create_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy workflow to GHL"""
        try:
            # Transform workflow to GHL format
            ghl_workflow = self._transform_to_ghl_format(workflow)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/workflows",
                    headers=self.headers,
                    json=ghl_workflow
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        'success': True,
                        'workflow_id': data.get('id'),
                        'workflow': data,
                        'message': 'Workflow deployed successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            logger.error(f"Workflow deployment failed: {e}")
            return {
                'success': False,
                'error': 'Deployment error',
                'message': str(e)
            }

    async def get_workflows(self, limit: int = 100) -> Dict[str, Any]:
        """Get workflows from GHL"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/workflows",
                    headers=self.headers,
                    params={'locationId': self.location_id, 'limit': limit}
                )

                if response.status_code == 200:
                    data = response.json()
                    workflows = data.get('workflows', [])
                    return {
                        'success': True,
                        'workflows': workflows,
                        'count': len(workflows)
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            logger.error(f"Get workflows failed: {e}")
            return {
                'success': False,
                'error': 'Fetch error',
                'message': str(e)
            }

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get single workflow from GHL"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/workflows/{workflow_id}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return {
                        'success': True,
                        'workflow': response.json()
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            return {
                'success': False,
                'error': 'Fetch error',
                'message': str(e)
            }

    async def update_workflow(self, workflow_id: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing workflow in GHL"""
        try:
            ghl_workflow = self._transform_to_ghl_format(workflow)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.BASE_URL}/workflows/{workflow_id}",
                    headers=self.headers,
                    json=ghl_workflow
                )

                if response.status_code == 200:
                    return {
                        'success': True,
                        'workflow': response.json(),
                        'message': 'Workflow updated successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            return {
                'success': False,
                'error': 'Update error',
                'message': str(e)
            }

    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete workflow from GHL"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    f"{self.BASE_URL}/workflows/{workflow_id}",
                    headers=self.headers
                )

                if response.status_code in [200, 204]:
                    return {
                        'success': True,
                        'message': 'Workflow deleted successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            return {
                'success': False,
                'error': 'Delete error',
                'message': str(e)
            }

    async def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get workflow execution history"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/workflows/{workflow_id}/executions",
                    headers=self.headers,
                    params={'limit': limit}
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'executions': data.get('executions', []),
                        'count': len(data.get('executions', []))
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'message': response.text
                    }
        except Exception as e:
            return {
                'success': False,
                'error': 'Fetch error',
                'message': str(e)
            }

    def _transform_to_ghl_format(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Transform our workflow format to GHL API format"""
        # This is a simplified transformation
        # Real implementation would map node types, params, etc.
        return {
            'name': workflow.get('name', 'Untitled'),
            'description': workflow.get('description', ''),
            'locationId': self.location_id,
            'nodes': self._transform_nodes(workflow.get('nodes', [])),
            'connections': workflow.get('connections', []),
            'version': workflow.get('version', '1.0')
        }

    def _transform_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """Transform nodes to GHL format"""
        transformed = []
        for node in nodes:
            transformed.append({
                'id': node.get('id'),
                'type': node.get('type'),
                'name': node.get('title'),
                'description': node.get('description', ''),
                'position': node.get('position', {}),
                'config': node.get('params', {})
            })
        return transformed
