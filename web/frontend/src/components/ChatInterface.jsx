import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { saveAs } from 'file-saver';
import {
  Send,
  Bot,
  User,
  Loader2,
  ChevronDown,
  ChevronUp,
  Download,
  Trash2,
  Copy,
  Check,
  AlertCircle,
  RefreshCw,
  MessageSquare,
  FileText,
  ExternalLink
} from 'lucide-react';
import { apiPost, getErrorMessage } from '../utils/api';
import { OfflineMessage } from './ErrorDisplay';
import './ChatInterface.css';

/**
 * ChatInterface Component - Epic 8: Chat Interface & Message Management
 * Built with BMAD-METHOD
 *
 * Stories Implemented:
 * 8.1: Chat interface with message display
 * 8.2: Markdown rendering for messages
 * 8.3: API integration with search backend
 * 8.4: Expandable source citations
 * 8.5: localStorage conversation persistence
 * 8.6: Export functionality (JSON/Markdown)
 * 8.7: Mobile optimization
 * 8.8: Comprehensive error handling
 */

const ChatInterface = ({
  initialMessage = '',
  onMessageUsed,
  conversationId = null,
  disableLocalStorage = false,
  onAutoSaveMessage = null,
  onFirstMessage = null
}) => {
  // Story 8.1: Message state management
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendOffline, setBackendOffline] = useState(false);

  // Story 8.4: Source citations state
  const [expandedSources, setExpandedSources] = useState({});

  // Story 8.6: Copy feedback state
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Story 8.5: Load conversations from localStorage on mount
  useEffect(() => {
    loadConversationFromStorage();
  }, []);

  // Story 8.5: Save conversations to localStorage when messages change
  useEffect(() => {
    if (messages.length > 0) {
      saveConversationToStorage();
    }
  }, [messages]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Story 9.4: Handle initial message from CommandLibrary
  useEffect(() => {
    if (initialMessage) {
      setInputMessage(initialMessage);
      inputRef.current?.focus();
      if (onMessageUsed) {
        onMessageUsed();
      }
    }
  }, [initialMessage, onMessageUsed]);

  // Story 8.5: localStorage functions (skip if disableLocalStorage is true)
  const loadConversationFromStorage = () => {
    if (disableLocalStorage || conversationId) {
      // Don't load from localStorage if we're using backend storage
      return;
    }

    try {
      const saved = localStorage.getItem('brobro-conversation');
      if (saved) {
        const parsed = JSON.parse(saved);

        // CRITICAL FIX: If conversation is too large (>50MB stored), it's likely corrupted
        // Clear it and start fresh
        if (saved.length > 50000000) {
          console.warn('[CRITICAL] Detected corrupted conversation history (>50MB). Clearing...');
          localStorage.removeItem('brobro-conversation');
          return;
        }

        // Limit to last 20 messages maximum to prevent size explosion
        const limited = Array.isArray(parsed) ? parsed.slice(-20) : [];
        setMessages(limited);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
      // Clear corrupted data
      try {
        localStorage.removeItem('brobro-conversation');
        console.log('Cleared corrupted localStorage data');
      } catch (e) {
        // Silent fail
      }
    }
  };

  const saveConversationToStorage = () => {
    if (disableLocalStorage || conversationId) {
      // Don't save to localStorage if we're using backend storage
      return;
    }

    try {
      // CRITICAL FIX: Limit to maximum 30 messages to prevent storage bloat
      // Keep only the most recent messages
      const recentMessages = messages.slice(-30);

      // Sanitize each message - only save essential fields
      const sanitizedMessages = recentMessages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: typeof msg.content === 'string' ? msg.content : '', // Only text
        timestamp: msg.timestamp,
        isError: msg.isError,
        ...(msg.sources && Array.isArray(msg.sources) && msg.sources.length > 0 && {
          sourcesCount: msg.sources.length // Just store count, not full source data
        })
      }));

      const serialized = JSON.stringify(sanitizedMessages);

      // Check size before saving - abort if > 1MB
      if (serialized.length > 1000000) {
        console.warn('[WARN] Conversation too large for localStorage, truncating to 10 messages');
        const truncated = recentMessages.slice(-10).map(msg => ({
          id: msg.id,
          role: msg.role,
          content: typeof msg.content === 'string' ? msg.content : '',
          timestamp: msg.timestamp
        }));
        localStorage.setItem('brobro-conversation', JSON.stringify(truncated));
      } else {
        localStorage.setItem('brobro-conversation', serialized);
      }
    } catch (err) {
      console.error('Failed to save conversation:', err);
      // Try to clear if it's a quota exceeded error
      if (err.name === 'QuotaExceededError') {
        console.warn('[WARN] localStorage quota exceeded, clearing conversation');
        try {
          localStorage.removeItem('brobro-conversation');
        } catch (e) {
          // Silent fail
        }
      }
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Story 8.3: API Integration - Send message and get response
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);
    setBackendOffline(false);

    // Auto-save user message to backend
    if (conversationId && onAutoSaveMessage) {
      onAutoSaveMessage(conversationId, 'user', userMessage.content);
    } else if (!conversationId && onFirstMessage) {
      // First message - call onFirstMessage to create conversation
      onFirstMessage(conversationId, userMessage.content);
    }

    try {
      // Story 8.3: Call chat API (Claude-powered) using API utility
      // IMPORTANT: Only send role and content, filter out any other fields (images, etc)
      // Use 60 second timeout for chat (Claude API can take 30-45 seconds)
      const result = await apiPost('/api/chat', {
        query: userMessage.content,
        n_results: 5,
        conversation_history: messages
          .filter(m => !m.isError)
          .slice(-6) // Last 3 exchanges for context
          .map(m => ({
            role: m.role,
            content: typeof m.content === 'string' ? m.content : '' // Ensure only text
          }))
          .filter(m => m.content.trim()) // Remove empty messages
      }, 60000); // 60 second timeout for Claude API

      // Story 8.2 & 8.4: Display Claude's answer with sources
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: result.data.answer,
        sources: result.data.sources,
        timestamp: new Date().toISOString(),
        searchTime: result.data.search_time_ms,
        generationTime: result.data.generation_time_ms,
        totalTime: result.data.total_time_ms
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Auto-save assistant message to backend
      if (conversationId && onAutoSaveMessage) {
        const metadata = {
          sources: assistantMessage.sources,
          searchTime: assistantMessage.searchTime,
          generationTime: assistantMessage.generationTime,
          totalTime: assistantMessage.totalTime
        };
        onAutoSaveMessage(conversationId, 'assistant', assistantMessage.content, metadata);
      }

    } catch (err) {
      // Story 8.8: Enhanced error handling with user-friendly messages
      console.error('Chat failed:', err);
      const errorInfo = getErrorMessage(err);
      setError(errorInfo);

      // Show offline message if backend is unreachable
      if (errorInfo.isRetryable && err.isNetworkError) {
        setBackendOffline(true);
      } else {
        // Add error message to chat
        const errorMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `I encountered an error: ${errorInfo.message}. ${errorInfo.suggestion || 'Please try again or rephrase your question.'}`,
          isError: true,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Story 8.2: Format search results as markdown
  const formatSearchResults = (data) => {
    if (!data.results || data.results.length === 0) {
      return "I couldn't find any relevant information for your question. Try rephrasing or asking about a different GHL topic.";
    }

    let markdown = `I found **${data.total_results}** relevant results for your question:\n\n`;

    data.results.forEach((result, index) => {
      const relevancePercent = (result.relevance_score * 100).toFixed(1);
      const sourceType = result.source === 'command' ? '🎯 Command' : '📚 Documentation';

      markdown += `### ${index + 1}. ${result.metadata.title || 'Untitled'}\n\n`;
      markdown += `**Source**: ${sourceType} | **Relevance**: ${relevancePercent}%\n\n`;
      markdown += `${result.content.substring(0, 300)}${result.content.length > 300 ? '...' : ''}\n\n`;

      if (result.metadata.url) {
        markdown += `[View full article →](${result.metadata.url})\n\n`;
      }

      markdown += '---\n\n';
    });

    markdown += `*Search completed in ${data.search_time_ms}ms*`;

    return markdown;
  };

  // Story 8.4: Toggle source expansion
  const toggleSourceExpansion = (messageId) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  // Story 8.6: Export functions
  const handleExportJSON = () => {
    try {
      const exportData = {
        exportDate: new Date().toISOString(),
        messageCount: messages.length,
        messages: messages.map(msg => ({
          ...msg,
          sources: msg.sources ? msg.sources.length : 0
        }))
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      saveAs(blob, `brobro-conversation-${Date.now()}.json`);
    } catch (err) {
      // Story 8.8: Error handling for export
      setError('Failed to export conversation as JSON');
      console.error('Export JSON failed:', err);
    }
  };

  const handleExportMarkdown = () => {
    try {
      let markdown = '# BroBro Conversation Export\n\n';
      markdown += `**Exported**: ${new Date().toLocaleString()}\n\n`;
      markdown += `**Total Messages**: ${messages.length}\n\n`;
      markdown += '---\n\n';

      messages.forEach((msg, index) => {
        const role = msg.role === 'user' ? '👤 You' : '🤖 BroBro';
        const time = new Date(msg.timestamp).toLocaleTimeString();

        markdown += `## ${role} (${time})\n\n`;
        markdown += `${msg.content}\n\n`;

        if (msg.sources && msg.sources.length > 0) {
          markdown += `**Sources**: ${msg.sources.length} documents\n\n`;
        }

        markdown += '---\n\n';
      });

      const blob = new Blob([markdown], { type: 'text/markdown' });
      saveAs(blob, `brobro-conversation-${Date.now()}.md`);
    } catch (err) {
      // Story 8.8: Error handling for export
      setError('Failed to export conversation as Markdown');
      console.error('Export Markdown failed:', err);
    }
  };

  // Story 8.6: Copy message content
  const handleCopyMessage = async (messageId, content) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      // Story 8.8: Error handling for copy
      console.error('Failed to copy:', err);
      setError('Failed to copy message');
    }
  };

  // Clear conversation
  const handleClearConversation = () => {
    if (window.confirm('Are you sure you want to clear the entire conversation? This cannot be undone.')) {
      setMessages([]);
      localStorage.removeItem('brobro-conversation');
      setExpandedSources({});
      setError(null);
    }
  };

  // Story 8.8: Retry failed message
  const handleRetry = () => {
    setError(null);
    setBackendOffline(false);
    if (messages.length > 0) {
      const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
      if (lastUserMessage) {
        setInputMessage(lastUserMessage.content);
        inputRef.current?.focus();
      }
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-title">
          <MessageSquare size={24} />
          <div>
            <h2>Chat with BroBro</h2>
            <p>BroBro</p>
          </div>
        </div>

        <div className="chat-actions">
          {messages.length > 0 && (
            <>
              <button
                className="action-btn"
                onClick={handleExportJSON}
                title="Export as JSON"
              >
                <Download size={18} />
                <span>JSON</span>
              </button>
              <button
                className="action-btn"
                onClick={handleExportMarkdown}
                title="Export as Markdown"
              >
                <FileText size={18} />
                <span>Markdown</span>
              </button>
              <button
                className="action-btn danger"
                onClick={handleClearConversation}
                title="Clear conversation"
              >
                <Trash2 size={18} />
                <span>Clear</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Story 8.8: Backend offline message */}
      {backendOffline && (
        <OfflineMessage onRetry={handleRetry} feature="chat" />
      )}

      {/* Story 8.8: Error banner */}
      {error && !backendOffline && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>
            {typeof error === 'string'
              ? error
              : (error?.title || error?.message || JSON.stringify(error) || 'An error occurred')}
          </span>
          <button onClick={() => setError(null)} className="close-btn">×</button>
          <button onClick={handleRetry} className="retry-btn">
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      )}

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 ? (
          // Empty state
          <div className="empty-state">
            <Bot size={64} />
            <h3>Start a conversation</h3>
            <p>Your Bro for anything Business, GHL, Cannabis and Tissue Culture</p>
            <div className="example-prompts">
              <button onClick={() => setInputMessage('How do I create a lead nurture workflow?')}>
                Create a lead nurture workflow
              </button>
              <button onClick={() => setInputMessage('Show me appointment reminder setup')}>
                Appointment reminder setup
              </button>
              <button onClick={() => setInputMessage('Explain SMS automation best practices')}>
                SMS automation best practices
              </button>
            </div>
          </div>
        ) : (
          // Message list
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-avatar">
                {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>

              <div className="message-content-wrapper">
                <div className="message-header">
                  <span className="message-role">
                    {message.role === 'user' ? 'You' : 'BroBro'}
                  </span>
                  <span className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                  {message.totalTime && (
                    <span className="message-time" title={`Search: ${message.searchTime}ms | Generation: ${message.generationTime}ms`}>
                      • {message.totalTime.toFixed(0)}ms
                    </span>
                  )}
                </div>

                {/* Story 8.2: Markdown rendering */}
                <div className="message-content">
                  {message.role === 'user' ? (
                    <p>{message.content}</p>
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  )}
                </div>

                {/* Story 8.4: Source citations */}
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <button
                      className="sources-toggle"
                      onClick={() => toggleSourceExpansion(message.id)}
                    >
                      <span>{message.sources.length} sources</span>
                      {expandedSources[message.id] ? (
                        <ChevronUp size={16} />
                      ) : (
                        <ChevronDown size={16} />
                      )}
                    </button>

                    {expandedSources[message.id] && (
                      <div className="sources-list">
                        {message.sources.map((source, idx) => (
                          <div key={idx} className="source-item">
                            <div className="source-header">
                              <span className={`source-badge ${source.source}`}>
                                {source.source === 'command' ? '🎯 Command' : '📚 Docs'}
                              </span>
                              <span className="source-relevance">
                                {(source.relevance_score * 100).toFixed(1)}% relevant
                              </span>
                            </div>
                            <h4>{source.metadata.title || 'Untitled'}</h4>
                            <p>{source.content.substring(0, 150)}...</p>
                            {source.metadata.url && (
                              <a
                                href={source.metadata.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="source-link"
                              >
                                View source <ExternalLink size={12} />
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Message actions */}
                {message.role === 'assistant' && !message.isError && (
                  <div className="message-actions">
                    <button
                      className="message-action-btn"
                      onClick={() => handleCopyMessage(message.id, message.content)}
                      title="Copy message"
                    >
                      {copiedMessageId === message.id ? (
                        <>
                          <Check size={14} />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy size={14} />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content-wrapper">
              <div className="loading-dots">
                <Loader2 className="spin" size={20} />
                <span>Analyzing with AI...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="BroBro"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            rows={1}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            title="Send message"
          >
            {isLoading ? (
              <Loader2 className="spin" size={20} />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
        <div className="chat-input-hint">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
