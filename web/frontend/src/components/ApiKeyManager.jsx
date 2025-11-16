import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Save, Trash2, CheckCircle, XCircle, Loader } from 'lucide-react';
import { storeApiKey, getApiKey, clearApiKey, hasStoredApiKey } from '../lib/encryption';

/**
 * ApiKeyManager - Epic 11: Story 11.2
 * Secure API key management with AES-256 encryption
 */

const ApiKeyManager = ({ onApiKeyChange }) => {
  const [apiKey, setApiKey] = useState('');
  const [locationId, setLocationId] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isStored, setIsStored] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [testStatus, setTestStatus] = useState(null); // null | 'testing' | 'success' | 'error'
  const [testMessage, setTestMessage] = useState('');
  const [saveStatus, setSaveStatus] = useState(null); // null | 'saving' | 'success' | 'error'

  // Load stored credentials on mount
  useEffect(() => {
    loadStoredCredentials();
  }, []);

  const loadStoredCredentials = async () => {
    if (hasStoredApiKey()) {
      setIsLoading(true);
      try {
        const credentials = await getApiKey();
        if (credentials) {
          setApiKey(credentials.apiKey);
          setLocationId(credentials.locationId);
          setIsStored(true);
          if (onApiKeyChange) {
            onApiKeyChange(credentials);
          }
        }
      } catch (error) {
        console.error('Failed to load credentials:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSave = async () => {
    if (!apiKey || !locationId) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 2000);
      return;
    }

    setSaveStatus('saving');
    try {
      const success = await storeApiKey(apiKey, locationId);
      if (success) {
        setIsStored(true);
        setSaveStatus('success');
        if (onApiKeyChange) {
          onApiKeyChange({ apiKey, locationId });
        }
        setTimeout(() => setSaveStatus(null), 2000);
      } else {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus(null), 2000);
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 2000);
    }
  };

  const handleClear = () => {
    clearApiKey();
    setApiKey('');
    setLocationId('');
    setIsStored(false);
    setTestStatus(null);
    setTestMessage('');
    if (onApiKeyChange) {
      onApiKeyChange(null);
    }
  };

  const handleTest = async () => {
    if (!apiKey || !locationId) {
      setTestStatus('error');
      setTestMessage('Please enter both API key and Location ID');
      setTimeout(() => setTestStatus(null), 3000);
      return;
    }

    setTestStatus('testing');
    setTestMessage('Testing connection...');

    try {
      const response = await fetch('http://localhost:8000/api/ghl/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          location_id: locationId
        })
      });

      const data = await response.json();

      if (data.success) {
        setTestStatus('success');
        setTestMessage(`Connected! Location: ${data.location?.name || 'Unknown'}`);
      } else {
        setTestStatus('error');
        setTestMessage(data.message || 'Connection failed');
      }
    } catch (error) {
      setTestStatus('error');
      setTestMessage('Failed to connect to backend. Is the server running?');
      console.error('Test error:', error);
    }

    setTimeout(() => {
      setTestStatus(null);
      setTestMessage('');
    }, 4000);
  };

  if (isLoading) {
    return (
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px'
      }}>
        <Loader size={20} style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ color: '#6b7280' }}>Loading credentials...</span>
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#111827' }}>
          GHL API Configuration
        </h3>
        <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#6b7280' }}>
          Securely store your GoHighLevel API credentials (AES-256 encrypted)
        </p>
      </div>

      {/* API Key Input */}
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          fontSize: '14px',
          fontWeight: '500',
          color: '#374151',
          marginBottom: '6px'
        }}>
          API Key
        </label>
        <div style={{ position: 'relative' }}>
          <input
            type={showApiKey ? 'text' : 'password'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your GHL API key"
            style={{
              width: '100%',
              padding: '10px 40px 10px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none',
              transition: 'border-color 0.2s',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
          />
          <button
            onClick={() => setShowApiKey(!showApiKey)}
            style={{
              position: 'absolute',
              right: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              color: '#6b7280'
            }}
          >
            {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>

      {/* Location ID Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{
          display: 'block',
          fontSize: '14px',
          fontWeight: '500',
          color: '#374151',
          marginBottom: '6px'
        }}>
          Location ID
        </label>
        <input
          type="text"
          value={locationId}
          onChange={(e) => setLocationId(e.target.value)}
          placeholder="Enter your GHL Location ID"
          style={{
            width: '100%',
            padding: '10px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none',
            transition: 'border-color 0.2s',
            boxSizing: 'border-box'
          }}
          onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
          onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
        />
      </div>

      {/* Test Status */}
      {testStatus && (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: testStatus === 'success' ? '#f0fdf4' :
                     testStatus === 'error' ? '#fef2f2' : '#f9fafb',
          border: `1px solid ${
            testStatus === 'success' ? '#86efac' :
            testStatus === 'error' ? '#fecaca' : '#e5e7eb'
          }`
        }}>
          {testStatus === 'testing' && <Loader size={16} style={{ animation: 'spin 1s linear infinite', color: '#3b82f6' }} />}
          {testStatus === 'success' && <CheckCircle size={16} color="#10b981" />}
          {testStatus === 'error' && <XCircle size={16} color="#ef4444" />}
          <span style={{
            fontSize: '14px',
            color: testStatus === 'success' ? '#15803d' :
                   testStatus === 'error' ? '#b91c1c' : '#374151'
          }}>
            {testMessage}
          </span>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={handleTest}
          disabled={testStatus === 'testing'}
          style={{
            flex: 1,
            minWidth: '120px',
            padding: '10px 16px',
            background: 'white',
            color: '#3b82f6',
            border: '1px solid #3b82f6',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: testStatus === 'testing' ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            transition: 'all 0.2s',
            opacity: testStatus === 'testing' ? 0.6 : 1
          }}
          onMouseOver={(e) => {
            if (testStatus !== 'testing') {
              e.target.style.background = '#eff6ff';
            }
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'white';
          }}
        >
          {testStatus === 'testing' ? 'Testing...' : 'Test Connection'}
        </button>

        <button
          onClick={handleSave}
          disabled={saveStatus === 'saving'}
          style={{
            flex: 1,
            minWidth: '120px',
            padding: '10px 16px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: saveStatus === 'saving' ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            transition: 'background 0.2s',
            opacity: saveStatus === 'saving' ? 0.6 : 1
          }}
          onMouseOver={(e) => {
            if (saveStatus !== 'saving') {
              e.target.style.background = '#2563eb';
            }
          }}
          onMouseOut={(e) => {
            e.target.style.background = '#3b82f6';
          }}
        >
          {saveStatus === 'saving' ? (
            <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
          ) : saveStatus === 'success' ? (
            <CheckCircle size={16} />
          ) : (
            <Save size={16} />
          )}
          {saveStatus === 'saving' ? 'Saving...' :
           saveStatus === 'success' ? 'Saved!' : 'Save Credentials'}
        </button>

        {isStored && (
          <button
            onClick={handleClear}
            style={{
              padding: '10px 16px',
              background: 'white',
              color: '#ef4444',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.target.style.background = '#fef2f2';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'white';
            }}
          >
            <Trash2 size={16} />
            Clear
          </button>
        )}
      </div>

      {/* Security Notice */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        background: '#f9fafb',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        fontSize: '12px',
        color: '#6b7280',
        lineHeight: '1.5'
      }}>
        🔒 Your API credentials are encrypted with AES-256-GCM and stored locally in your browser.
        They never leave your device unencrypted.
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ApiKeyManager;
