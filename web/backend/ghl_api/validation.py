"""
Workflow Validation - Epic 11: Story 11.1
Comprehensive validation before deployment
"""

from typing import Dict, List, Any

def validate_workflow_for_deployment(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate workflow is ready for GHL deployment
    Returns: {"valid": bool, "errors": [], "warnings": []}
    """
    errors = []
    warnings = []

    # Required fields
    if not workflow.get('name'):
        errors.append({'code': 'NO_NAME', 'message': 'Workflow must have a name'})

    if not workflow.get('nodes') or not isinstance(workflow['nodes'], list):
        errors.append({'code': 'NO_NODES', 'message': 'Workflow must have nodes'})
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    nodes = workflow['nodes']
    connections = workflow.get('connections', [])

    if len(nodes) == 0:
        errors.append({'code': 'EMPTY_WORKFLOW', 'message': 'Workflow has no nodes'})

    # Validate trigger
    triggers = [n for n in nodes if n.get('type') == 'trigger']
    if len(triggers) == 0:
        errors.append({'code': 'NO_TRIGGER', 'message': 'Workflow must have exactly 1 trigger'})
    elif len(triggers) > 1:
        errors.append({'code': 'MULTIPLE_TRIGGERS', 'message': f'Workflow has {len(triggers)} triggers, need exactly 1'})

    # Validate each node
    for idx, node in enumerate(nodes):
        if not node.get('id'):
            errors.append({'code': 'NODE_NO_ID', 'message': f'Node at index {idx} missing id'})
        if not node.get('type'):
            errors.append({'code': 'NODE_NO_TYPE', 'message': f'Node {node.get("id", idx)} missing type'})
        if not node.get('title'):
            errors.append({'code': 'NODE_NO_TITLE', 'message': f'Node {node.get("id", idx)} missing title'})

        # Validate position
        pos = node.get('position')
        if not pos or not isinstance(pos, dict):
            errors.append({'code': 'NODE_NO_POSITION', 'message': f'Node {node.get("id", idx)} missing position'})
        elif not isinstance(pos.get('x'), (int, float)) or not isinstance(pos.get('y'), (int, float)):
            errors.append({'code': 'NODE_INVALID_POSITION', 'message': f'Node {node.get("id", idx)} has invalid position'})

    # Validate connections
    node_ids = {n['id'] for n in nodes if 'id' in n}
    for idx, conn in enumerate(connections):
        if not conn.get('from'):
            errors.append({'code': 'CONN_NO_FROM', 'message': f'Connection {idx} missing from'})
        elif conn['from'] not in node_ids:
            errors.append({'code': 'CONN_FROM_MISSING', 'message': f'Connection from non-existent node: {conn["from"]}'})

        if not conn.get('to'):
            errors.append({'code': 'CONN_NO_TO', 'message': f'Connection {idx} missing to'})
        elif conn['to'] not in node_ids:
            errors.append({'code': 'CONN_TO_MISSING', 'message': f'Connection to non-existent node: {conn["to"]}'})

        if conn.get('from') == conn.get('to'):
            errors.append({'code': 'CONN_SELF_LOOP', 'message': 'Cannot connect node to itself'})

    # Check for orphaned nodes
    if connections:
        connected_nodes = set()
        for conn in connections:
            if 'from' in conn:
                connected_nodes.add(conn['from'])
            if 'to' in conn:
                connected_nodes.add(conn['to'])

        orphaned = node_ids - connected_nodes
        if orphaned and len(nodes) > 1:
            for node_id in orphaned:
                node = next((n for n in nodes if n.get('id') == node_id), None)
                warnings.append({
                    'code': 'ORPHANED_NODE',
                    'message': f'Node "{node.get("title", node_id)}" is not connected'
                })

    # Check for circular connections
    circular = detect_circular(nodes, connections)
    if circular:
        errors.append({'code': 'CIRCULAR_CONNECTION', 'message': f'Circular connection: {circular}'})

    # GHL-specific validations
    if len(nodes) > 100:
        warnings.append({'code': 'LARGE_WORKFLOW', 'message': 'Workflow has >100 nodes, may be slow in GHL'})

    # Check for end node
    end_nodes = [n for n in nodes if n.get('type') == 'end']
    if len(end_nodes) == 0:
        warnings.append({'code': 'NO_END_NODE', 'message': 'Workflow has no end node'})

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def detect_circular(nodes: List[Dict], connections: List[Dict]) -> str:
    """Detect circular connections using DFS"""
    graph = {n['id']: [] for n in nodes if 'id' in n}
    for conn in connections:
        if 'from' in conn and 'to' in conn and conn['from'] in graph:
            graph[conn['from']].append(conn['to'])

    visited = set()
    rec_stack = set()

    def dfs(node_id: str, path: List[str]) -> str:
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)

        for neighbor in graph.get(node_id, []):
            if neighbor not in visited:
                result = dfs(neighbor, path[:])
                if result:
                    return result
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle_path = path[cycle_start:]
                titles = []
                for nid in cycle_path:
                    node = next((n for n in nodes if n.get('id') == nid), None)
                    titles.append(node.get('title', nid) if node else nid)
                return ' → '.join(titles)

        rec_stack.remove(node_id)
        return ''

    for node_id in graph:
        if node_id not in visited:
            result = dfs(node_id, [])
            if result:
                return result

    return ''
