/**
 * SearchResults Component
 * Built with BMAD-METHOD for Epic US: Unified Search
 *
 * Displays search results grouped by type with:
 * - Top Answer (highest relevance)
 * - Documentation section
 * - Commands section (when available)
 * - Related suggestions
 * - Intent badge
 */

import React from 'react';
import ResultCard from './ResultCard';
import './UnifiedSearch.css';

const SearchResults = ({ searchData, onSuggestionClick }) => {
  if (!searchData) {
    return null;
  }

  const { query, intent, total_results, results, suggestions, search_time_ms } = searchData;

  // No results found
  if (total_results === 0) {
    return (
      <div className="search-results-empty">
        <div className="empty-icon">🔍</div>
        <h3 className="empty-title">No results found</h3>
        <p className="empty-message">
          Try different keywords or check your spelling
        </p>
        {suggestions && suggestions.length > 0 && (
          <div className="suggestions-section">
            <p className="suggestions-title">Try these instead:</p>
            <div className="suggestions-list">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => onSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="search-results-container">
      {/* Search Meta Info */}
      <div className="search-meta">
        <div className="search-meta-left">
          <span className="intent-badge intent-{intent.toLowerCase()}">
            {intent.replace('_', ' ')}
          </span>
          <span className="results-count">
            {total_results} result{total_results !== 1 ? 's' : ''}
          </span>
          <span className="search-time">
            {search_time_ms}ms
          </span>
        </div>
      </div>

      {/* Top Answer Section */}
      {results.topAnswer && (
        <div className="top-answer-section">
          <div className="section-header">
            <div className="section-icon">⭐</div>
            <h3 className="section-title">Top Answer</h3>
          </div>
          <ResultCard result={results.topAnswer} isTopAnswer={true} />
        </div>
      )}

      {/* Documentation Section */}
      {results.documentation && results.documentation.length > 0 && (
        <div className="results-section">
          <div className="section-header">
            <div className="section-icon">📚</div>
            <h3 className="section-title">
              Documentation
              <span className="section-count">
                ({results.documentation.length})
              </span>
            </h3>
          </div>
          <div className="results-grid">
            {results.documentation.map((result, index) => (
              <ResultCard key={result.id || index} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* Commands Section (when ghl-knowledge-base has data) */}
      {results.commands && results.commands.length > 0 && (
        <div className="results-section">
          <div className="section-header">
            <div className="section-icon">⚡</div>
            <h3 className="section-title">
              Commands
              <span className="section-count">
                ({results.commands.length})
              </span>
            </h3>
          </div>
          <div className="results-grid">
            {results.commands.map((result, index) => (
              <ResultCard key={result.id || index} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* Related Suggestions */}
      {suggestions && suggestions.length > 0 && (
        <div className="suggestions-section">
          <div className="section-header">
            <div className="section-icon">💡</div>
            <h3 className="section-title">Related Searches</h3>
          </div>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-chip"
                onClick={() => onSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Stats Footer */}
      <div className="search-footer">
        <div className="footer-stats">
          {results.total_by_type && (
            <>
              {results.total_by_type.documentation > 0 && (
                <span className="stat-item">
                  📚 {results.total_by_type.documentation} docs
                </span>
              )}
              {results.total_by_type.commands > 0 && (
                <span className="stat-item">
                  ⚡ {results.total_by_type.commands} commands
                </span>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchResults;
