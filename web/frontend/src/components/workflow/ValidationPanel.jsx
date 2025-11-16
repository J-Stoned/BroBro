/**
 * ValidationPanel Component
 * Enhancement 4: Workflow Validator & Best Practices Checker
 *
 * Modal panel that displays:
 * - Workflow validation score (0-100)
 * - Issues grouped by severity (error, warning, suggestion)
 * - One-click fix buttons for each issue
 * - Auto-validates when workflow changes
 */

import React, { useEffect, useState, useCallback } from 'react';
import { ValidationIssue } from './ValidationIssue';
import './ValidationPanel.css';

export function ValidationPanel({
  workflow,
  isVisible = false,
  onClose,
  onApplyFix,
  apiBaseUrl = 'http://localhost:8000'
}) {
  const [validationResult, setValidationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-validate when workflow changes
  useEffect(() => {
    if (isVisible && workflow) {
      validateWorkflow();
    }
  }, [workflow?.nodes?.length, workflow?.connections?.length, isVisible]);

  const validateWorkflow = useCallback(async () => {
    if (!workflow) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/workflows/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nodes: workflow.nodes || [],
          connections: workflow.connections || [],
          metadata: workflow.metadata || {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setValidationResult(data.data);
      } else {
        throw new Error(data.error || 'Validation failed');
      }
    } catch (err) {
      console.error('Validation error:', err);
      setError(err.message || 'Network error');
      setValidationResult(null);
    } finally {
      setIsLoading(false);
    }
  }, [workflow, apiBaseUrl]);

  const handleApplyFix = async (issue) => {
    if (onApplyFix) {
      await onApplyFix(issue);
      // Re-validate after fix
      setTimeout(() => validateWorkflow(), 100);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981'; // green
    if (score >= 75) return '#3b82f6'; // blue
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const getScoreGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  // Group issues by severity
  const groupedIssues = validationResult?.issues?.reduce((acc, issue) => {
    if (!acc[issue.severity]) {
      acc[issue.severity] = [];
    }
    acc[issue.severity].push(issue);
    return acc;
  }, { error: [], warning: [], suggestion: [] }) || { error: [], warning: [], suggestion: [] };

  if (!isVisible) return null;

  return (
    <div className="validation-modal-overlay" onClick={onClose}>
      <div className="validation-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="validation-header">
          <div className="header-left">
            <div className="header-icon">[CHECK]</div>
            <h2>Workflow Validation</h2>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="validation-loading">
            <div className="spinner"></div>
            <p>Validating workflow...</p>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="validation-error">
            <p>{error}</p>
            <button onClick={validateWorkflow} className="retry-btn">
              Retry Validation
            </button>
          </div>
        )}

        {/* Results */}
        {validationResult && !isLoading && !error && (
          <>
            {/* Score Display */}
            <div className="validation-score-section">
              <div
                className="score-circle"
                style={{ borderColor: getScoreColor(validationResult.score) }}
              >
                <div className="score-value" style={{ color: getScoreColor(validationResult.score) }}>
                  {validationResult.score}
                </div>
                <div className="score-grade">{getScoreGrade(validationResult.score)}</div>
              </div>
              <div className="score-details">
                <h3>Overall Score</h3>
                <div className="score-stats">
                  <div className="stat-item error">
                    <span className="stat-icon">[!]</span>
                    <span className="stat-count">{validationResult.stats.errors}</span>
                    <span className="stat-label">Errors</span>
                  </div>
                  <div className="stat-item warning">
                    <span className="stat-icon">[/!]</span>
                    <span className="stat-count">{validationResult.stats.warnings}</span>
                    <span className="stat-label">Warnings</span>
                  </div>
                  <div className="stat-item suggestion">
                    <span className="stat-icon">[i]</span>
                    <span className="stat-count">{validationResult.stats.suggestions}</span>
                    <span className="stat-label">Suggestions</span>
                  </div>
                </div>
                <div className="best-practices-bar">
                  <div className="bar-label">Best Practices: {validationResult.best_practices_met}%</div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${validationResult.best_practices_met}%`,
                        background: getScoreColor(validationResult.best_practices_met)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Issues List */}
            <div className="validation-issues">
              {/* Errors */}
              {groupedIssues.error.length > 0 && (
                <div className="issue-section error-section">
                  <h3 className="section-title">
                    <span className="title-icon">[!]</span>
                    Errors ({groupedIssues.error.length})
                  </h3>
                  <p className="section-description">
                    Critical issues that must be fixed before deployment
                  </p>
                  <div className="issue-list">
                    {groupedIssues.error.map((issue, idx) => (
                      <ValidationIssue
                        key={`error-${idx}`}
                        issue={issue}
                        onApplyFix={handleApplyFix}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Warnings */}
              {groupedIssues.warning.length > 0 && (
                <div className="issue-section warning-section">
                  <h3 className="section-title">
                    <span className="title-icon">[/!]</span>
                    Warnings ({groupedIssues.warning.length})
                  </h3>
                  <p className="section-description">
                    Important issues that should be addressed
                  </p>
                  <div className="issue-list">
                    {groupedIssues.warning.map((issue, idx) => (
                      <ValidationIssue
                        key={`warning-${idx}`}
                        issue={issue}
                        onApplyFix={handleApplyFix}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {groupedIssues.suggestion.length > 0 && (
                <div className="issue-section suggestion-section">
                  <h3 className="section-title">
                    <span className="title-icon">[i]</span>
                    Suggestions ({groupedIssues.suggestion.length})
                  </h3>
                  <p className="section-description">
                    Optimization opportunities to improve your workflow
                  </p>
                  <div className="issue-list">
                    {groupedIssues.suggestion.map((issue, idx) => (
                      <ValidationIssue
                        key={`suggestion-${idx}`}
                        issue={issue}
                        onApplyFix={handleApplyFix}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* No Issues */}
              {validationResult.issues.length === 0 && (
                <div className="no-issues">
                  <div className="success-icon">[✓]</div>
                  <h3>Perfect Workflow!</h3>
                  <p>No issues found. Your workflow follows all best practices.</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Footer */}
        <div className="validation-footer">
          <button className="refresh-btn" onClick={validateWorkflow} disabled={isLoading}>
            {isLoading ? 'Validating...' : 'Re-validate Workflow'}
          </button>
          <button className="close-footer-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
