import React from 'react';
import { Trash2, Database, MessageSquare } from 'lucide-react';

const Sidebar = ({ isConnected, onClearChat, messageCount }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <Database size={32} />
          <h2>GHL WHIZ</h2>
        </div>
      </div>

      <div className="sidebar-content">
        <div className="stats-card">
          <div className="stat-item">
            <MessageSquare size={20} />
            <div>
              <p className="stat-value">{messageCount}</p>
              <p className="stat-label">Messages</p>
            </div>
          </div>
          <div className="stat-item">
            <Database size={20} />
            <div>
              <p className="stat-value">1,235+</p>
              <p className="stat-label">Indexed Items</p>
            </div>
          </div>
        </div>

        <button 
          className="clear-button"
          onClick={onClearChat}
          disabled={messageCount === 0}
        >
          <Trash2 size={18} />
          Clear Chat
        </button>

        <div className="info-section">
          <h3>About</h3>
          <p>
            GHL WHIZ connects to your ChromaDB knowledge base 
            containing comprehensive GoHighLevel documentation, 
            tutorials, and best practices.
          </p>
        </div>

        <div className="info-section">
          <h3>Connection</h3>
          <div className="connection-info">
            <div className={`status-indicator ${isConnected ? 'active' : 'inactive'}`}></div>
            <div>
              <p className="connection-label">Backend Status</p>
              <p className="connection-value">
                {isConnected ? 'Connected' : 'Disconnected'}
              </p>
              <p className="connection-url">localhost:8000</p>
            </div>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <p>J Stone Media Solutions</p>
        <p className="version">v1.0.0</p>
      </div>
    </div>
  );
};

export default Sidebar;
