import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Plus, Trash2, Edit2, MessageSquare } from 'lucide-react';
import * as conversationApi from '../api/conversationApi';
import { getSessionId } from '../utils/sessionManager';
import './ChatHistorySidebar.css';

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
  const sessionId = getSessionId();

  // Load conversations on mount and when session changes
  useEffect(() => {
    loadConversations();
  }, [sessionId]);

  const loadConversations = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await conversationApi.listConversations(sessionId, {
        limit: 100,
        offset: 0,
        archived: false
      });
      setConversations(result.conversations || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
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

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)} className="dismiss-error">×</button>
        </div>
      )}

      {/* Conversations List */}
      <div className="conversations-list">
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
      </div>
    </div>
  );
};

export default ChatHistorySidebar;
