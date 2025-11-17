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
 * - LocalStorage migration to backend on first load
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
  const [migrationComplete, setMigrationComplete] = useState(false);
  const sessionId = getSessionId();

  // Migrate localStorage data to backend on first load
  useEffect(() => {
    const migrateLocalStorageData = async () => {
      try {
        // Check if migration has already been done
        const migrated = localStorage.getItem('brobro-migrated-to-backend');
        if (migrated) {
          setMigrationComplete(true);
          return;
        }

        // Migrate Claude conversations from localStorage
        const claudeData = localStorage.getItem('brobro-conversation');
        if (claudeData) {
          try {
            const parsedData = JSON.parse(claudeData);
            if (parsedData && typeof parsedData === 'object') {
              // Create conversation with Claude backend
              const newConv = await conversationApi.createConversation(sessionId, 'Migrated Claude Conversation');

              // Add messages if they exist
              if (Array.isArray(parsedData.messages)) {
                for (const msg of parsedData.messages) {
                  await conversationApi.addMessage(
                    newConv.id,
                    msg.role || 'user',
                    msg.content || '',
                    { migrated_from: 'localStorage', original_timestamp: msg.timestamp }
                  );
                }
              }

              // Update conversation with backend_type
              if (newConv.id) {
                await conversationApi.updateConversation(newConv.id, {
                  title: parsedData.title || 'Migrated Claude Conversation',
                  backend_type: 'claude'
                });
              }
            }
          } catch (err) {
            console.error('Failed to migrate Claude conversation:', err);
          }
        }

        // Migrate Gemini conversations from localStorage
        const geminiData = localStorage.getItem('brobro-gemini-conversation');
        if (geminiData) {
          try {
            const parsedData = JSON.parse(geminiData);
            if (parsedData && typeof parsedData === 'object') {
              // Create conversation with Gemini backend
              const newConv = await conversationApi.createConversation(sessionId, 'Migrated Gemini Conversation');

              // Add messages if they exist
              if (Array.isArray(parsedData.messages)) {
                for (const msg of parsedData.messages) {
                  await conversationApi.addMessage(
                    newConv.id,
                    msg.role || 'user',
                    msg.content || '',
                    { migrated_from: 'localStorage', original_timestamp: msg.timestamp }
                  );
                }
              }

              // Update conversation with backend_type
              if (newConv.id) {
                await conversationApi.updateConversation(newConv.id, {
                  title: parsedData.title || 'Migrated Gemini Conversation',
                  backend_type: 'gemini'
                });
              }
            }
          } catch (err) {
            console.error('Failed to migrate Gemini conversation:', err);
          }
        }

        // Mark migration as complete
        localStorage.setItem('brobro-migrated-to-backend', 'true');
        setMigrationComplete(true);
      } catch (err) {
        console.error('LocalStorage migration error:', err);
        setMigrationComplete(true); // Continue anyway
      }
    };

    migrateLocalStorageData();
  }, [sessionId]);

  // Handle new conversation
  const handleNewConversation = (newConversation) => {
    setSelectedConversationId(newConversation.id);
    setCurrentBackend(newConversation.backend_type || 'claude');
  };

  // Handle conversation selection
  const handleSelectConversation = async (conversationId) => {
    setSelectedConversationId(conversationId);

    // Fetch conversation details to get backend_type
    try {
      const convDetails = await conversationApi.getConversation(conversationId);
      if (convDetails && convDetails.conversation) {
        const backend = convDetails.conversation.backend_type || 'claude';
        setCurrentBackend(backend);
      }
    } catch (err) {
      console.error('Failed to fetch conversation details:', err);
      // Continue with default backend
    }
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

  // Only render chat interface after migration is complete
  if (!migrationComplete) {
    return (
      <div className="unified-chat-container">
        <div className="migration-loading">
          <p>Initializing chat system...</p>
        </div>
      </div>
    );
  }

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
            disableLocalStorage={true}
            onFirstMessage={handleFirstMessage}
            onAutoSaveMessage={autoSaveMessage}
          />
        ) : (
          <GeminiChatInterface
            conversationId={selectedConversationId}
            disableLocalStorage={true}
            onFirstMessage={handleFirstMessage}
            onAutoSaveMessage={autoSaveMessage}
          />
        )}
      </div>
    </div>
  );
};

export default UnifiedChatContainer;
