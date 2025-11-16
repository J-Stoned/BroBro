/**
 * UnifiedSearchContainer Component
 * Built with BMAD-METHOD for Epic US: Unified Search
 *
 * Main container that orchestrates:
 * - Search bar with keyboard shortcuts
 * - API calls to backend
 * - Results display
 * - Error handling
 */

import React, { useState } from 'react';
import UnifiedSearchBar from './UnifiedSearchBar';
import SearchResults from './SearchResults';
import { getErrorText } from '../../utils/api';
import './UnifiedSearch.css';

const UnifiedSearchContainer = () => {
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Execute search API call
  const handleSearch = async (query) => {
    if (!query || !query.trim()) {
      setSearchResults(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/search/unified?query=${encodeURIComponent(query)}&limit=20`
      );

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setSearchResults(data.data);
      } else {
        throw new Error(data.error || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message);
      setSearchResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    handleSearch(suggestion);
  };

  return (
    <div className="unified-search-container-page">
      <div className="search-header">
        <h2 className="search-page-title">Unified Search</h2>
        <p className="search-page-subtitle">
          Search across all documentation, commands, and workflows with intelligent intent detection
        </p>
      </div>

      <UnifiedSearchBar onSearch={handleSearch} />

      {/* Loading State */}
      {isLoading && (
        <div className="search-loading-state">
          <div className="spinner-large"></div>
          <p>Searching...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="search-error-state">
          <div className="error-icon">⚠️</div>
          <h3>Search Error</h3>
          <p>{getErrorText(error)}</p>
          <button
            className="retry-button"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {!isLoading && !error && searchResults && (
        <SearchResults
          searchData={searchResults}
          onSuggestionClick={handleSuggestionClick}
        />
      )}

      {/* Welcome State (no search yet) */}
      {!isLoading && !error && !searchResults && (
        <div className="search-welcome-state">
          <div className="welcome-content">
            <div className="welcome-icon">🔍</div>
            <h3 className="welcome-title">Start Your Search</h3>
            <p className="welcome-description">
              Try searching for workflows, documentation, commands, or ask a question
            </p>

            <div className="welcome-examples">
              <p className="examples-title">Popular searches:</p>
              <div className="examples-list">
                <button
                  className="example-chip"
                  onClick={() => handleSearch('how to send SMS')}
                >
                  How to send SMS
                </button>
                <button
                  className="example-chip"
                  onClick={() => handleSearch('workflow examples')}
                >
                  Workflow examples
                </button>
                <button
                  className="example-chip"
                  onClick={() => handleSearch('setup calendar')}
                >
                  Setup calendar
                </button>
                <button
                  className="example-chip"
                  onClick={() => handleSearch('appointment reminders')}
                >
                  Appointment reminders
                </button>
              </div>
            </div>

            <div className="welcome-features">
              <div className="feature-item">
                <div className="feature-icon">🎯</div>
                <div className="feature-text">
                  <strong>Intent Detection</strong>
                  <p>Automatically understands your search intent</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">📊</div>
                <div className="feature-text">
                  <strong>Relevance Scoring</strong>
                  <p>Results ranked by 6-factor algorithm</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">⚡</div>
                <div className="feature-text">
                  <strong>Fast Search</strong>
                  <p>Sub-second response times</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedSearchContainer;
