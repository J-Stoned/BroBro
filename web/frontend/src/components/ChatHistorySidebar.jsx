import React, { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight, Plus, Trash2, Edit2, MessageSquare, Pin, Archive, Search, X, Loader, Settings, LogOut, Info, Download, Keyboard } from 'lucide-react';
import * as conversationApi from '../api/conversationApi';
import { getSessionId, clearSessionId } from '../utils/sessionManager';
import { getPreferences, updatePreferences } from '../api/preferencesApi';
import { exportConversations } from '../api/conversationApi';
import { ShortcutsHelp } from './ShortcutsHelp';
import './ChatHistorySidebar.css';

// Elite: Universal navigation function - works in any context
const navigate = (path) => {
  // Try React Router first if available via context
  const routerNav = window.__routerNavigate;
  if (routerNav) {
    routerNav(path);
  } else {
    // Fallback to standard navigation
    window.location.href = path;
  }
};

/**
 * ChatHistorySidebar Component
 *
 * Left sidebar that displays chat conversation history.
 * Features:
 * - Toggle collapse/expand
 * - List conversations sorted by recent
 * - Create new conversation
 * - Resume conversation (load messages)
 * - Rename conversation
 * - Delete conversation with confirmation
 */

const ChatHistorySidebar = ({
  currentConversationId = null,
  onSelectConversation = null,
  onNewConversation = null,
  isCollapsed = false,
  onToggleCollapse = null
}) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [renaming, setRenaming] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [error, setError] = useState(null);
  const [showArchived, setShowArchived] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null); // null = not searching, [] = no results
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const searchTimeoutRef = useRef(null);
  const sessionId = getSessionId();

  // Load conversations on mount and when session or filters change
  useEffect(() => {
    // Clear search when filters change
    setSearchQuery('');
    setSearchResults(null);
    loadConversations();
  }, [sessionId, showArchived]);

  // Debounced search handler
  useEffect(() => {
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // If search is empty, show normal conversations
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }

    // Set timeout for debounced search (300ms)
    searchTimeoutRef.current = setTimeout(() => {
      performSearch();
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const loadConversations = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await conversationApi.listConversations(sessionId, {
        limit: 100,
        offset: 0,
        archived: showArchived
      });
      setConversations(result.conversations || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async () => {
    setSearching(true);
    setError(null);

    try {
      const result = await conversationApi.searchConversations(sessionId, searchQuery, {
        archived: showArchived,
        limit: 50
      });
      setSearchResults(result.conversations || []);
    } catch (err) {
      console.error('Failed to search conversations:', err);
      setError(err.message);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to log out? This will clear your session.')) {
      clearSessionId();
      localStorage.clear();
      window.location.reload();
    }
  };

  const handleExport = async (format) => {
    try {
      await exportConversations(sessionId, format, true);
      setShowExportDialog(false);
      setProfileMenuOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleThemeToggle = async () => {
    try {
      const prefs = await getPreferences(sessionId);
      const newTheme = prefs.theme === 'light' ? 'dark' : 'light';
      await updatePreferences(sessionId, { theme: newTheme });

      // Apply theme to document
      document.documentElement.setAttribute('data-theme', newTheme);

      setProfileMenuOpen(false);
    } catch (error) {
      console.error('Theme toggle failed:', error);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchResults(null);
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await conversationApi.createConversation(sessionId);

      // Add to list
      setConversations(prev => [newConv, ...prev]);

      // Callback to parent
      if (onNewConversation) {
        onNewConversation(newConv);
      }

      // Also select it
      if (onSelectConversation) {
        onSelectConversation(newConv.id);
      }
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError(err.message);
    }
  };

  const handleSelectConversation = (conversationId) => {
    if (onSelectConversation) {
      onSelectConversation(conversationId);
    }
  };

  const handleRenameStart = (conversation) => {
    setRenaming(conversation.id);
    setNewTitle(conversation.title || '');
  };

  const handleRenameSave = async (conversationId) => {
    if (!newTitle.trim()) return;

    try {
      const updated = await conversationApi.renameConversation(conversationId, newTitle.trim());

      // Update in list
      setConversations(prev =>
        prev.map(c => (c.id === conversationId ? { ...c, title: updated.title } : c))
      );

      setRenaming(null);
      setNewTitle('');
    } catch (err) {
      console.error('Failed to rename conversation:', err);
      setError(err.message);
    }
  };

  const handleDelete = async (conversationId, e) => {
    e.stopPropagation();

    const conversation = conversations.find(c => c.id === conversationId);
    if (!window.confirm(`Delete "${conversation?.title || 'Conversation'}"? This cannot be undone.`)) {
      return;
    }

    try {
      await conversationApi.deleteConversation(conversationId);

      // Remove from list
      setConversations(prev => prev.filter(c => c.id !== conversationId));
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError(err.message);
    }
  };

  const handleTogglePin = async (conversationId, e) => {
    e.stopPropagation();

    const conversation = conversations.find(c => c.id === conversationId);
    const newPinnedStatus = !conversation?.pinned;

    try {
      const updated = await conversationApi.updateConversation(conversationId, {
        pinned: newPinnedStatus
      });

      // Update in list - will resort due to dependency change
      setConversations(prev =>
        prev.map(c => (c.id === conversationId ? { ...c, pinned: updated.pinned } : c))
      );
    } catch (err) {
      console.error('Failed to update pin status:', err);
      setError(err.message);
    }
  };

  const handleToggleArchive = async (conversationId, e) => {
    e.stopPropagation();

    const conversation = conversations.find(c => c.id === conversationId);
    const newArchivedStatus = !conversation?.archived;

    try {
      const updated = await conversationApi.updateConversation(conversationId, {
        archived: newArchivedStatus
      });

      // Remove from list (will be filtered out unless showing archived)
      if (!showArchived) {
        setConversations(prev => prev.filter(c => c.id !== conversationId));
      } else {
        setConversations(prev =>
          prev.map(c => (c.id === conversationId ? { ...c, archived: updated.archived } : c))
        );
      }
    } catch (err) {
      console.error('Failed to update archive status:', err);
      setError(err.message);
    }
  };

  const formatTimestamp = (isoString) => {
    if (!isoString) return '';

    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  if (isCollapsed) {
    return (
      <div className="chat-history-sidebar collapsed">
        <button
          className="collapse-toggle"
          onClick={onToggleCollapse}
          title="Show chat history"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    );
  }

  return (
    <div className="chat-history-sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="header-content">
          <div className="header-title">
            <MessageSquare size={18} className="header-icon" />
            <h2>Chat History</h2>
          </div>
        </div>
        <button
          className="collapse-toggle"
          onClick={onToggleCollapse}
          title="Hide chat history"
        >
          <ChevronLeft size={18} />
        </button>
      </div>

      {/* Controls Bar */}
      <div className="sidebar-controls">
        {/* New Chat Button */}
        <button
          className="new-chat-btn"
          onClick={handleNewConversation}
          disabled={loading}
          title="Start a new conversation"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="search-bar-container">
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            title="Search messages in conversations"
          />
          {searchQuery && (
            <button
              className="search-clear-btn"
              onClick={handleClearSearch}
              title="Clear search"
            >
              <X size={16} />
            </button>
          )}
          {searching && (
            <Loader size={16} className="search-spinner" />
          )}
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        {/* Show Archived Toggle */}
        <button
          className={`archive-toggle ${showArchived ? 'active' : ''}`}
          onClick={() => setShowArchived(!showArchived)}
          title={showArchived ? 'Hide archived' : 'Show archived'}
        >
          <Archive size={14} />
          <span>{showArchived ? 'Archived' : 'Active'}</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)} className="dismiss-error">×</button>
        </div>
      )}

      {/* Conversations List */}
      <div className="conversations-list">
        {/* Show search results if searching */}
        {searchResults !== null ? (
          <>
            {searching ? (
              <div className="empty-state">
                <Loader size={32} className="empty-icon" />
                <p>Searching...</p>
              </div>
            ) : searchResults.length === 0 ? (
              <div className="empty-state">
                <MessageSquare size={32} className="empty-icon" />
                <p>No results found</p>
                <span className="empty-help">Try a different search term</span>
              </div>
            ) : (
              <>
                <div className="search-status">
                  Found {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
                </div>
                {searchResults.map(conversation => (
            <div
              key={conversation.id}
              className={`conversation-item ${currentConversationId === conversation.id ? 'active' : ''}`}
              onClick={() => handleSelectConversation(conversation.id)}
            >
              <div className="conversation-content">
                {renaming === conversation.id ? (
                  <input
                    autoFocus
                    type="text"
                    className="rename-input"
                    value={newTitle}
                    onChange={e => setNewTitle(e.target.value)}
                    onClick={e => e.stopPropagation()}
                    onBlur={() => handleRenameSave(conversation.id)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        handleRenameSave(conversation.id);
                      } else if (e.key === 'Escape') {
                        setRenaming(null);
                        setNewTitle('');
                      }
                    }}
                  />
                ) : (
                  <>
                    <h3 className="conversation-title">
                      {conversation.title || 'Untitled Conversation'}
                    </h3>
                    <p className="conversation-timestamp">
                      {formatTimestamp(conversation.updated_at)}
                    </p>
                  </>
                )}
              </div>

              {/* Action Buttons */}
              {renaming !== conversation.id && (
                <div className="conversation-actions">
                  <button
                    className={`action-btn pin-btn ${conversation.pinned ? 'active' : ''}`}
                    onClick={e => handleTogglePin(conversation.id, e)}
                    title={conversation.pinned ? 'Unpin conversation' : 'Pin conversation'}
                  >
                    <Pin size={14} />
                  </button>
                  <button
                    className="action-btn archive-btn"
                    onClick={e => handleToggleArchive(conversation.id, e)}
                    title={conversation.archived ? 'Restore conversation' : 'Archive conversation'}
                  >
                    <Archive size={14} />
                  </button>
                  <button
                    className="action-btn rename-btn"
                    onClick={e => {
                      e.stopPropagation();
                      handleRenameStart(conversation);
                    }}
                    title="Rename conversation"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={e => handleDelete(conversation.id, e)}
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </div>
                ))}
              </>
            )}
          </>
        ) : (
          <>
            {loading && conversations.length === 0 ? (
              <div className="empty-state">
                <MessageSquare size={32} className="empty-icon" />
                <p>Loading conversations...</p>
              </div>
            ) : conversations.length === 0 ? (
              <div className="empty-state">
                <MessageSquare size={32} className="empty-icon" />
                <p>No conversations yet</p>
                <span className="empty-help">Click "New Chat" to get started</span>
              </div>
            ) : (
              conversations.map(conversation => (
            <div
              key={conversation.id}
              className={`conversation-item ${currentConversationId === conversation.id ? 'active' : ''}`}
              onClick={() => handleSelectConversation(conversation.id)}
            >
              {/* Backend Badge */}
              <span
                className={`backend-badge ${conversation.backend_type || 'claude'}`}
                title={conversation.backend_type || 'claude'}
              />

              <div className="conversation-content">
                {renaming === conversation.id ? (
                  <input
                    autoFocus
                    type="text"
                    className="rename-input"
                    value={newTitle}
                    onChange={e => setNewTitle(e.target.value)}
                    onClick={e => e.stopPropagation()}
                    onBlur={() => handleRenameSave(conversation.id)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        handleRenameSave(conversation.id);
                      } else if (e.key === 'Escape') {
                        setRenaming(null);
                        setNewTitle('');
                      }
                    }}
                  />
                ) : (
                  <>
                    <h3 className="conversation-title">
                      {conversation.title || 'Untitled Conversation'}
                    </h3>
                    <p className="conversation-timestamp">
                      {formatTimestamp(conversation.updated_at)}
                    </p>
                  </>
                )}
              </div>

              {/* Action Buttons */}
              {renaming !== conversation.id && (
                <div className="conversation-actions">
                  <button
                    className={`action-btn pin-btn ${conversation.pinned ? 'active' : ''}`}
                    onClick={e => handleTogglePin(conversation.id, e)}
                    title={conversation.pinned ? 'Unpin conversation' : 'Pin conversation'}
                  >
                    <Pin size={14} />
                  </button>
                  <button
                    className="action-btn archive-btn"
                    onClick={e => handleToggleArchive(conversation.id, e)}
                    title={conversation.archived ? 'Restore conversation' : 'Archive conversation'}
                  >
                    <Archive size={14} />
                  </button>
                  <button
                    className="action-btn rename-btn"
                    onClick={e => {
                      e.stopPropagation();
                      handleRenameStart(conversation);
                    }}
                    title="Rename conversation"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={e => handleDelete(conversation.id, e)}
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </div>
              ))
            )}
          </>
        )}
      </div>

      {/* Profile Menu Footer */}
      <div className="sidebar-footer">
        <div
          className="profile-banner"
          onClick={() => setProfileMenuOpen(!profileMenuOpen)}
        >
          <div className="profile-avatar">
            {sessionId?.substring(0, 2).toUpperCase() || 'US'}
          </div>
          <div className="profile-info">
            <div className="profile-name">User</div>
            <div className="profile-session">Session Active</div>
          </div>
          <div className={`profile-menu-icon ${profileMenuOpen ? 'open' : ''}`}>
            ▲
          </div>
        </div>

        {profileMenuOpen && (
          <div className="profile-menu">
            <button
              className="profile-menu-item"
              onClick={() => {
                setShowShortcuts(true);
                setProfileMenuOpen(false);
              }}
            >
              <Keyboard size={18} />
              <span>Keyboard Shortcuts</span>
            </button>

            <button
              className="profile-menu-item"
              onClick={() => {
                navigate('/settings');
                setProfileMenuOpen(false);
              }}
            >
              <Settings size={18} />
              <span>Settings</span>
            </button>

            <button
              className="profile-menu-item"
              onClick={handleThemeToggle}
            >
              <span className="menu-icon">🌓</span>
              <span>Toggle Theme</span>
            </button>

            <button
              className="profile-menu-item"
              onClick={() => setShowExportDialog(!showExportDialog)}
            >
              <Download size={18} />
              <span>Export Data</span>
            </button>

            {showExportDialog && (
              <div className="export-submenu">
                <button onClick={() => handleExport('json')}>
                  Export as JSON
                </button>
                <button onClick={() => handleExport('markdown')}>
                  Export as Markdown
                </button>
              </div>
            )}

            <button
              className="profile-menu-item"
              onClick={() => {
                setShowAbout(true);
                setProfileMenuOpen(false);
              }}
            >
              <Info size={18} />
              <span>About BroBro</span>
            </button>

            <button
              className="profile-menu-item logout"
              onClick={handleLogout}
            >
              <LogOut size={18} />
              <span>Log Out</span>
            </button>
          </div>
        )}
      </div>

      {/* Modals */}
      {showShortcuts && (
        <ShortcutsHelp
          isOpen={showShortcuts}
          onClose={() => setShowShortcuts(false)}
        />
      )}

      {showAbout && (
        <div
          className="modal-overlay"
          onClick={() => setShowAbout(false)}
        >
          <div
            className="modal-content"
            onClick={e => e.stopPropagation()}
          >
            <h2>About BroBro</h2>
            <p><strong>Version:</strong> 2.0.0</p>
            <p>
              <strong>Description:</strong> Your Bro for anything Business, GHL, Cannabis and Tissue Culture
            </p>
            <p><strong>Powered by:</strong></p>
            <ul>
              <li>Anthropic Claude</li>
              <li>Google Gemini File Search</li>
            </ul>
            <button onClick={() => setShowAbout(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistorySidebar;
