/**
 * SmartSuggestions Component
 * Enhancement 2: Smart Command Suggestions
 *
 * AI-powered workflow suggestions panel that:
 * - Analyzes current workflow context
 * - Suggests relevant next commands
 * - Uses semantic search + pattern rules
 * - Auto-updates when workflow changes
 * - One-click adds suggestions to canvas
 */

import React, { useEffect, useState, useCallback } from 'react';
import { SuggestionCard } from './SuggestionCard';
import './SmartSuggestions.css';

export function SmartSuggestions({
  currentWorkflow,
  onAddNode,
  isVisible = true,
  apiBaseUrl = 'http://localhost:8000'
}) {
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [contextSummary, setContextSummary] = useState('');

  // Fetch suggestions when workflow changes
  useEffect(() => {
    if (isVisible) {
      fetchSuggestions();
    }
  }, [currentWorkflow?.nodes?.length, isVisible]);

  const fetchSuggestions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Build context from current workflow
      const context = buildWorkflowContext(currentWorkflow);

      const response = await fetch(`${apiBaseUrl}/api/workflows/suggest-next`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setSuggestions(data.data.suggestions || []);
        setContextSummary(data.data.context_summary || '');
      } else {
        throw new Error(data.error || 'Failed to load suggestions');
      }
    } catch (err) {
      console.error('Suggestions error:', err);
      setError(err.message || 'Network error');
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  }, [currentWorkflow, apiBaseUrl]);

  const handleAddSuggestion = (suggestion) => {
    // Create node from suggestion
    const newNode = {
      id: `node-${Date.now()}`,
      type: 'action',
      data: {
        title: suggestion.title,
        description: suggestion.description,
        command_id: suggestion.command_id,
        category: suggestion.category,
        action_type: suggestion.command_id // Use command_id as action type
      },
      position: calculateNextPosition(currentWorkflow?.nodes || [])
    };

    if (onAddNode) {
      onAddNode(newNode);
    }

    // Log acceptance for analytics
    logSuggestionEvent(suggestion.command_id, 'accepted', {
      relevance_score: suggestion.relevance_score,
      workflow_size: currentWorkflow?.nodes?.length || 0
    });
  };

  const handleRejectSuggestion = (suggestion) => {
    // Remove from current suggestions
    setSuggestions(prev => prev.filter(s => s.command_id !== suggestion.command_id));

    // Log rejection for analytics
    logSuggestionEvent(suggestion.command_id, 'rejected', {
      relevance_score: suggestion.relevance_score,
      workflow_size: currentWorkflow?.nodes?.length || 0
    });
  };

  const logSuggestionEvent = async (commandId, action, context) => {
    try {
      // Future: Send to analytics endpoint
      console.log('[Analytics] Suggestion event:', {
        command_id: commandId,
        action,
        context,
        timestamp: new Date().toISOString()
      });
    } catch (err) {
      console.warn('Failed to log suggestion event:', err);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="smart-suggestions-panel">
      {/* Header */}
      <div className="suggestions-header">
        <div className="header-icon">[BULB]</div>
        <h3>Smart Suggestions</h3>
      </div>

      {/* Context Summary */}
      {contextSummary && !isLoading && (
        <div className="context-summary">
          {contextSummary}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="suggestions-loading">
          <div className="spinner"></div>
          <p>Finding relevant commands...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="suggestions-error">
          <p>{error}</p>
          <button onClick={fetchSuggestions} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {/* Suggestions List */}
      {!isLoading && !error && suggestions.length > 0 && (
        <div className="suggestions-list">
          {suggestions.map((suggestion, idx) => (
            <SuggestionCard
              key={`${suggestion.command_id}-${idx}`}
              suggestion={suggestion}
              onAdd={handleAddSuggestion}
              onReject={handleRejectSuggestion}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && suggestions.length === 0 && (
        <div className="suggestions-empty">
          <div className="empty-icon">[?]</div>
          <p>Add nodes to see suggestions</p>
        </div>
      )}

      {/* Refresh Button */}
      <div className="suggestions-footer">
        <button
          className="refresh-btn"
          onClick={fetchSuggestions}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh Suggestions'}
        </button>
      </div>
    </div>
  );
}

function buildWorkflowContext(workflow) {
  const nodes = workflow?.nodes || [];
  const lastNode = nodes.length > 0 ? nodes[nodes.length - 1] : null;

  return {
    last_node: lastNode,
    all_nodes: nodes,
    workflow_type: workflow?.metadata?.category || null,
    workflow_goal: workflow?.metadata?.description || null
  };
}

function calculateNextPosition(existingNodes) {
  if (existingNodes.length === 0) {
    return { x: 400, y: 100 };
  }

  // Position below last node
  const lastNode = existingNodes[existingNodes.length - 1];
  return {
    x: lastNode.position?.x || 400,
    y: (lastNode.position?.y || 100) + 150
  };
}
