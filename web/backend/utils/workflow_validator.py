"""
Workflow Validator - Enhancement 4
Comprehensive workflow validation with 20+ best practice rules
Built with BMAD methodology
"""

from typing import List, Dict, Optional
from datetime import datetime


class ValidationIssue:
    """Represents a validation issue found in a workflow"""

    def __init__(
        self,
        severity: str,  # 'error', 'warning', 'suggestion'
        rule_id: str,
        title: str,
        description: str,
        affected_nodes: List[str],
        fix_suggestion: Optional[Dict] = None
    ):
        self.severity = severity
        self.rule_id = rule_id
        self.title = title
        self.description = description
        self.affected_nodes = affected_nodes
        self.fix_suggestion = fix_suggestion

    def to_dict(self):
        return {
            'severity': self.severity,
            'rule_id': self.rule_id,
            'title': self.title,
            'description': self.description,
            'affected_nodes': self.affected_nodes,
            'fix_suggestion': self.fix_suggestion
        }


class WorkflowValidator:
    """
    Validates workflows against automation best practices

    Features:
    - 20+ validation rules
    - Severity levels (error/warning/suggestion)
    - Scoring system (0-100)
    - Actionable fix suggestions
    - Performance optimized (<1s for 20 nodes)
    """

    def __init__(self):
        self.rules_count = 20

    def validate(self, workflow: Dict) -> Dict:
        """
        Comprehensive workflow validation

        Returns validation report with:
        - is_valid: bool (no errors)
        - score: int (0-100)
        - issues: list of ValidationIssue
        - stats: error/warning/suggestion counts
        - best_practices_met: percentage
        """
        issues = []
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', [])

        # Run all 20+ validation rules
        issues.extend(self._check_missing_error_handling(nodes, connections))
        issues.extend(self._check_no_follow_up_actions(nodes, connections))
        issues.extend(self._check_missing_tracking(nodes))
        issues.extend(self._check_timing_issues(nodes))
        issues.extend(self._check_duplicate_actions(nodes))
        issues.extend(self._check_infinite_loops(nodes, connections))
        issues.extend(self._check_orphaned_nodes(nodes, connections))
        issues.extend(self._check_missing_personalization(nodes))
        issues.extend(self._check_no_unsubscribe_link(nodes))
        issues.extend(self._check_poor_email_timing(nodes))
        issues.extend(self._check_sms_quiet_hours(nodes))
        issues.extend(self._check_missing_conditions(nodes, connections))
        issues.extend(self._check_too_many_emails(nodes))
        issues.extend(self._check_no_ab_testing(nodes))
        issues.extend(self._check_missing_delays(nodes, connections))
        issues.extend(self._check_unclear_node_names(nodes))
        issues.extend(self._check_complex_workflow(nodes))
        issues.extend(self._check_missing_goal_tracking(workflow))
        issues.extend(self._check_no_fallback_channel(nodes))
        issues.extend(self._check_missing_contact_validation(nodes))

        # Calculate statistics
        errors = sum(1 for i in issues if i.severity == 'error')
        warnings = sum(1 for i in issues if i.severity == 'warning')
        suggestions = sum(1 for i in issues if i.severity == 'suggestion')

        # Calculate score (100 - penalties)
        score = 100
        score -= errors * 15      # -15 per error
        score -= warnings * 5     # -5 per warning
        score -= suggestions * 2  # -2 per suggestion
        score = max(0, score)

        # Calculate best practices percentage
        rules_passed = self.rules_count - len(issues)
        best_practices_met = max(0, (rules_passed / self.rules_count) * 100)

        return {
            'is_valid': errors == 0,
            'score': round(score),
            'issues': [issue.to_dict() for issue in issues],
            'stats': {
                'errors': errors,
                'warnings': warnings,
                'suggestions': suggestions
            },
            'best_practices_met': round(best_practices_met),
            'timestamp': datetime.now().isoformat()
        }

    # VALIDATION RULES (20+)

    def _check_missing_error_handling(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 1: Critical actions should have error handling"""
        issues = []

        for node in nodes:
            if node.get('type') != 'action':
                continue

            action_type = str(node.get('data', {}).get('action_type', '')).lower()

            if 'email' in action_type or 'sms' in action_type:
                # Check for conditional paths
                has_error_path = any(
                    conn.get('source') == node['id'] and
                    str(conn.get('label', '')).lower() in ['failure', 'error', 'failed']
                    for conn in connections
                )

                if not has_error_path:
                    issues.append(ValidationIssue(
                        severity='warning',
                        rule_id='missing-error-handling',
                        title='Missing Error Handling',
                        description=f"{node.get('data', {}).get('title', 'Action')} has no failure path",
                        affected_nodes=[node['id']],
                        fix_suggestion={
                            'action': 'add_condition_node',
                            'type': 'check_delivery_status',
                            'after_node': node['id']
                        }
                    ))

        return issues

    def _check_no_follow_up_actions(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 2: Actions should have follow-ups"""
        issues = []

        if len(nodes) == 1 and nodes[0].get('type') == 'action':
            node = nodes[0]
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='no-follow-up',
                title='No Follow-up Action',
                description=f"Single action without follow-up. Add delay + follow-up for better engagement.",
                affected_nodes=[node['id']],
                fix_suggestion={
                    'action': 'add_delay_and_followup',
                    'delay_duration': 2880,  # 2 days
                    'after_node': node['id']
                }
            ))

        return issues

    def _check_missing_tracking(self, nodes) -> List[ValidationIssue]:
        """Rule 3: Workflows should use tags for tracking"""
        issues = []

        has_tag = any(
            node.get('type') == 'action' and
            'tag' in str(node.get('data', {}).get('action_type', '')).lower()
            for node in nodes
        )

        if not has_tag and len(nodes) > 2:
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='missing-tracking',
                title='Missing Progress Tracking',
                description='Add tags to track workflow progress and segment contacts',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'add_tag_action',
                    'tag_name': 'workflow-entered',
                    'position': 'after_trigger'
                }
            ))

        return issues

    def _check_timing_issues(self, nodes) -> List[ValidationIssue]:
        """Rule 4: SMS timing validation"""
        issues = []

        for node in nodes:
            if node.get('type') == 'action':
                action_type = str(node.get('data', {}).get('action_type', '')).lower()

                if 'sms' in action_type:
                    issues.append(ValidationIssue(
                        severity='warning',
                        rule_id='sms-timing',
                        title='SMS Timing Not Verified',
                        description=f"SMS should only be sent during business hours (9am-8pm)",
                        affected_nodes=[node['id']],
                        fix_suggestion={
                            'action': 'add_time_condition',
                            'before_node': node['id'],
                            'allowed_hours': '9:00-20:00'
                        }
                    ))

        return issues

    def _check_duplicate_actions(self, nodes) -> List[ValidationIssue]:
        """Rule 5: Avoid duplicate actions"""
        issues = []
        seen_titles = {}

        for node in nodes:
            if node.get('type') == 'action':
                title = node.get('data', {}).get('title', '')
                if title in seen_titles:
                    issues.append(ValidationIssue(
                        severity='warning',
                        rule_id='duplicate-action',
                        title='Duplicate Action',
                        description=f"'{title}' appears multiple times",
                        affected_nodes=[node['id'], seen_titles[title]],
                        fix_suggestion={
                            'action': 'consolidate_actions',
                            'nodes': [node['id'], seen_titles[title]]
                        }
                    ))
                else:
                    seen_titles[title] = node['id']

        return issues

    def _check_infinite_loops(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 6: Detect circular dependencies"""
        issues = []

        def has_cycle(node_id, path, visited):
            if node_id in path:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            path.add(node_id)

            for conn in connections:
                if conn.get('source') == node_id:
                    if has_cycle(conn.get('target'), path.copy(), visited):
                        return True

            return False

        visited_global = set()
        for node in nodes:
            if has_cycle(node['id'], set(), visited_global):
                issues.append(ValidationIssue(
                    severity='error',
                    rule_id='infinite-loop',
                    title='Potential Infinite Loop',
                    description='Workflow may loop infinitely. Add exit condition.',
                    affected_nodes=[node['id']],
                    fix_suggestion={
                        'action': 'add_exit_condition',
                        'type': 'max_iterations',
                        'max_count': 5
                    }
                ))
                break

        return issues

    def _check_orphaned_nodes(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 7: All nodes should be connected"""
        issues = []

        if not nodes:
            return issues

        connected = set()
        for conn in connections:
            # Support both 'from'/'to' and 'source'/'target' formats
            from_node = conn.get('from') or conn.get('source')
            to_node = conn.get('to') or conn.get('target')

            if from_node:
                connected.add(from_node)
            if to_node:
                connected.add(to_node)

        # First node is always connected (trigger)
        if nodes:
            connected.add(nodes[0]['id'])

        for node in nodes:
            if node['id'] not in connected:
                issues.append(ValidationIssue(
                    severity='error',
                    rule_id='orphaned-node',
                    title='Disconnected Node',
                    description=f"{node.get('data', {}).get('title', 'Node')} is not connected",
                    affected_nodes=[node['id']],
                    fix_suggestion={
                        'action': 'connect_node',
                        'node_id': node['id']
                    }
                ))

        return issues

    def _check_missing_personalization(self, nodes) -> List[ValidationIssue]:
        """Rule 8: Messages should be personalized"""
        issues = []

        for node in nodes:
            if node.get('type') == 'action':
                action_type = str(node.get('data', {}).get('action_type', '')).lower()
                message = str(node.get('data', {}).get('message', ''))

                if ('email' in action_type or 'sms' in action_type) and message:
                    has_personalization = '{{' in message

                    if not has_personalization:
                        issues.append(ValidationIssue(
                            severity='suggestion',
                            rule_id='missing-personalization',
                            title='Missing Personalization',
                            description=f"Consider personalizing with {{{{contact.first_name}}}}",
                            affected_nodes=[node['id']],
                            fix_suggestion={
                                'action': 'add_personalization',
                                'token': '{{contact.first_name}}',
                                'node_id': node['id']
                            }
                        ))

        return issues

    def _check_no_unsubscribe_link(self, nodes) -> List[ValidationIssue]:
        """Rule 9: Marketing emails need unsubscribe"""
        issues = []

        for node in nodes:
            if node.get('type') == 'action':
                action_type = str(node.get('data', {}).get('action_type', '')).lower()
                message = str(node.get('data', {}).get('message', '')).lower()

                if 'email' in action_type and message:
                    if 'unsubscribe' not in message:
                        issues.append(ValidationIssue(
                            severity='warning',
                            rule_id='no-unsubscribe',
                            title='Missing Unsubscribe Link',
                            description='Marketing emails should include unsubscribe link',
                            affected_nodes=[node['id']],
                            fix_suggestion={
                                'action': 'add_unsubscribe_link',
                                'node_id': node['id']
                            }
                        ))

        return issues

    def _check_poor_email_timing(self, nodes) -> List[ValidationIssue]:
        """Rule 10: Space out emails properly"""
        issues = []

        for i in range(len(nodes) - 1):
            curr = nodes[i]
            next_node = nodes[i + 1]

            if (curr.get('type') == 'action' and
                'email' in str(curr.get('data', {}).get('action_type', '')).lower() and
                next_node.get('type') == 'action' and
                'email' in str(next_node.get('data', {}).get('action_type', '')).lower()):

                issues.append(ValidationIssue(
                    severity='suggestion',
                    rule_id='rapid-emails',
                    title='Emails Too Close Together',
                    description='Add delay between consecutive emails',
                    affected_nodes=[curr['id'], next_node['id']],
                    fix_suggestion={
                        'action': 'add_delay',
                        'before_node': next_node['id'],
                        'duration': 1440  # 1 day
                    }
                ))

        return issues

    def _check_sms_quiet_hours(self, nodes) -> List[ValidationIssue]:
        """Rule 11: Respect SMS quiet hours"""
        issues = []

        for node in nodes:
            if node.get('type') == 'action':
                action_type = str(node.get('data', {}).get('action_type', '')).lower()

                if 'sms' in action_type:
                    # Simplified check - in production would check for time condition
                    issues.append(ValidationIssue(
                        severity='warning',
                        rule_id='sms-quiet-hours',
                        title='SMS Quiet Hours Not Enforced',
                        description='Add time condition to avoid late-night SMS',
                        affected_nodes=[node['id']],
                        fix_suggestion={
                            'action': 'add_time_gate',
                            'before_node': node['id'],
                            'quiet_hours': '21:00-09:00'
                        }
                    ))

        return issues

    def _check_missing_conditions(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 12: Long workflows need decision points"""
        issues = []

        if len(nodes) > 5:
            has_condition = any(node.get('type') == 'condition' for node in nodes)

            if not has_condition:
                issues.append(ValidationIssue(
                    severity='suggestion',
                    rule_id='missing-conditions',
                    title='No Decision Points',
                    description='Long workflows benefit from personalized paths',
                    affected_nodes=[],
                    fix_suggestion={
                        'action': 'add_condition',
                        'type': 'check_engagement',
                        'position': 'mid_workflow'
                    }
                ))

        return issues

    def _check_too_many_emails(self, nodes) -> List[ValidationIssue]:
        """Rule 13: Don't overwhelm with emails"""
        issues = []

        email_count = sum(
            1 for node in nodes
            if node.get('type') == 'action' and
            'email' in str(node.get('data', {}).get('action_type', '')).lower()
        )

        if email_count > 5:
            issues.append(ValidationIssue(
                severity='warning',
                rule_id='too-many-emails',
                title='High Email Volume',
                description=f'{email_count} emails may overwhelm contacts',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'reduce_email_count',
                    'current': email_count,
                    'recommended': 5
                }
            ))

        return issues

    def _check_no_ab_testing(self, nodes) -> List[ValidationIssue]:
        """Rule 14: Consider A/B testing"""
        issues = []

        has_email = any(
            node.get('type') == 'action' and
            'email' in str(node.get('data', {}).get('action_type', '')).lower()
            for node in nodes
        )

        has_ab = any(
            node.get('type') == 'condition' and
            'ab' in str(node.get('data', {}).get('title', '')).lower()
            for node in nodes
        )

        if has_email and not has_ab and len(nodes) > 3:
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='no-ab-testing',
                title='Consider A/B Testing',
                description='Test different messages to improve engagement',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'add_ab_test',
                    'position': 'first_email'
                }
            ))

        return issues

    def _check_missing_delays(self, nodes, connections) -> List[ValidationIssue]:
        """Rule 15: Actions need delays between them"""
        issues = []

        for i in range(len(nodes) - 1):
            curr = nodes[i]
            next_node = nodes[i + 1]

            if (curr.get('type') == 'action' and
                next_node.get('type') == 'action' and
                next_node.get('type') != 'delay'):

                issues.append(ValidationIssue(
                    severity='warning',
                    rule_id='missing-delay',
                    title='Missing Delay Between Actions',
                    description='Add delay for better pacing',
                    affected_nodes=[curr['id'], next_node['id']],
                    fix_suggestion={
                        'action': 'insert_delay',
                        'between_nodes': [curr['id'], next_node['id']],
                        'duration': 1440
                    }
                ))

        return issues

    def _check_unclear_node_names(self, nodes) -> List[ValidationIssue]:
        """Rule 16: Use descriptive names"""
        issues = []

        generic_names = ['action', 'send', 'wait', 'check', 'node', 'step']

        for node in nodes:
            title = str(node.get('data', {}).get('title', '')).lower()

            if any(title == name for name in generic_names):
                issues.append(ValidationIssue(
                    severity='suggestion',
                    rule_id='unclear-name',
                    title='Unclear Node Name',
                    description=f"'{title}' is too generic. Use descriptive names.",
                    affected_nodes=[node['id']],
                    fix_suggestion={
                        'action': 'rename_node',
                        'node_id': node['id']
                    }
                ))

        return issues

    def _check_complex_workflow(self, nodes) -> List[ValidationIssue]:
        """Rule 17: Split complex workflows"""
        issues = []

        if len(nodes) > 15:
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='complex-workflow',
                title='Workflow Too Complex',
                description=f'{len(nodes)} nodes. Consider splitting into multiple workflows.',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'suggest_split',
                    'current_nodes': len(nodes),
                    'recommended_max': 15
                }
            ))

        return issues

    def _check_missing_goal_tracking(self, workflow) -> List[ValidationIssue]:
        """Rule 18: Define measurable goals"""
        issues = []

        metadata = workflow.get('metadata', {})
        has_goal = metadata.get('goal') or metadata.get('success_metric')

        if not has_goal and len(workflow.get('nodes', [])) > 3:
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='missing-goal',
                title='No Success Metric Defined',
                description='Define a goal to measure workflow success',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'add_goal_tracking',
                    'suggested_metrics': ['open_rate', 'click_rate', 'conversion_rate']
                }
            ))

        return issues

    def _check_no_fallback_channel(self, nodes) -> List[ValidationIssue]:
        """Rule 19: Add fallback communication"""
        issues = []

        has_email = any(
            node.get('type') == 'action' and
            'email' in str(node.get('data', {}).get('action_type', '')).lower()
            for node in nodes
        )

        has_sms = any(
            node.get('type') == 'action' and
            'sms' in str(node.get('data', {}).get('action_type', '')).lower()
            for node in nodes
        )

        if has_email and not has_sms and len(nodes) > 2:
            issues.append(ValidationIssue(
                severity='suggestion',
                rule_id='no-fallback-channel',
                title='No Fallback Channel',
                description='Add SMS as fallback if email fails',
                affected_nodes=[],
                fix_suggestion={
                    'action': 'add_sms_fallback'
                }
            ))

        return issues

    def _check_missing_contact_validation(self, nodes) -> List[ValidationIssue]:
        """Rule 20: Validate contact data exists"""
        issues = []

        for node in nodes:
            if node.get('type') == 'action':
                action_type = str(node.get('data', {}).get('action_type', '')).lower()

                if 'email' in action_type or 'sms' in action_type:
                    issues.append(ValidationIssue(
                        severity='suggestion',
                        rule_id='missing-validation',
                        title='No Contact Data Validation',
                        description='Check if contact has email/phone before sending',
                        affected_nodes=[node['id']],
                        fix_suggestion={
                            'action': 'add_validation_condition',
                            'before_node': node['id'],
                            'check': 'has_email' if 'email' in action_type else 'has_phone'
                        }
                    ))

        return issues
