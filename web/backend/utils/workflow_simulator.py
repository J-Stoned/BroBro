"""
Workflow Simulator - Enhancement 5
Simulates workflow execution with mock contact data for testing
"""

import re
import time
from typing import Dict, List, Optional
from datetime import datetime


class WorkflowSimulator:
    """
    Simulates workflow execution step-by-step with mock contact data
    """

    def __init__(self):
        self.execution_log = []

    def simulate(
        self,
        workflow: Dict,
        mock_contact: Dict,
        speed_multiplier: int = 1000  # 1000x = 1 day → 86 seconds
    ) -> Dict:
        """
        Simulate workflow execution step-by-step

        Args:
            workflow: Workflow definition with nodes and connections
            mock_contact: Mock contact persona data
            speed_multiplier: Time acceleration (1000 = 1 day → 86s)

        Returns:
            {
                'success': bool,
                'execution_log': [...],
                'total_time_simulated': str,
                'final_state': dict
            }
        """
        self.execution_log = []
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', [])

        if not nodes:
            return {
                'success': False,
                'error': 'Workflow has no nodes'
            }

        # Start with trigger node (first node)
        current_node = nodes[0]
        contact_state = mock_contact.copy()
        execution_start = time.time()

        # Execute workflow
        visited_nodes = set()
        max_iterations = 50  # Prevent infinite loops
        iteration = 0

        while current_node and iteration < max_iterations:
            if current_node['id'] in visited_nodes:
                # Potential loop - check if we should continue
                if iteration > 20:
                    self._log_step(
                        current_node,
                        'failed',
                        'Infinite loop detected - stopping execution',
                        {}
                    )
                    break

            visited_nodes.add(current_node['id'])
            iteration += 1

            # Execute node
            result = self._execute_node(
                current_node,
                contact_state,
                speed_multiplier
            )

            # Log execution
            self._log_step(
                current_node,
                result['status'],
                result['message'],
                result['details']
            )

            # Update contact state if needed
            if 'state_changes' in result:
                contact_state.update(result['state_changes'])

            # Find next node
            next_node_id = self._get_next_node(
                current_node,
                connections,
                result
            )

            if not next_node_id:
                break

            current_node = next((n for n in nodes if n['id'] == next_node_id), None)

        execution_time = time.time() - execution_start
        total_simulated = self._calculate_total_time(workflow)

        return {
            'success': True,
            'execution_log': self.execution_log,
            'total_time_simulated': total_simulated,
            'execution_time_actual': f"{execution_time:.2f}s",
            'final_state': contact_state,
            'nodes_executed': len(visited_nodes)
        }

    def _execute_node(
        self,
        node: Dict,
        contact: Dict,
        speed_multiplier: int
    ) -> Dict:
        """Execute a single node and return result"""
        node_type = node.get('type', 'unknown')

        if node_type == 'trigger':
            return self._execute_trigger(node, contact)
        elif node_type == 'action':
            return self._execute_action(node, contact)
        elif node_type == 'delay':
            return self._execute_delay(node, contact, speed_multiplier)
        elif node_type == 'condition':
            return self._execute_condition(node, contact)
        else:
            return {
                'status': 'skipped',
                'message': f'Unknown node type: {node_type}',
                'details': {}
            }

    def _execute_trigger(self, node: Dict, contact: Dict) -> Dict:
        """Execute trigger node"""
        trigger_type = node.get('data', {}).get('trigger_type', 'unknown')

        return {
            'status': 'success',
            'message': f'Workflow triggered: {trigger_type}',
            'details': {
                'trigger_type': trigger_type,
                'contact': contact.get('name', 'Unknown')
            }
        }

    def _execute_action(self, node: Dict, contact: Dict) -> Dict:
        """Execute action node (email, SMS, tag, task, etc.)"""
        node_data = node.get('data', {})
        action_type = str(node_data.get('action_type', 'unknown')).lower()
        title = node_data.get('title', 'Action')

        # Substitute variables in message
        message = node_data.get('message', '')
        subject = node_data.get('subject', '')

        substituted_message = self._substitute_variables(message, contact)
        substituted_subject = self._substitute_variables(subject, contact)

        # Simulate action execution based on type
        if 'email' in action_type or 'send_email' in action_type:
            return {
                'status': 'success',
                'message': f'Email sent to {contact.get("email", "unknown")}',
                'details': {
                    'to': contact.get('email'),
                    'subject': substituted_subject or 'No Subject',
                    'message_preview': substituted_message[:100] + '...' if len(substituted_message) > 100 else substituted_message,
                    'action_type': 'email'
                },
                'state_changes': {
                    'last_email_sent': datetime.now().isoformat(),
                    'emails_received': contact.get('emails_received', 0) + 1
                }
            }

        elif 'sms' in action_type or 'send_sms' in action_type:
            return {
                'status': 'success',
                'message': f'SMS sent to {contact.get("phone", "unknown")}',
                'details': {
                    'to': contact.get('phone'),
                    'message': substituted_message,
                    'action_type': 'sms'
                },
                'state_changes': {
                    'last_sms_sent': datetime.now().isoformat(),
                    'sms_received': contact.get('sms_received', 0) + 1
                }
            }

        elif 'tag' in action_type or 'add_tag' in action_type:
            tag_name = node_data.get('tag_name') or node_data.get('tag', 'unknown-tag')
            current_tags = contact.get('tags', [])

            if 'remove' in action_type:
                new_tags = [t for t in current_tags if t != tag_name]
                return {
                    'status': 'success',
                    'message': f'Tag removed: {tag_name}',
                    'details': {
                        'tag': tag_name,
                        'action_type': 'remove_tag'
                    },
                    'state_changes': {
                        'tags': new_tags
                    }
                }
            else:
                new_tags = current_tags + [tag_name] if tag_name not in current_tags else current_tags
                return {
                    'status': 'success',
                    'message': f'Tag added: {tag_name}',
                    'details': {
                        'tag': tag_name,
                        'action_type': 'add_tag'
                    },
                    'state_changes': {
                        'tags': new_tags
                    }
                }

        elif 'task' in action_type:
            task_title = node_data.get('task_title', 'New Task')
            return {
                'status': 'success',
                'message': f'Task created: {task_title}',
                'details': {
                    'task_title': task_title,
                    'assigned_to': node_data.get('assigned_to', 'Unassigned'),
                    'action_type': 'create_task'
                }
            }

        else:
            return {
                'status': 'success',
                'message': f'Action executed: {title}',
                'details': {
                    'action_type': action_type
                }
            }

    def _execute_delay(
        self,
        node: Dict,
        contact: Dict,
        speed_multiplier: int
    ) -> Dict:
        """Execute delay node (fast-forwarded for testing)"""
        node_data = node.get('data', {})
        duration = node_data.get('delay_duration', 60)  # Default: minutes
        unit = node_data.get('unit', 'minutes')

        # Convert to minutes
        if unit == 'hours':
            duration_minutes = duration * 60
        elif unit == 'days':
            duration_minutes = duration * 1440
        elif unit == 'minutes':
            duration_minutes = duration
        else:
            # If delay_duration is already in minutes
            duration_minutes = duration

        # Fast-forward (1000x = 1 day → 86 seconds)
        actual_wait = (duration_minutes * 60) / speed_multiplier
        time.sleep(min(actual_wait, 1))  # Cap at 1 second for UX

        return {
            'status': 'success',
            'message': f'Waited {duration_minutes} minutes (simulated)',
            'details': {
                'duration': duration_minutes,
                'unit': 'minutes',
                'simulated_wait': f'{duration_minutes} minutes',
                'actual_wait': f'{actual_wait:.2f}s'
            }
        }

    def _execute_condition(self, node: Dict, contact: Dict) -> Dict:
        """Execute condition node and evaluate logic"""
        node_data = node.get('data', {})
        condition_type = str(node_data.get('condition_type', 'unknown')).lower()
        title = node_data.get('title', 'Condition')

        # Evaluate condition based on contact state
        result = False
        reason = ''

        if 'email' in condition_type and 'open' in condition_type:
            # Check if contact opened emails
            emails_received = contact.get('emails_received', 0)
            engagement_rate = contact.get('email_engagement_rate', 0)
            result = emails_received > 0 and engagement_rate > 0.3
            reason = f'Email engagement: {engagement_rate*100:.0f}% ({"opened" if result else "not opened"})'

        elif 'sms' in condition_type and 'repl' in condition_type:
            # Check if contact replied to SMS
            sms_received = contact.get('sms_received', 0)
            reply_rate = contact.get('sms_reply_rate', 0)
            result = sms_received > 0 and reply_rate > 0.5
            reason = f'SMS reply rate: {reply_rate*100:.0f}% ({"replied" if result else "no reply"})'

        elif 'tag' in condition_type or 'has_tag' in condition_type:
            # Check if contact has tag
            required_tag = node_data.get('tag', 'unknown-tag')
            contact_tags = contact.get('tags', [])
            result = required_tag in contact_tags
            reason = f'Has tag "{required_tag}": {"Yes" if result else "No"}'

        elif 'purchase' in condition_type:
            # Check if contact made purchase
            result = contact.get('purchased', False)
            reason = f'Purchase made: {"Yes" if result else "No"}'

        elif 'delivery' in condition_type or 'check_delivery' in condition_type:
            # Check delivery status (simulate based on engagement)
            engagement_rate = contact.get('email_engagement_rate', 0.5)
            result = engagement_rate > 0.2  # Delivered if engagement > 20%
            reason = f'Delivery status: {"Success" if result else "Failed"}'

        else:
            # Default: evaluate based on engagement level
            engagement_level = contact.get('engagement_level', 'medium')
            if engagement_level == 'high':
                result = True
            elif engagement_level == 'low':
                result = False
            else:
                result = contact.get('email_engagement_rate', 0.5) > 0.4
            reason = f'Engagement level: {engagement_level}'

        return {
            'status': 'success',
            'message': f'Condition evaluated: {title}',
            'details': {
                'condition_type': condition_type,
                'result': 'TRUE' if result else 'FALSE',
                'reason': reason
            },
            'condition_result': result
        }

    def _substitute_variables(self, text: str, contact: Dict) -> str:
        """Substitute {{variable}} tokens with contact data"""
        if not text:
            return text

        # Common substitutions
        substitutions = {
            'contact.name': contact.get('name', 'Friend'),
            'contact.first_name': contact.get('first_name', contact.get('name', 'Friend').split()[0]),
            'contact.last_name': contact.get('last_name', ''),
            'contact.email': contact.get('email', 'email@example.com'),
            'contact.phone': contact.get('phone', '+1234567890'),
            'contact.company': contact.get('company', 'Your Company'),
            'unsubscribe_url': '[Unsubscribe Link]',
            'unsubscribe_link': '[Unsubscribe Link]'
        }

        # Replace {{var}} with values
        result = text
        for var, value in substitutions.items():
            pattern = r'\{\{\s*' + re.escape(var) + r'\s*\}\}'
            result = re.sub(pattern, str(value), result, flags=re.IGNORECASE)

        return result

    def _get_next_node(
        self,
        current_node: Dict,
        connections: List[Dict],
        execution_result: Dict
    ) -> Optional[str]:
        """Determine next node based on current node and execution result"""

        # If condition node, follow appropriate path based on result
        if current_node.get('type') == 'condition':
            condition_result = execution_result.get('condition_result', False)

            # Find connections from this node
            outgoing = [c for c in connections
                       if c.get('from') == current_node['id'] or c.get('source') == current_node['id']]

            # Look for labeled connections (yes/no, true/false, success/failure)
            for conn in outgoing:
                label = str(conn.get('label', '')).lower()
                if condition_result and ('yes' in label or 'true' in label or 'success' in label or 'valid' in label):
                    return conn.get('to') or conn.get('target')
                elif not condition_result and ('no' in label or 'false' in label or 'fail' in label or 'invalid' in label):
                    return conn.get('to') or conn.get('target')

            # If no labeled connections, take first one if condition is true
            if outgoing:
                if condition_result:
                    return outgoing[0].get('to') or outgoing[0].get('target')
                elif len(outgoing) > 1:
                    return outgoing[1].get('to') or outgoing[1].get('target')

        # For other nodes, follow first connection
        next_conn = next(
            (c for c in connections
             if c.get('from') == current_node['id'] or c.get('source') == current_node['id']),
            None
        )

        return next_conn.get('to') or next_conn.get('target') if next_conn else None

    def _log_step(
        self,
        node: Dict,
        status: str,
        message: str,
        details: Dict
    ):
        """Add execution step to log"""
        self.execution_log.append({
            'node_id': node['id'],
            'node_title': node.get('data', {}).get('title', 'Unknown'),
            'node_type': node.get('type', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'result': message,
            'details': details
        })

    def _calculate_total_time(self, workflow: Dict) -> str:
        """Calculate total workflow duration from all delays"""
        total_minutes = 0

        for node in workflow.get('nodes', []):
            if node.get('type') == 'delay':
                node_data = node.get('data', {})
                duration = node_data.get('delay_duration', 0)
                unit = node_data.get('unit', 'minutes')

                if unit == 'hours':
                    total_minutes += duration * 60
                elif unit == 'days':
                    total_minutes += duration * 1440
                else:
                    total_minutes += duration

        if total_minutes < 60:
            return f'{total_minutes} minutes'
        elif total_minutes < 1440:
            return f'{total_minutes / 60:.1f} hours'
        else:
            return f'{total_minutes / 1440:.1f} days'
