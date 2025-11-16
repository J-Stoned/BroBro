import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Bot,
  User,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { apiPost, getErrorMessage, getErrorText } from '../utils/api';
import { OfflineMessage } from './ErrorDisplay';
import './GeminiChatInterface.css';

/**
 * GeminiChatInterface Component - Simplified Chat Layout
 * Single conversation view with large message bubbles and bottom search input
 */

const GeminiChatInterface = ({ initialMessage = '', onMessageUsed, onBackendChange, chatBackend = 'gemini' }) => {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendOffline, setBackendOffline] = useState(false);
  const [tokenCount, setTokenCount] = useState(0);
  const [isCompacting, setIsCompacting] = useState(false);
  const [compactionInfo, setCompactionInfo] = useState(null);
  const [showCompactionNotice, setShowCompactionNotice] = useState(false);

  // Refs
  const inputRef = useRef(null);

  // Token estimation utility (rough: 4 characters = 1 token)
  const estimateTokens = (text) => {
    return Math.ceil((text || '').length / 4);
  };

  // Load conversations from localStorage on mount
  useEffect(() => {
    loadConversationFromStorage();
  }, []);

  // Save conversations to localStorage when messages change
  useEffect(() => {
    if (messages.length > 0) {
      saveConversationToStorage();
    }
  }, [messages]);

  // Handle initial message
  useEffect(() => {
    if (initialMessage) {
      setInputMessage(initialMessage);
      inputRef.current?.focus();
      if (onMessageUsed) {
        onMessageUsed();
      }
    }
  }, [initialMessage, onMessageUsed]);

  // localStorage functions
  const loadConversationFromStorage = () => {
    try {
      const saved = localStorage.getItem('brobro-gemini-conversation');
      if (saved) {
        const parsed = JSON.parse(saved);

        // Check for corruption (localStorage max is usually 5-10MB)
        if (saved.length > 10000000) {
          console.warn('[CRITICAL] Detected corrupted conversation history. Clearing...');
          localStorage.removeItem('brobro-gemini-conversation');
          return;
        }

        const limited = Array.isArray(parsed) ? parsed : [];
        setMessages(limited);

        // Calculate initial token count
        const initialTokenCount = limited.reduce((sum, msg) => {
          return sum + estimateTokens(msg.content);
        }, 0);
        setTokenCount(initialTokenCount);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
      localStorage.removeItem('brobro-gemini-conversation');
    }
  };

  const saveConversationToStorage = () => {
    try {
      localStorage.setItem('brobro-gemini-conversation', JSON.stringify(messages));

      // Update token count when saving
      const newTokenCount = messages.reduce((sum, msg) => {
        return sum + estimateTokens(msg.content);
      }, 0);
      setTokenCount(newTokenCount);
    } catch (err) {
      console.error('Failed to save conversation:', err);
    }
  };

  // Check token count and get compaction warning if needed
  const checkTokenCount = async (messagesList) => {
    try {
      const messagesForBackend = messagesList.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await apiPost('/api/gemini/count-tokens', {
        messages: messagesForBackend,
        system_prompt: 'You are an expert GoHighLevel consultant and automation specialist. Provide detailed, actionable guidance.'
      }, 10000);  // 10 second timeout for token counting (should be fast)

      if (response.ok) {
        const data = await response.json();
        setTokenCount(data.token_count);

        if (data.should_warn && !showCompactionNotice) {
          console.warn('[TOKEN WARNING] Approaching token limit:', {
            tokenCount: data.token_count,
            contextWindow: data.context_window,
            utilizationPercent: data.utilization_percent
          });
          setShowCompactionNotice(true);
        }

        if (data.should_compact) {
          console.warn('[AUTO-COMPACT NEEDED] Token count exceeds compact threshold');
          return true; // Signal that compaction is needed
        }
      }
    } catch (err) {
      console.error('Error checking token count:', err);
      // Continue anyway - use estimation fallback
    }
    return false;
  };

  // Compact conversation history
  const handleCompactConversation = async () => {
    try {
      setIsCompacting(true);
      console.log('[COMPACTING] Starting conversation compaction...');

      const messagesForBackend = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await apiPost('/api/gemini/compact', {
        messages: messagesForBackend,
        system_prompt: 'You are an expert GoHighLevel consultant and automation specialist. Provide detailed, actionable guidance.'
      });

      if (!response.ok) {
        throw new Error(getErrorMessage(response));
      }

      const data = await response.json();

      // Update messages with compacted version
      const compactedMessages = data.compacted_messages.map((msg, idx) => ({
        id: `compacted-${idx}`,
        role: msg.role,
        content: msg.content,
        timestamp: new Date().toISOString(),
      }));

      setMessages(compactedMessages);
      setTokenCount(data.token_count);

      setCompactionInfo({
        messagesSummarized: data.messages_summarized,
        messagesPreserved: data.messages_preserved,
        tokensBefore: null,
        tokensAfter: data.token_count,
        summary: data.summary
      });

      console.log('[COMPACTION] Conversation compacted successfully:', {
        messagesSummarized: data.messages_summarized,
        messagesPreserved: data.messages_preserved,
        tokensAfter: data.token_count
      });

      // Show success notice for 5 seconds
      setTimeout(() => {
        setCompactionInfo(null);
      }, 5000);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      setError(`Compaction failed: ${errorMsg}`);
      console.error('Compaction error:', err);
    } finally {
      setIsCompacting(false);
    }
  };

  // Send message to Gemini backend
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Check token count before sending
      const needsCompaction = await checkTokenCount(newMessages);

      if (needsCompaction) {
        setShowCompactionNotice(true);
        // Don't send message yet - wait for compaction
        setIsLoading(false);
        inputRef.current?.focus();
        return;
      }

      // Build messages array in format backend expects: [{role, content}, ...]
      const messagesForBackend = newMessages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await apiPost('/api/gemini/chat', {
        messages: messagesForBackend,
        system_prompt: 'You are an expert GoHighLevel consultant and automation specialist. Provide detailed, actionable guidance.',
        max_tokens: 50000,
        temperature: 0.2
      }, 300000);  // 5 minute timeout for complex AI operations

      if (!response.ok) {
        // Parse error from response body and create proper error
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.error || `Request failed with status ${response.status}`;
        const error = new Error(errorMessage);
        error.statusCode = response.status;
        error.isNetworkError = response.status === 0 || response.status === 408;
        throw error;
      }

      const data = await response.json();

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.response || data.answer || '',
        sources: data.sources || [],
        citations: data.citations || [],
        followUpQuestions: data.follow_up_questions || [],
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      setError(errorMsg);
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // Get the last user message and response
  const lastUserMessage = messages.filter(m => m.role === 'user').pop();
  const lastAssistantMessage = messages.filter(m => m.role === 'assistant').pop();

  return (
    <div className="gemini-chat-container">
      {/* Background with particles visible */}

      {/* Main Content Area */}
      <div className="gemini-chat-wrapper">
        {/* Messages Display Area - Upper Section */}
        <div className="gemini-messages-area">
          {/* Last User Request Bubble */}
          {lastUserMessage && (
            <div className="conversation-bubble user-bubble">
              <div className="bubble-header">
                <User size={24} />
                <span className="bubble-label">Your Question</span>
              </div>
              <div className="bubble-content">
                <p>{lastUserMessage.content}</p>
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="conversation-bubble assistant-bubble loading">
              <div className="bubble-header">
                <Bot size={24} />
                <span className="bubble-label">BroBro is thinking...</span>
              </div>
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          {/* Last Assistant Response Bubble */}
          {lastAssistantMessage && !isLoading && (
            <div className="conversation-bubble assistant-bubble">
              <div className="bubble-header">
                <Bot size={24} />
                <span className="bubble-label">BroBro Response</span>
              </div>
              <div className="bubble-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ node, ...props }) => (
                      <a {...props} target="_blank" rel="noopener noreferrer" />
                    ),
                    p: ({ node, ...props }) => <p {...props} />,
                  }}
                >
                  {lastAssistantMessage.content}
                </ReactMarkdown>
              </div>

              {/* Citations Section */}
              {lastAssistantMessage.citations && lastAssistantMessage.citations.length > 0 && (
                <div className="bubble-citations">
                  <h4>Sources</h4>
                  <ul>
                    {lastAssistantMessage.citations.slice(0, 3).map((citation, idx) => (
                      <li key={idx}>
                        <span className="citation-source">{citation.source}</span>
                        {citation.url && (
                          <a href={citation.url} target="_blank" rel="noopener noreferrer">
                            View →
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Follow-up Questions Section */}
              {lastAssistantMessage.followUpQuestions && lastAssistantMessage.followUpQuestions.length > 0 && (
                <div className="bubble-follow-ups">
                  <h4>Continue exploring:</h4>
                  <div className="follow-up-buttons">
                    {lastAssistantMessage.followUpQuestions.map((question, idx) => (
                      <button
                        key={idx}
                        className="follow-up-btn"
                        onClick={() => {
                          setInputMessage(question);
                          inputRef.current?.focus();
                        }}
                        title={question}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Empty State */}
          {messages.length === 0 && !isLoading && (
            <div className="empty-state-alt">
              <Bot size={48} />
              <h2>Ask BroBro</h2>
              <p>Get instant answers about GoHighLevel, business strategy, and more</p>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <div>
              {typeof error === 'string'
                ? error
                : (error?.title || error?.message || JSON.stringify(error) || 'An error occurred')}
            </div>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* Compaction Progress Notice */}
        {isCompacting && (
          <div className="compaction-progress">
            <Loader2 size={18} className="spinner" />
            <div>Compacting conversation history...</div>
          </div>
        )}

        {/* Compaction Success Notice */}
        {compactionInfo && (
          <div className="compaction-notice">
            <div className="compaction-header">
              <span>Conversation compacted successfully!</span>
            </div>
            <div className="compaction-stats">
              <div className="stat">
                <span className="label">Summarized:</span>
                <span className="value">{compactionInfo.messagesSummarized} messages</span>
              </div>
              <div className="stat">
                <span className="label">Preserved:</span>
                <span className="value">{compactionInfo.messagesPreserved} messages</span>
              </div>
              <div className="stat">
                <span className="label">New token count:</span>
                <span className="value">{compactionInfo.tokensAfter.toLocaleString()} tokens</span>
              </div>
            </div>
            <button
              onClick={() => setCompactionInfo(null)}
              className="notice-close-btn"
            >
              ✕
            </button>
          </div>
        )}

        {/* Token Limit Warning */}
        {showCompactionNotice && !compactionInfo && !isCompacting && (
          <div className="token-warning">
            <AlertCircle size={18} />
            <div>
              <span className="token-count">Token usage: {tokenCount.toLocaleString()} / 2,097,152</span>
              <span className="token-usage-bar">
                <span
                  className="token-usage-fill"
                  style={{ width: `${Math.min(100, (tokenCount / 2097152) * 100)}%` }}
                ></span>
              </span>
            </div>
            <button
              onClick={handleCompactConversation}
              disabled={isCompacting || isLoading}
              className="compact-btn"
            >
              Compact Now
            </button>
            <button onClick={() => setShowCompactionNotice(false)} className="notice-close-btn">
              ✕
            </button>
          </div>
        )}

        {backendOffline && <OfflineMessage />}

        {/* Search Input Area - Lower Section */}
        <div className="gemini-input-section">
          <div className="search-bubble-container">
            {/* Model Selector Tab */}
            <div className="model-selector">
              <button
                className={`model-btn ${chatBackend === 'claude' ? 'active' : ''}`}
                onClick={() => onBackendChange('claude')}
              >
                Claude
              </button>
              <button
                className={`model-btn ${chatBackend === 'gemini' ? 'active' : ''}`}
                onClick={() => onBackendChange('gemini')}
              >
                Gemini
              </button>
            </div>

            {/* Search Input */}
            <div className="search-input-wrapper">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Ask a question..."
                disabled={isLoading}
                className="gemini-input"
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="gemini-send-btn"
              >
                {isLoading ? (
                  <Loader2 size={20} className="spinner" />
                ) : (
                  <Send size={20} />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeminiChatInterface;
