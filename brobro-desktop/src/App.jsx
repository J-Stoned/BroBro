import React, { useState, useEffect } from 'react';
import ChatContainer from './components/ChatContainer';
import Sidebar from './components/Sidebar';
import chromaAPI from './api/chromadb';
import './styles/App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    const connected = await chromaAPI.checkHealth();
    setIsConnected(connected);
  };

  const handleSendMessage = async (message) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Query ChromaDB
    const response = await chromaAPI.query(message);
    
    setIsLoading(false);

    // Add bot response
    const botMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.success 
        ? formatResponse(response.data)
        : `❌ ${response.error}`,
      timestamp: new Date(),
      sources: response.success ? extractSources(response.data) : []
    };

    setMessages(prev => [...prev, botMessage]);
  };

  const formatResponse = (data) => {
    if (!data.results || data.results.length === 0) {
      return "I couldn't find relevant information in the knowledge base.";
    }

    let response = "📚 Here's what I found:\n\n";
    
    // Show up to 10 results with better formatting
    data.results.slice(0, 10).forEach((result, index) => {
      const doc = result.document || '';
      const metadata = result.metadata || {};
      const source = metadata.title || metadata.source || metadata.name || 'Unknown Source';
      const collection = metadata.collection || 'unknown';
      const type = metadata.type || collection;
      
      response += `**${index + 1}. ${source}**\n`;
      response += `*Source: ${type}*\n`;
      response += `${doc.substring(0, 500)}...\n\n`;
    });

    return response;
  };

  const extractSources = (data) => {
    if (!data.results) return [];
    
    return data.results.slice(0, 10).map(result => ({
      name: result.metadata?.title || result.metadata?.source || 'Unknown',
      excerpt: result.document?.substring(0, 150) || ''
    }));
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app">
      <Sidebar 
        isConnected={isConnected}
        onClearChat={handleClearChat}
        messageCount={messages.length}
      />
      <ChatContainer
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        isConnected={isConnected}
      />
    </div>
  );
}

export default App;
