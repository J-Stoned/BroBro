import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, Clock, RefreshCw, TrendingUp } from 'lucide-react';
import { getApiKey } from '../lib/encryption';

/**
 * WorkflowStatusMonitor - Epic 11: Story 11.5
 * Real-time monitoring of workflow execution status
 */

const WorkflowStatusMonitor = ({ workflowId }) => {
  const [executions, setExecutions] = useState([]);
  const [credentials, setCredentials] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    loadCredentials();
  }, []);

  useEffect(() => {
    if (credentials && workflowId && autoRefresh) {
      const interval = setInterval(() => {
        fetchExecutions(credentials, workflowId);
      }, 10000); // Refresh every 10 seconds

      return () => clearInterval(interval);
    }
  }, [credentials, workflowId, autoRefresh]);

  const loadCredentials = async () => {
    try {
      const creds = await getApiKey();
      setCredentials(creds);
      if (creds && workflowId) {
        fetchExecutions(creds, workflowId);
      }
    } catch (error) {
      console.error('Failed to load credentials:', error);
      setError('Failed to load API credentials');
    }
  };

  const fetchExecutions = async (creds, wfId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/ghl/workflows/${wfId}/executions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: creds.apiKey,
          location_id: creds.locationId,
          limit: 20
        })
      });

      const data = await response.json();

      if (response.status === 429) {
        setError(`Rate limit exceeded. ${data.detail.message}`);
        setLoading(false);
        return;
      }

      if (data.success) {
        setExecutions(data.executions);
        setError(null);
      } else {
        setError(data.message || 'Failed to fetch executions');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (credentials && workflowId) {
      fetchExecutions(credentials, workflowId);
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return <CheckCircle size={16} color="#10b981" />;
      case 'failed':
      case 'error':
        return <XCircle size={16} color="#ef4444" />;
      case 'running':
      case 'pending':
        return <Clock size={16} color="#f59e0b" />;
      default:
        return <Activity size={16} color="#6b7280" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return '#10b981';
      case 'failed':
      case 'error':
        return '#ef4444';
      case 'running':
      case 'pending':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const stats = executions.reduce((acc, exec) => {
    const status = exec.status?.toLowerCase();
    if (status === 'success' || status === 'completed') acc.success++;
    else if (status === 'failed' || status === 'error') acc.failed++;
    else if (status === 'running' || status === 'pending') acc.running++;
    return acc;
  }, { success: 0, failed: 0, running: 0 });

  if (!credentials || !workflowId) {
    return (
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '20px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '14px'
      }}>
        Configure API credentials and deploy a workflow to monitor executions
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Activity size={24} color="#3b82f6" />
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#111827' }}>
              Execution Status
            </h3>
            <p style={{ margin: '2px 0 0 0', fontSize: '13px', color: '#6b7280' }}>
              Last 20 executions
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            color: '#6b7280',
            cursor: 'pointer'
          }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Auto-refresh
          </label>
          <button
            onClick={handleRefresh}
            disabled={loading}
            style={{
              padding: '6px',
              background: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex'
            }}
          >
            <RefreshCw
              size={16}
              color="#6b7280"
              style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }}
            />
          </button>
        </div>
      </div>

      {/* Stats */}
      {executions.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
          marginBottom: '16px'
        }}>
          <div style={{
            padding: '12px',
            background: '#f0fdf4',
            border: '1px solid #86efac',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#15803d', marginBottom: '4px' }}>
              {stats.success}
            </div>
            <div style={{ fontSize: '12px', color: '#15803d' }}>
              Success
            </div>
          </div>
          <div style={{
            padding: '12px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#b91c1c', marginBottom: '4px' }}>
              {stats.failed}
            </div>
            <div style={{ fontSize: '12px', color: '#b91c1c' }}>
              Failed
            </div>
          </div>
          <div style={{
            padding: '12px',
            background: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#92400e', marginBottom: '4px' }}>
              {stats.running}
            </div>
            <div style={{ fontSize: '12px', color: '#92400e' }}>
              Running
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          fontSize: '13px',
          color: '#b91c1c'
        }}>
          {error}
        </div>
      )}

      {/* Executions List */}
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {loading && executions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}>
            <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 8px' }} />
            <div style={{ fontSize: '14px' }}>Loading executions...</div>
          </div>
        ) : executions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}>
            <TrendingUp size={32} color="#d1d5db" style={{ margin: '0 auto 12px' }} />
            <div style={{ fontSize: '14px' }}>No executions yet</div>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>
              Workflow executions will appear here
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {executions.map((execution, idx) => (
              <div
                key={execution.id || idx}
                style={{
                  padding: '12px',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                  {getStatusIcon(execution.status)}
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '13px',
                      fontWeight: '500',
                      color: '#374151',
                      marginBottom: '2px'
                    }}>
                      Execution #{execution.id?.substring(0, 8) || idx + 1}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                      {formatTimestamp(execution.startedAt || execution.createdAt)}
                      {execution.duration && ` • ${execution.duration}ms`}
                    </div>
                  </div>
                </div>
                <div style={{
                  padding: '4px 12px',
                  background: `${getStatusColor(execution.status)}15`,
                  color: getStatusColor(execution.status),
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: '500',
                  textTransform: 'capitalize'
                }}>
                  {execution.status || 'Unknown'}
                </div>
              </div>
            ))}
          </div>
        )}
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

export default WorkflowStatusMonitor;
