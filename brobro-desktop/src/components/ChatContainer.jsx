import React, { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';

const ChatContainer = ({ messages, onSendMessage, isLoading, isConnected }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading && isConnected) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="header-content">
          <h1>🚀 GHL WHIZ Desktop</h1>
          <p>Query your 1,235+ indexed GoHighLevel knowledge base</p>
        </div>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <div className="status-dot"></div>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>👋 Welcome to GHL WHIZ!</h2>
            <p>Ask me anything about GoHighLevel</p>
            <div className="example-questions">
              <h3>Try asking:</h3>
              <button onClick={() => setInput("How do I set up email authentication?")}>
                How do I set up email authentication?
              </button>
              <button onClick={() => setInput("What are workflow automation best practices?")}>
                What are workflow automation best practices?
              </button>
              <button onClick={() => setInput("Show me info about conversation AI")}>
                Show me info about conversation AI
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map(message => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="loading-message">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Searching knowledge base...</p>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="input-container">
        {!isConnected && (
          <div className="connection-warning">
            <AlertCircle size={16} />
            Backend not connected. Make sure FastAPI server is running on http://localhost:8000
          </div>
        )}
        <form onSubmit={handleSubmit} className="input-form">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about GoHighLevel..."
            disabled={!isConnected || isLoading}
            rows={1}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || !isConnected || isLoading}
            className="send-button"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatContainer;
