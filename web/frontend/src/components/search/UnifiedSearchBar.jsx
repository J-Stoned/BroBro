/**
 * UnifiedSearchBar Component
 * Built with BMAD-METHOD for Epic US: Unified Search
 *
 * Features:
 * - Keyboard shortcut (Cmd/Ctrl + K)
 * - Recent searches (localStorage)
 * - Real-time search with debouncing
 * - Loading states
 * - Intent detection display
 */

import React, { useState, useEffect, useRef } from 'react';
import './UnifiedSearch.css';

const UnifiedSearchBar = ({ onSearch, onClose }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [showRecent, setShowRecent] = useState(false);
  const inputRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('brobro-recent-searches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load recent searches:', e);
      }
    }
  }, []);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Keyboard shortcut listener (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K to focus search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }

      // Escape to close
      if (e.key === 'Escape') {
        if (query) {
          setQuery('');
        } else if (onClose) {
          onClose();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [query, onClose]);

  // Save search to recent searches
  const saveToRecent = (searchQuery) => {
    if (!searchQuery.trim()) return;

    const updated = [
      searchQuery,
      ...recentSearches.filter(s => s !== searchQuery)
    ].slice(0, 10); // Keep last 10 searches

    setRecentSearches(updated);
    localStorage.setItem('brobro-recent-searches', JSON.stringify(updated));
  };

  // Handle search with debouncing
  const handleSearch = (searchQuery) => {
    if (!searchQuery.trim()) {
      setIsSearching(false);
      return;
    }

    setIsSearching(true);

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Debounce search by 300ms
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        saveToRecent(searchQuery);
        await onSearch(searchQuery);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setIsSearching(false);
      }
    }, 300);
  };

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setShowRecent(false);
    handleSearch(value);
  };

  // Handle recent search click
  const handleRecentClick = (searchQuery) => {
    setQuery(searchQuery);
    setShowRecent(false);
    handleSearch(searchQuery);
  };

  // Handle input focus
  const handleFocus = () => {
    if (!query && recentSearches.length > 0) {
      setShowRecent(true);
    }
  };

  // Clear recent searches
  const clearRecent = () => {
    setRecentSearches([]);
    localStorage.removeItem('brobro-recent-searches');
    setShowRecent(false);
  };

  return (
    <div className="unified-search-bar">
      <div className="search-input-container">
        <div className="search-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder="Search for workflows, docs, commands... (⌘K)"
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          autoComplete="off"
        />

        {isSearching && (
          <div className="search-loading">
            <div className="spinner"></div>
          </div>
        )}

        {query && !isSearching && (
          <button
            className="clear-button"
            onClick={() => {
              setQuery('');
              setShowRecent(false);
              if (inputRef.current) {
                inputRef.current.focus();
              }
            }}
            aria-label="Clear search"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M12 4L4 12M4 4l8 8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Recent Searches Dropdown */}
      {showRecent && recentSearches.length > 0 && (
        <div className="recent-searches-dropdown">
          <div className="recent-header">
            <span className="recent-title">Recent Searches</span>
            <button
              className="clear-recent-btn"
              onClick={clearRecent}
            >
              Clear
            </button>
          </div>
          <div className="recent-list">
            {recentSearches.map((search, index) => (
              <button
                key={index}
                className="recent-item"
                onClick={() => handleRecentClick(search)}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="recent-icon">
                  <path
                    d="M8 14A6 6 0 1 0 8 2a6 6 0 0 0 0 12z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M8 4v4l2 2"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                </svg>
                <span className="recent-text">{search}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Tips */}
      {!query && !showRecent && (
        <div className="search-tips">
          <div className="tip">
            <span className="tip-icon">💡</span>
            <span className="tip-text">Try: "how to send SMS", "workflow examples", or "setup calendar"</span>
          </div>
          <div className="tip">
            <span className="tip-icon">⚡</span>
            <span className="tip-text">Press <kbd>Cmd/Ctrl</kbd> + <kbd>K</kbd> to focus search</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedSearchBar;
