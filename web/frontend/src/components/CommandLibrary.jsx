import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  Search,
  Filter,
  Star,
  Clock,
  ChevronRight,
  X,
  Copy,
  Check,
  MessageSquare,
  AlertCircle,
  RefreshCw,
  Loader2,
  ExternalLink,
  Grid,
  List,
  Heart,
  Bookmark
} from 'lucide-react';
import { apiGet, apiPost, getErrorMessage, APIError } from '../utils/api';
import { OfflineMessage } from './ErrorDisplay';
import './CommandLibrary.css';

/**
 * CommandLibrary Component - Epic 9: Command Library Browser
 * Built with BMAD-METHOD
 *
 * Stories Implemented:
 * 9.1: Command library UI with grid layout
 * 9.2: Command details modal
 * 9.3: Search and filter functionality
 * 9.4: Chat integration (use in chat)
 * 9.5: Favorites system with localStorage
 * 9.6: Recently viewed tracking
 * 9.7: Backend search integration
 * 9.8: Mobile optimization
 * 9.9: Comprehensive error handling
 */

const CommandLibrary = ({ onUseInChat }) => {
  // Story 9.1: State for commands and UI
  const [commands, setCommands] = useState([]);
  const [filteredCommands, setFilteredCommands] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  // Story 9.2: Modal state
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Story 9.3: Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all'); // all, favorites, recent
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [categories, setCategories] = useState([]);

  // Story 9.5: Favorites state
  const [favorites, setFavorites] = useState([]);

  // Story 9.6: Recently viewed state
  const [recentlyViewed, setRecentlyViewed] = useState([]);

  // Story 9.4: Copy feedback
  const [copiedId, setCopiedId] = useState(null);
  const [copiedType, setCopiedType] = useState(null); // 'purpose', 'content', 'command'
  const [showFullContent, setShowFullContent] = useState(false);

  const searchInputRef = useRef(null);

  // Story 9.5 & 9.6: Load favorites and recently viewed from localStorage
  useEffect(() => {
    loadFavorites();
    loadRecentlyViewed();
  }, []);

  // Story 9.7: Load commands from backend on mount
  useEffect(() => {
    loadCommands();
  }, []);

  // Story 9.3: Filter commands when search/filters change
  useEffect(() => {
    filterCommands();
  }, [commands, searchQuery, activeFilter, categoryFilter, favorites, recentlyViewed]);

  // Story 9.7: Load commands from backend via Gemini File Search
  const loadCommands = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Note: /api/commands/all is deprecated (ChromaDB removed)
      // Use /api/gemini/query or /api/search/unified for command searches
      // For now, show a helpful message and disable bulk command loading

      setError({
        title: 'Command Library Updated',
        message: 'Commands are now powered by Gemini File Search. Use the Chat interface to search for specific commands, or search via /api/gemini/query endpoint.',
        suggestion: 'Try using the Chat interface or /api/search/unified for command searches.'
      });

      setCommands([]);
      setCategories([]);

    } catch (err) {
      // Story 9.9: Enhanced error handling
      console.error('Failed to load commands:', err);
      const errorInfo = getErrorMessage(err);
      setError(errorInfo);
    } finally {
      setIsLoading(false);
    }
  };

  // Process and deduplicate commands
  const processCommands = (results) => {
    const commandMap = new Map();

    // Helper: Extract title from content
    const extractTitle = (content, command) => {
      if (command && command.trim()) return command;

      // Try to find markdown heading
      const headingMatch = content?.match(/^#\s+(.+)$/m);
      if (headingMatch) return headingMatch[1].trim();

      // Try to find title in first line
      const firstLine = content?.split('\n')[0]?.trim();
      if (firstLine && firstLine.length < 100) {
        return firstLine.replace(/^[#*\-]+\s*/, '').trim();
      }

      // Fallback: first 60 chars
      return content?.substring(0, 60)?.trim() || 'Documentation';
    };

    // Helper: Extract description from content
    const extractDescription = (purpose, content) => {
      if (purpose && purpose.trim()) return purpose;

      // Find first paragraph (skip headers)
      const lines = content?.split('\n') || [];
      for (let line of lines) {
        const cleaned = line.trim();
        if (cleaned &&
            !cleaned.startsWith('#') &&
            !cleaned.startsWith('*') &&
            !cleaned.startsWith('-') &&
            cleaned.length > 50) {
          return cleaned.substring(0, 150) + (cleaned.length > 150 ? '...' : '');
        }
      }

      // Fallback: first 150 chars
      return content?.substring(0, 150)?.trim() || 'No description available';
    };

    results.forEach(result => {
      // Extract better title and description
      const title = extractTitle(result.content, result.command);
      const description = extractDescription(result.purpose, result.content);
      const cmdId = result.id || `cmd-${title.toLowerCase().replace(/\s+/g, '-')}`;

      if (!commandMap.has(cmdId)) {
        commandMap.set(cmdId, {
          id: cmdId,
          title,
          description,
          content: result.content || '',
          category: result.category || 'General',
          url: '',
          relevance: 1.0,
          metadata: {
            command: result.command,
            category: result.category,
            purpose: result.purpose,
            tags: result.tags || [],
            source: result.source
          }
        });
      }
    });

    return Array.from(commandMap.values());
  };

  // Story 9.3: Filter commands based on search and filters
  const filterCommands = () => {
    let filtered = [...commands];

    // Apply active filter (all, favorites, recent)
    if (activeFilter === 'favorites') {
      filtered = filtered.filter(cmd => favorites.includes(cmd.id));
    } else if (activeFilter === 'recent') {
      filtered = recentlyViewed
        .map(id => commands.find(cmd => cmd.id === id))
        .filter(Boolean);
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(cmd => cmd.category === categoryFilter);
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(cmd =>
        cmd.title.toLowerCase().includes(query) ||
        cmd.description.toLowerCase().includes(query) ||
        cmd.category.toLowerCase().includes(query)
      );
    }

    setFilteredCommands(filtered);
  };

  // Story 9.5: Favorites management
  const loadFavorites = () => {
    try {
      const saved = localStorage.getItem('brobro-favorites');
      if (saved) {
        setFavorites(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Failed to load favorites:', err);
    }
  };

  const saveFavorites = (newFavorites) => {
    try {
      localStorage.setItem('brobro-favorites', JSON.stringify(newFavorites));
      setFavorites(newFavorites);
    } catch (err) {
      console.error('Failed to save favorites:', err);
    }
  };

  const toggleFavorite = (commandId) => {
    const newFavorites = favorites.includes(commandId)
      ? favorites.filter(id => id !== commandId)
      : [...favorites, commandId];
    saveFavorites(newFavorites);
  };

  // Story 9.6: Recently viewed management
  const loadRecentlyViewed = () => {
    try {
      const saved = localStorage.getItem('brobro-recent-commands');
      if (saved) {
        setRecentlyViewed(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Failed to load recently viewed:', err);
    }
  };

  const saveRecentlyViewed = (newRecent) => {
    try {
      localStorage.setItem('brobro-recent-commands', JSON.stringify(newRecent));
      setRecentlyViewed(newRecent);
    } catch (err) {
      console.error('Failed to save recently viewed:', err);
    }
  };

  const addToRecentlyViewed = (commandId) => {
    const newRecent = [commandId, ...recentlyViewed.filter(id => id !== commandId)].slice(0, 20);
    saveRecentlyViewed(newRecent);
  };

  // Story 9.2: Open command details modal
  const openCommandModal = (command) => {
    setSelectedCommand(command);
    setShowModal(true);
    addToRecentlyViewed(command.id);
  };

  // Close modal
  const closeModal = () => {
    setShowModal(false);
    setTimeout(() => setSelectedCommand(null), 300);
  };

  // Story 9.4: Use command in chat
  const handleUseInChat = (command) => {
    if (onUseInChat) {
      onUseInChat(command.title);
    }
    closeModal();
  };

  // Copy command to clipboard
  const handleCopy = async (text, id, type = 'default') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setCopiedType(type);
      setTimeout(() => {
        setCopiedId(null);
        setCopiedType(null);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Story 9.9: Retry loading commands
  const handleRetry = () => {
    loadCommands();
  };

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
    searchInputRef.current?.focus();
  };

  return (
    <div className="command-library">
      {/* Header */}
      <div className="library-header">
        <div className="header-title">
          <BookOpen size={28} />
          <div>
            <h2>Command Library</h2>
            <p>{filteredCommands.length} commands available</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            className={`view-mode-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
            title="Grid view"
          >
            <Grid size={20} />
          </button>
          <button
            className={`view-mode-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            <List size={20} />
          </button>
        </div>
      </div>

      {/* Story 9.9: Enhanced error display */}
      {error && error.isRetryable && (
        <OfflineMessage onRetry={handleRetry} feature="commands" />
      )}

      {/* Story 9.3: Search and Filters */}
      <div className="library-controls">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search commands..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button onClick={clearSearch} className="clear-search-btn">
              <X size={16} />
            </button>
          )}
        </div>

        <div className="filter-tabs">
          <button
            className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setActiveFilter('all')}
          >
            <BookOpen size={16} />
            <span>All Commands</span>
          </button>
          <button
            className={`filter-tab ${activeFilter === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveFilter('favorites')}
          >
            <Star size={16} />
            <span>Favorites ({favorites.length})</span>
          </button>
          <button
            className={`filter-tab ${activeFilter === 'recent' ? 'active' : ''}`}
            onClick={() => setActiveFilter('recent')}
          >
            <Clock size={16} />
            <span>Recently Viewed</span>
          </button>
        </div>

        {categories.length > 0 && (
          <div className="category-filter">
            <Filter size={16} />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="category-select"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Story 9.1: Commands Grid/List */}
      <div className="library-content">
        {isLoading ? (
          <div className="loading-state">
            <Loader2 className="spin" size={48} />
            <p>Loading commands...</p>
          </div>
        ) : filteredCommands.length === 0 ? (
          <div className="empty-state">
            <BookOpen size={64} />
            <h3>No commands found</h3>
            <p>
              {searchQuery
                ? 'Try adjusting your search or filters'
                : activeFilter === 'favorites'
                ? 'No favorites yet. Click the star icon to add favorites!'
                : 'No commands available'}
            </p>
            {(searchQuery || activeFilter !== 'all') && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setActiveFilter('all');
                  setCategoryFilter('all');
                }}
                className="reset-btn"
              >
                Reset Filters
              </button>
            )}
          </div>
        ) : (
          <div className={`commands-${viewMode}`}>
            {filteredCommands.map((command) => (
              <div
                key={command.id}
                className="command-card"
                onClick={() => openCommandModal(command)}
              >
                <div className="card-header">
                  <h3>{command.title}</h3>
                  <button
                    className={`favorite-btn ${favorites.includes(command.id) ? 'active' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(command.id);
                    }}
                    title={favorites.includes(command.id) ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    <Star size={18} fill={favorites.includes(command.id) ? 'currentColor' : 'none'} />
                  </button>
                </div>

                <p className="card-description">{command.description}</p>

                {command.metadata?.tags && command.metadata.tags.length > 0 && (
                  <div className="card-tags">
                    {command.metadata.tags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="tag-badge">{tag}</span>
                    ))}
                  </div>
                )}

                <div className="card-footer">
                  <span className="card-category">{command.category}</span>
                  <ChevronRight size={16} className="card-arrow" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Story 9.2: Command Details Modal */}
      {showModal && selectedCommand && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <h2>{selectedCommand.title}</h2>
                <span className="modal-category">{selectedCommand.category}</span>
              </div>
              <div className="modal-actions">
                <button
                  className={`favorite-btn ${favorites.includes(selectedCommand.id) ? 'active' : ''}`}
                  onClick={() => toggleFavorite(selectedCommand.id)}
                  title={favorites.includes(selectedCommand.id) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  <Star size={20} fill={favorites.includes(selectedCommand.id) ? 'currentColor' : 'none'} />
                </button>
                <button onClick={closeModal} className="close-btn" title="Close">
                  <X size={24} />
                </button>
              </div>
            </div>

            <div className="modal-body">
              {/* Purpose Section */}
              {selectedCommand.metadata?.purpose && (
                <div className="modal-section">
                  <h3 className="section-title">Purpose</h3>
                  <p className="purpose-text">{selectedCommand.metadata.purpose}</p>
                </div>
              )}

              {/* Tags Section */}
              {selectedCommand.metadata?.tags && selectedCommand.metadata.tags.length > 0 && (
                <div className="modal-section">
                  <h3 className="section-title">Tags</h3>
                  <div className="modal-tags">
                    {selectedCommand.metadata.tags.map((tag, idx) => (
                      <span key={idx} className="tag-badge large">{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Command Section (if it's a slash command) */}
              {selectedCommand.metadata?.command && selectedCommand.metadata.command.trim() && (
                <>
                  <div className="modal-section">
                    <h3 className="section-title">How to Use This Command</h3>
                    <div className="instructions-box">
                      <p className="instruction-text">
                        This is a <strong>BroBro command</strong> that generates GoHighLevel workflows using AI and the embedded knowledge base.
                      </p>
                      <ol className="instruction-steps">
                        <li>Copy the command below</li>
                        <li>Open the <strong>Claude Code chat window</strong> (or BroBro Chat)</li>
                        <li>Paste the command and describe what you want to create</li>
                        <li>Claude will search the knowledge base and generate workflow options</li>
                        <li>Choose your preferred variation and deploy to GoHighLevel</li>
                      </ol>
                      <p className="instruction-note">
                        <strong>Note:</strong> These commands work in BroBro, not directly in GoHighLevel. They generate configurations that you then deploy to your GHL account.
                      </p>
                    </div>
                  </div>

                  <div className="modal-section">
                    <h3 className="section-title">Command</h3>
                    <div className="command-display">
                      <code>{selectedCommand.metadata.command}</code>
                      <button
                        className="copy-icon-btn"
                        onClick={() => handleCopy(selectedCommand.metadata.command, selectedCommand.id, 'command')}
                        title="Copy command"
                      >
                        {copiedId === selectedCommand.id && copiedType === 'command' ? (
                          <Check size={16} />
                        ) : (
                          <Copy size={16} />
                        )}
                      </button>
                    </div>
                  </div>
                </>
              )}

              {/* Details Section */}
              <div className="modal-section">
                <h3 className="section-title">Details</h3>
                <div className="content-preview">
                  <p className={showFullContent ? '' : 'content-truncated'}>
                    {showFullContent
                      ? selectedCommand.content
                      : selectedCommand.content?.substring(0, 500) + (selectedCommand.content?.length > 500 ? '...' : '')}
                  </p>
                  {selectedCommand.content?.length > 500 && (
                    <button
                      className="show-more-btn"
                      onClick={() => setShowFullContent(!showFullContent)}
                    >
                      {showFullContent ? 'Show Less' : 'Show More'}
                    </button>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="modal-footer-actions">
                {selectedCommand.metadata?.command && selectedCommand.metadata.command.trim() ? (
                  <>
                    <button
                      className="action-btn primary"
                      onClick={() => handleUseInChat(selectedCommand)}
                    >
                      <MessageSquare size={18} />
                      <span>Use in BroBro Chat</span>
                    </button>
                    <button
                      className="action-btn"
                      onClick={() => handleCopy(selectedCommand.metadata.command, selectedCommand.id, 'command')}
                    >
                      {copiedId === selectedCommand.id && copiedType === 'command' ? (
                        <>
                          <Check size={18} />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy size={18} />
                          <span>Copy Command</span>
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  <button
                    className="action-btn primary"
                    onClick={() => handleUseInChat(selectedCommand)}
                  >
                    <Search size={18} />
                    <span>Search for This Topic</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommandLibrary;
