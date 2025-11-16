/**
 * ValidationIssue Component
 * Enhancement 4: Workflow Validator & Best Practices Checker
 *
 * Displays individual validation issue with:
 * - Severity indicator (error/warning/suggestion)
 * - Title and description
 * - Affected nodes
 * - Quick Fix button
 */

import React, { useState } from 'react';
import './ValidationIssue.css';

export function ValidationIssue({ issue, onApplyFix }) {
  const [isApplying, setIsApplying] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleApplyFix = async () => {
    if (!onApplyFix || !issue.fix_suggestion) return;

    setIsApplying(true);
    try {
      await onApplyFix(issue);
    } catch (err) {
      console.error('Failed to apply fix:', err);
    } finally {
      setIsApplying(false);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'error': return '[!]';
      case 'warning': return '[/!]';
      case 'suggestion': return '[i]';
      default: return '[?]';
    }
  };

  const formatFixSuggestion = (fix) => {
    if (!fix) return null;

    const actions = {
      'add_condition_node': 'Add error handling condition',
      'add_delay_and_followup': `Add ${fix.delay_duration ? Math.floor(fix.delay_duration / 1440) : 2} day delay + follow-up`,
      'add_personalization': `Add ${fix.token || 'personalization'} token`,
      'add_unsubscribe_link': 'Add unsubscribe link',
      'add_validation_condition': 'Add data validation',
      'add_delay': `Add ${fix.delay_hours || 24}h delay`,
      'add_tag': `Add "${fix.tag_name || 'tracking'}" tag`,
      'merge_nodes': 'Merge duplicate nodes',
      'break_loop': 'Break infinite loop',
      'connect_node': 'Connect orphaned node',
      'add_ab_test': 'Add A/B test variant',
      'add_goal_tracking': 'Add goal tracking',
      'add_sms_fallback': 'Add SMS fallback'
    };

    return actions[fix.action] || 'Apply suggested fix';
  };

  return (
    <div className={`validation-issue ${issue.severity}`}>
      <div className="issue-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="issue-left">
          <span className="severity-icon">{getSeverityIcon(issue.severity)}</span>
          <div className="issue-info">
            <h4 className="issue-title">{issue.title}</h4>
            <p className="issue-description">{issue.description}</p>
          </div>
        </div>
        <button
          className="expand-btn"
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? '[-]' : '[+]'}
        </button>
      </div>

      {isExpanded && (
        <div className="issue-details">
          {/* Affected Nodes */}
          {issue.affected_nodes && issue.affected_nodes.length > 0 && (
            <div className="affected-nodes">
              <span className="detail-label">Affected nodes:</span>
              <div className="node-badges">
                {issue.affected_nodes.map((nodeId, idx) => (
                  <span key={idx} className="node-badge">
                    {nodeId}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Fix Suggestion */}
          {issue.fix_suggestion && (
            <div className="fix-section">
              <div className="fix-info">
                <span className="fix-icon">[WRENCH]</span>
                <span className="fix-text">
                  {formatFixSuggestion(issue.fix_suggestion)}
                </span>
              </div>
              <button
                className="quick-fix-btn"
                onClick={handleApplyFix}
                disabled={isApplying}
              >
                {isApplying ? 'Applying...' : 'Quick Fix'}
              </button>
            </div>
          )}

          {/* Rule ID (for debugging) */}
          <div className="rule-id">
            Rule: {issue.rule_id}
          </div>
        </div>
      )}
    </div>
  );
}
