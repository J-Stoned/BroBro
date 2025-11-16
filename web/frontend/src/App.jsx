import React, { useState, useEffect } from 'react';
import UnifiedSearchContainer from './components/search/UnifiedSearchContainer';
import SetupManagement from './components/SetupManagement';
import ChatInterface from './components/ChatInterface';
import GeminiChatInterface from './components/GeminiChatInterface';
import CommandLibrary from './components/CommandLibrary';
import WorkflowBuilder from './components/WorkflowBuilder';
import WorkflowErrorBoundary from './components/WorkflowErrorBoundary';
import Analytics from './pages/Analytics';
import ConnectionStatus from './components/ConnectionStatus';
import ParticlesBackground from './components/ParticlesBackground';
import { MessageSquare, BookOpen, GitBranch, BarChart3, Search, Settings } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [chatBackend, setChatBackend] = useState('gemini'); // Default to Gemini (Google File Search)
  const [systemHealth, setSystemHealth] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Handle connection status changes
  const handleStatusChange = (statusData) => {
    setSystemHealth(statusData.data);
    setBackendStatus(statusData.status);
  };

  // Handle "Use in Chat" from CommandLibrary
  const handleUseInChat = (commandTitle) => {
    setActiveTab('chat');
  };

  return (
    <div className="app">
      <ParticlesBackground />
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">BroBro</div>
            <div className="logo-text">
              <h1>Chat with BroBro</h1>
              <p>GoHighLevel Expert AI Assistant</p>
            </div>
          </div>

          <ConnectionStatus onStatusChange={handleStatusChange} />
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={18} />
            <span>Chat</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'commands' ? 'active' : ''}`}
            onClick={() => setActiveTab('commands')}
          >
            <BookOpen size={18} />
            <span>Commands</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'workflows' ? 'active' : ''}`}
            onClick={() => setActiveTab('workflows')}
          >
            <GitBranch size={18} />
            <span>Workflows</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <BarChart3 size={18} />
            <span>Analytics</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search size={18} />
            <span>Search</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'setup' ? 'active' : ''}`}
            onClick={() => setActiveTab('setup')}
          >
            <Settings size={18} />
            <span>Setup Management</span>
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {activeTab === 'chat' && (
          chatBackend === 'claude' ?
            <ChatInterface onBackendChange={setChatBackend} /> :
            <GeminiChatInterface chatBackend={chatBackend} onBackendChange={setChatBackend} />
        )}
        {activeTab === 'commands' && <CommandLibrary onUseInChat={handleUseInChat} />}
        {activeTab === 'workflows' && (
          <WorkflowErrorBoundary>
            <WorkflowBuilder />
          </WorkflowErrorBoundary>
        )}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'search' && <UnifiedSearchContainer />}
        {activeTab === 'setup' && <SetupManagement onHealthUpdate={handleStatusChange} />}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>BroBro - Powered by Google Gemini File Search</p>
      </footer>
    </div>
  );
}

export default App;
