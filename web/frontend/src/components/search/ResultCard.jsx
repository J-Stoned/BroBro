/**
 * ResultCard Component
 * Built with BMAD-METHOD for Epic US: Unified Search
 *
 * Displays individual search result with:
 * - Title and description
 * - Relevance score (0-100)
 * - Collection type badge
 * - Category tag
 * - Link to source
 */

import React from 'react';
import './UnifiedSearch.css';

const ResultCard = ({ result, isTopAnswer = false }) => {
  const {
    title,
    description,
    relevance_score,
    collection,
    type,
    category,
    url,
    has_examples,
    metadata
  } = result;

  // Truncate description to reasonable length
  const truncatedDescription = description && description.length > 200
    ? description.substring(0, 200) + '...'
    : description;

  // Get collection display name and color
  const getCollectionInfo = (coll) => {
    switch (coll) {
      case 'ghl-docs':
        return { label: 'Documentation', color: 'blue' };
      case 'ghl-knowledge-base':
        return { label: 'Command', color: 'purple' };
      case 'workflows':
        return { label: 'Workflow', color: 'green' };
      case 'conversations':
        return { label: 'Chat', color: 'orange' };
      default:
        return { label: coll, color: 'gray' };
    }
  };

  const collectionInfo = getCollectionInfo(collection);

  // Format relevance score for display
  const formattedScore = relevance_score ? Math.round(relevance_score) : 0;

  // Score color based on value
  const getScoreColor = (score) => {
    if (score >= 80) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
  };

  const handleClick = (e) => {
    if (url) {
      // Open external links in new tab
      e.preventDefault();
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className={`result-card ${isTopAnswer ? 'top-answer-card' : ''}`}>
      {/* Card Header */}
      <div className="card-header">
        <div className="card-badges">
          <span className={`collection-badge collection-${collectionInfo.color}`}>
            {collectionInfo.label}
          </span>
          {category && category !== 'General' && (
            <span className="category-badge">
              {category}
            </span>
          )}
          {has_examples && (
            <span className="feature-badge" title="Includes examples">
              📝 Examples
            </span>
          )}
        </div>

        {isTopAnswer && (
          <div className={`relevance-score score-${getScoreColor(formattedScore)}`}>
            <span className="score-value">{formattedScore}</span>
            <span className="score-label">%</span>
          </div>
        )}
      </div>

      {/* Card Body */}
      <div className="card-body">
        <h4 className="card-title">
          {url ? (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="card-title-link"
              onClick={handleClick}
            >
              {title}
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                className="external-link-icon"
              >
                <path
                  d="M11 7.5v3.5c0 .55-.45 1-1 1H3c-.55 0-1-.45-1-1V4c0-.55.45-1 1-1h3.5M9 2h5v5M6.5 7.5L14 0"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </a>
          ) : (
            title
          )}
        </h4>

        {truncatedDescription && (
          <p className="card-description">
            {truncatedDescription}
          </p>
        )}
      </div>

      {/* Card Footer */}
      {!isTopAnswer && formattedScore > 0 && (
        <div className="card-footer">
          <div className={`relevance-bar score-${getScoreColor(formattedScore)}`}>
            <div
              className="relevance-fill"
              style={{ width: `${formattedScore}%` }}
            ></div>
          </div>
          <span className="relevance-text">
            {formattedScore}% match
          </span>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
