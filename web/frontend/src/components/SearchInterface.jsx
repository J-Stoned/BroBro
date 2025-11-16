import React, { useState } from 'react';
import { Search, Loader2, FileText, BookOpen, ExternalLink, Clock } from 'lucide-react';
import { apiPost, getErrorMessage } from '../utils/api';
import { OfflineMessage } from './ErrorDisplay';
import './SearchInterface.css';

function SearchInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [collectionFilter, setCollectionFilter] = useState('both');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await apiPost('/api/search', {
        query: query.trim(),
        n_results: 10,
        collection_filter: collectionFilter,
        include_metadata: true
      });

      setResults(result.data);
    } catch (err) {
      console.error('Search failed:', err);
      const errorInfo = getErrorMessage(err);
      setError(errorInfo);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    if (query.trim()) {
      handleSearch({ preventDefault: () => {} });
    }
  };

  const getSourceIcon = (source) => {
    return source === 'command' ? <FileText size={16} /> : <BookOpen size={16} />;
  };

  const getSourceBadge = (source) => {
    return source === 'command' ? 'COMMAND' : 'DOCS';
  };

  const getSourceColor = (source) => {
    return source === 'command' ? '#667eea' : '#10b981';
  };

  return (
    <div className="search-interface">
      <div className="search-container">
        <div className="search-header">
          <h2>Search GHL Knowledge Base</h2>
          <p>1,235+ searchable documents from commands and official documentation</p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              className="search-input"
              placeholder="Ask anything about GoHighLevel..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            {loading && <Loader2 className="loading-icon" size={20} />}
          </div>

          <div className="search-filters">
            <label className="filter-label">Search in:</label>
            <div className="filter-buttons">
              <button
                type="button"
                className={`filter-btn ${collectionFilter === 'both' ? 'active' : ''}`}
                onClick={() => setCollectionFilter('both')}
              >
                Both
              </button>
              <button
                type="button"
                className={`filter-btn ${collectionFilter === 'commands' ? 'active' : ''}`}
                onClick={() => setCollectionFilter('commands')}
              >
                Commands
              </button>
              <button
                type="button"
                className={`filter-btn ${collectionFilter === 'docs' ? 'active' : ''}`}
                onClick={() => setCollectionFilter('docs')}
              >
                Documentation
              </button>
            </div>
          </div>

          <button type="submit" className="search-button" disabled={loading || !query.trim()}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" />
                Searching...
              </>
            ) : (
              <>
                <Search size={18} />
                Search
              </>
            )}
          </button>
        </form>

        {/* Error Message */}
        {error && error.isRetryable && (
          <OfflineMessage onRetry={handleRetry} feature="search" />
        )}

        {error && !error.isRetryable && (
          <div className="error-message">
            <p>{error.title}: {error.message}</p>
            {error.suggestion && <p className="error-suggestion">{error.suggestion}</p>}
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="results-section">
            <div className="results-header">
              <h3>
                {results.total_results} Results for "{results.query}"
              </h3>
              <div className="results-meta">
                <Clock size={14} />
                <span>{results.search_time_ms}ms</span>
              </div>
            </div>

            <div className="results-list">
              {results.results.map((result, index) => (
                <div key={index} className="result-card">
                  <div className="result-header">
                    <div className="result-source-badge" style={{ backgroundColor: getSourceColor(result.source) }}>
                      {getSourceIcon(result.source)}
                      <span>{getSourceBadge(result.source)}</span>
                    </div>
                    <div className="result-score">
                      {(result.relevance_score * 100).toFixed(1)}% relevant
                    </div>
                  </div>

                  <h4 className="result-title">
                    {result.metadata.title || result.metadata.documentTitle || 'Untitled'}
                  </h4>

                  <p className="result-content">
                    {result.content.substring(0, 300)}
                    {result.content.length > 300 && '...'}
                  </p>

                  {result.metadata.url && (
                    <a
                      href={result.metadata.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="result-link"
                    >
                      <span>View source</span>
                      <ExternalLink size={14} />
                    </a>
                  )}

                  {result.metadata.category && (
                    <div className="result-meta">
                      <span className="meta-tag">{result.metadata.category}</span>
                      {result.metadata.wordCount && (
                        <span className="meta-info">{result.metadata.wordCount} words</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!results && !error && !loading && (
          <div className="empty-state">
            <Search size={48} />
            <h3>Start searching</h3>
            <p>Enter a query to search across 1,235+ GHL documents</p>
            <div className="example-queries">
              <p>Try these examples:</p>
              <div className="example-chips">
                <button onClick={() => setQuery('create a lead nurture workflow')} className="example-chip">
                  Create a lead nurture workflow
                </button>
                <button onClick={() => setQuery('appointment reminders')} className="example-chip">
                  Appointment reminders
                </button>
                <button onClick={() => setQuery('SMS automation setup')} className="example-chip">
                  SMS automation setup
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SearchInterface;
