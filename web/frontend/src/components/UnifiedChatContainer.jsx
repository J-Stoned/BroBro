import React, { useState, useEffect } from 'react';
import ChatHistorySidebar from './ChatHistorySidebar';
import ChatInterface from './ChatInterface';
import GeminiChatInterface from './GeminiChatInterface';
import * as conversationApi from '../api/conversationApi';
import { getSessionId } from '../utils/sessionManager';
import './UnifiedChatContainer.css';

/**
 * UnifiedChatContainer Component
 *
 * Combines ChatHistorySidebar with ChatInterface/GeminiChatInterface.
 * Handles:
 * - Conversation creation and selection
 * - Message auto-saving to backend
 * - Switching between Claude and Gemini backends
 * - Sidebar collapse state
 */

const UnifiedChatContainer = ({
  defaultBackend = 'claude'
}) => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [currentBackend, setCurrentBackend] = useState(defaultBackend);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const sessionId = getSessionId();

  // Handle new conversation
  const handleNewConversation = (newConversation) => {
    setSelectedConversationId(newConversation.id);
  };

  // Handle conversation selection
  const handleSelectConversation = async (conversationId) => {
    setSelectedConversationId(conversationId);
    // Messages will be loaded by the chat component
  };

  // Helper function to auto-save messages
  const autoSaveMessage = async (conversationId, role, content, metadata = null) => {
    if (!autoSaveEnabled || !conversationId) return;

    try {
      await conversationApi.addMessage(conversationId, role, content, metadata);
    } catch (err) {
      console.error('Failed to auto-save message:', err);
      // Don't break the chat flow, just log the error
    }
  };

  // Helper function to generate title from first user message
  const generateTitleFromMessage = (message) => {
    const maxLength = 50;
    const text = message.trim();
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  };

  // Handle auto-saving first message to generate title
  const handleFirstMessage = async (conversationId, messageContent) => {
    if (!conversationId) return;

    try {
      const title = generateTitleFromMessage(messageContent);
      await conversationApi.renameConversation(conversationId, title);
    } catch (err) {
      console.error('Failed to set conversation title:', err);
    }
  };

  return (
    <div className="unified-chat-container">
      {/* Chat History Sidebar */}
      <ChatHistorySidebar
        currentConversationId={selectedConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Chat Area */}
      <div className={`chat-area ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {currentBackend === 'claude' ? (
          <ChatInterface
            conversationId={selectedConversationId}
            onFirstMessage={handleFirstMessage}
            onAutoSaveMessage={autoSaveMessage}
          />
        ) : (
          <GeminiChatInterface
            conversationId={selectedConversationId}
            onFirstMessage={handleFirstMessage}
            onAutoSaveMessage={autoSaveMessage}
          />
        )}
      </div>
    </div>
  );
};

export default UnifiedChatContainer;
