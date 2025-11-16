/**
 * SuggestionCard Component
 * Enhancement 2: Smart Command Suggestions
 *
 * Displays a single workflow suggestion with:
 * - Title and description
 * - Category badge and icon
 * - Reasoning for the suggestion
 * - Relevance score bar
 * - Add button to insert into workflow
 */

import React from 'react';
import './SuggestionCard.css';

export function SuggestionCard({ suggestion, onAdd, onReject }) {
  const handleAdd = () => {
    onAdd(suggestion);
  };

  const handleReject = () => {
    if (onReject) {
      onReject(suggestion);
    }
  };

  return (
    <div className="suggestion-card">
      <div className="card-header">
        <span className="card-icon">{suggestion.icon}</span>
        <span className="card-category">{suggestion.category}</span>
      </div>

      <h4 className="card-title">{suggestion.title}</h4>
      <p className="card-description">{suggestion.description}</p>

      <div className="card-footer">
        <div className="card-reason">
          <span className="reason-label">Why?</span>
          <span className="reason-text">{suggestion.reason}</span>
        </div>

        <div className="card-score">
          <div className="score-bar">
            <div
              className="score-fill"
              style={{ width: `${Math.min(suggestion.relevance_score, 100)}%` }}
            />
          </div>
          <span className="score-text">{suggestion.relevance_score}% match</span>
        </div>
      </div>

      <div className="card-actions">
        <button className="add-btn" onClick={handleAdd} title="Add to workflow">
          <span className="btn-icon">+</span>
          Add to Workflow
        </button>
        {onReject && (
          <button className="reject-btn" onClick={handleReject} title="Not helpful">
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
