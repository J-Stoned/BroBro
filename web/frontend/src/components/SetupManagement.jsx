import React, { useState, useEffect } from 'react';
import {
  Server,
  CheckCircle,
  XCircle,
  RefreshCw,
  Zap,
  AlertCircle,
  BarChart3
} from 'lucide-react';
import { apiGet, getErrorMessage } from '../utils/api';
import { OfflineMessage } from './ErrorDisplay';
import './SetupManagement.css';

function SetupManagement({ onHealthUpdate }) {
  const [health, setHealth] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [collections, setCollections] = useState(null);
  const [geminiStatus, setGeminiStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [geminiLoading, setGeminiLoading] = useState(false);

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch system data using API utility
      const [healthResult, systemResult, collectionsResult, geminiResult] = await Promise.all([
        apiGet('/health'),
        apiGet('/api/system/info'),
        apiGet('/api/collections'),
        apiGet('/api/gemini/status')
      ]);

      setHealth(healthResult.data);
      setSystemInfo(systemResult.data);
      setCollections(collectionsResult.data);
      setGeminiStatus(geminiResult.data);

      if (onHealthUpdate) {
        onHealthUpdate({
          status: healthResult.data?.status || 'healthy',
          data: healthResult.data
        });
      }
    } catch (err) {
      console.error('Failed to load system data:', err);
      const errorInfo = getErrorMessage(err);
      setError(errorInfo);
    } finally {
      setLoading(false);
    }
  };

  const loadGeminiStatus = async () => {
    setGeminiLoading(true);
    try {
      const result = await apiGet('/api/gemini/status');
      setGeminiStatus(result.data);
    } catch (err) {
      console.error('Failed to load Gemini status:', err);
    } finally {
      setGeminiLoading(false);
    }
  };

  const handleRetry = () => {
    loadSystemData();
  };

  const getStatusIcon = (status) => {
    if (status === 'healthy') return <CheckCircle size={20} color="#10b981" />;
    if (status === 'degraded') return <AlertCircle size={20} color="#f59e0b" />;
    return <XCircle size={20} color="#ef4444" />;
  };

  const getStatusColor = (status) => {
    if (status === 'healthy') return '#10b981';
    if (status === 'degraded') return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="setup-management">
      <div className="setup-header">
        <div>
          <h2>Setup Management</h2>
          <p>Epic 7: System configuration and monitoring</p>
        </div>
        <button
          className="refresh-button"
          onClick={loadSystemData}
          disabled={loading}
        >
          <RefreshCw size={18} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {error && error.isRetryable && (
        <OfflineMessage onRetry={handleRetry} feature="setup management" />
      )}

      {error && !error.isRetryable && (
        <div className="error-banner">
          <XCircle size={20} />
          <span>{error.title}: {error.message}</span>
          {error.suggestion && <p className="error-suggestion">{error.suggestion}</p>}
        </div>
      )}

      {/* System Health Status */}
      <div className="status-grid">
        <div className="status-card">
          <div className="status-header">
            <Server size={24} />
            <h3>System Status</h3>
          </div>
          {health && (
            <div className="status-content">
              <div className="status-indicator">
                {getStatusIcon(health.status)}
                <span style={{ color: getStatusColor(health.status) }}>
                  {health.status.toUpperCase()}
                </span>
              </div>
              <p className="status-message">{health.message}</p>
              <div className="status-meta">
                <span>Last checked: {new Date(health.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          )}
        </div>

        <div className="status-card">
          <div className="status-header">
            <Zap size={24} />
            <h3>Google File Search</h3>
          </div>
          {geminiStatus && (
            <div className="status-content">
              <div className="status-indicator">
                {geminiStatus.configured ? (
                  <>
                    {getStatusIcon('healthy')}
                    <span style={{ color: '#10b981' }}>CONFIGURED</span>
                  </>
                ) : (
                  <>
                    {getStatusIcon('degraded')}
                    <span style={{ color: '#f59e0b' }}>NOT CONFIGURED</span>
                  </>
                )}
              </div>
              <p className="status-message">{geminiStatus.message}</p>
              <div className="connection-details" style={{ marginTop: '1rem' }}>
                <div className="detail-row">
                  <span className="detail-label">Model:</span>
                  <span className="detail-value">{geminiStatus.model}</span>
                </div>
                {geminiStatus.store_id && (
                  <div className="detail-row">
                    <span className="detail-label">Store ID:</span>
                    <span className="detail-value" style={{ fontSize: '0.85rem', wordBreak: 'break-all' }}>
                      {geminiStatus.store_id.substring(0, 20)}...
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
          {geminiLoading && (
            <div className="status-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                <span>Loading status...</span>
              </div>
            </div>
          )}
        </div>

        <div className="status-card">
          <div className="status-header">
            <BarChart3 size={24} />
            <h3>Statistics</h3>
          </div>
          {systemInfo && (
            <div className="status-content">
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">{systemInfo.total_documents.toLocaleString()}</div>
                  <div className="stat-label">Total Documents</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{systemInfo.collections.length}</div>
                  <div className="stat-label">Collections</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>



      {/* Google File Search Configuration */}
      <div className="section">
        <h3 className="section-title">
          <Zap size={20} />
          Google File Search Configuration
        </h3>
        <div className="gemini-config-card">
          {geminiStatus?.configured ? (
            <div className="gemini-status-success">
              <div className="gemini-header">
                <CheckCircle size={24} color="#10b981" />
                <h4>Google File Search is Configured</h4>
              </div>
              <div className="gemini-details">
                <div className="gemini-detail-row">
                  <span className="gemini-detail-label">Model:</span>
                  <span className="gemini-detail-value">{geminiStatus.model}</span>
                </div>
                <div className="gemini-detail-row">
                  <span className="gemini-detail-label">Store ID:</span>
                  <span className="gemini-detail-value gemini-store-id">
                    {geminiStatus.store_id}
                  </span>
                </div>
                <div className="gemini-detail-row">
                  <span className="gemini-detail-label">Context Window:</span>
                  <span className="gemini-detail-value">2,097,152 tokens (2M)</span>
                </div>
                <div className="gemini-detail-row">
                  <span className="gemini-detail-label">Auto-Compaction Threshold:</span>
                  <span className="gemini-detail-value">1,500,000 tokens (75%)</span>
                </div>
              </div>
              <div className="gemini-actions">
                <button
                  className="gemini-action-btn refresh-btn"
                  onClick={loadGeminiStatus}
                  disabled={geminiLoading}
                >
                  <RefreshCw size={16} className={geminiLoading ? 'spin' : ''} />
                  Refresh Status
                </button>
              </div>
            </div>
          ) : (
            <div className="gemini-status-error">
              <div className="gemini-header">
                <AlertCircle size={24} color="#f59e0b" />
                <h4>Google File Search Not Configured</h4>
              </div>
              <p className="gemini-message">
                {geminiStatus?.message || 'Store ID not found. Please configure Google File Search API.'}
              </p>
              <div className="gemini-setup-instructions">
                <h5>Setup Instructions:</h5>
                <ol>
                  <li>Set the <code>GOOGLE_API_KEY</code> environment variable with your Google API key</li>
                  <li>Run the file upload script to create a file search store</li>
                  <li>Set the <code>GEMINI_FILE_SEARCH_STORE_ID</code> environment variable</li>
                  <li>Restart the backend server</li>
                </ol>
              </div>
              <div className="gemini-actions">
                <button
                  className="gemini-action-btn refresh-btn"
                  onClick={loadGeminiStatus}
                  disabled={geminiLoading}
                >
                  <RefreshCw size={16} className={geminiLoading ? 'spin' : ''} />
                  Check Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SetupManagement;
