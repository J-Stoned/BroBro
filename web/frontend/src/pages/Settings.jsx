import React, { useState } from 'react';
import ApiKeyManager from '../components/ApiKeyManager';
import DeploymentHistory from '../components/DeploymentHistory';
import { Settings as SettingsIcon, Key, History } from 'lucide-react';

/**
 * Settings Page - Epic 11
 * Centralized settings for API configuration and deployment history
 */

const Settings = () => {
  const [activeTab, setActiveTab] = useState('credentials'); // 'credentials' | 'history'

  return (
    <div style={{
      minHeight: '100vh',
      background: '#fafafa',
      padding: '24px'
    }}>
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto'
      }}>
        {/* Page Header */}
        <div style={{
          marginBottom: '32px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '8px'
          }}>
            <SettingsIcon size={32} color="#3b82f6" />
            <h1 style={{
              margin: 0,
              fontSize: '32px',
              fontWeight: '700',
              color: '#111827'
            }}>
              Settings
            </h1>
          </div>
          <p style={{
            margin: 0,
            fontSize: '16px',
            color: '#6b7280'
          }}>
            Manage your API credentials and view deployment history
          </p>
        </div>

        {/* Tabs */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '6px',
          marginBottom: '24px',
          display: 'inline-flex',
          gap: '4px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <TabButton
            icon={<Key size={18} />}
            label="API Credentials"
            active={activeTab === 'credentials'}
            onClick={() => setActiveTab('credentials')}
          />
          <TabButton
            icon={<History size={18} />}
            label="Deployment History"
            active={activeTab === 'history'}
            onClick={() => setActiveTab('history')}
          />
        </div>

        {/* Content */}
        <div>
          {activeTab === 'credentials' && (
            <ApiKeyManager
              onApiKeyChange={(credentials) => {
                console.log('API credentials updated:', credentials ? 'Set' : 'Cleared');
              }}
            />
          )}

          {activeTab === 'history' && (
            <DeploymentHistory
              onViewWorkflow={(workflowId) => {
                console.log('View workflow:', workflowId);
                alert(`Workflow ID: ${workflowId}\n\nView workflow functionality coming soon!`);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

// Tab Button Component
const TabButton = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    style={{
      padding: '10px 20px',
      background: active ? '#3b82f6' : 'transparent',
      color: active ? 'white' : '#6b7280',
      border: 'none',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      transition: 'all 0.2s'
    }}
    onMouseOver={(e) => {
      if (!active) {
        e.target.style.background = '#f3f4f6';
      }
    }}
    onMouseOut={(e) => {
      if (!active) {
        e.target.style.background = 'transparent';
      }
    }}
  >
    {icon}
    {label}
  </button>
);

export default Settings;
