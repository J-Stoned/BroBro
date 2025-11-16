import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, XCircle, AlertCircle, Loader, Rocket } from 'lucide-react';
import { getApiKey } from '../lib/encryption';

/**
 * DeploymentPanel - Epic 11: Story 11.3
 * One-click workflow deployment to GHL with validation
 */

const DeploymentPanel = ({ workflow, onDeploymentSuccess, onDeploymentError }) => {
  const [deployStatus, setDeployStatus] = useState(null); // null | 'validating' | 'deploying' | 'success' | 'error'
  const [deployMessage, setDeployMessage] = useState('');
  const [validation, setValidation] = useState(null);
  const [credentials, setCredentials] = useState(null);
  const [showValidation, setShowValidation] = useState(false);
  const [rateLimit, setRateLimit] = useState(null);

  // Load credentials on mount
  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const creds = await getApiKey();
      setCredentials(creds);
    } catch (error) {
      console.error('Failed to load credentials:', error);
    }
  };

  const validateWorkflow = async () => {
    setDeployStatus('validating');
    setDeployMessage('Validating workflow...');
    setShowValidation(true);

    try {
      const response = await fetch('http://localhost:8000/api/ghl/workflows/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ workflow })
      });

      const data = await response.json();
      setValidation(data);

      if (data.valid) {
        setDeployStatus(null);
        setDeployMessage('');
        return true;
      } else {
        setDeployStatus('error');
        setDeployMessage(`Validation failed: ${data.errors.length} error(s) found`);
        return false;
      }
    } catch (error) {
      setDeployStatus('error');
      setDeployMessage('Validation failed: Unable to connect to server');
      console.error('Validation error:', error);
      return false;
    }
  };

  const handleDeploy = async () => {
    // Check credentials
    if (!credentials) {
      setDeployStatus('error');
      setDeployMessage('Please configure your API credentials first');
      setTimeout(() => setDeployStatus(null), 3000);
      return;
    }

    // Validate first
    const isValid = await validateWorkflow();
    if (!isValid) {
      return;
    }

    // Deploy
    setDeployStatus('deploying');
    setDeployMessage('Deploying workflow to GHL...');

    try {
      const response = await fetch('http://localhost:8000/api/ghl/workflows/deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: credentials.apiKey,
          location_id: credentials.locationId,
          workflow: workflow
        })
      });

      const data = await response.json();

      if (response.status === 429) {
        // Rate limit exceeded
        setDeployStatus('error');
        setDeployMessage(`Rate limit exceeded. ${data.detail.message}`);
        setRateLimit(data.detail);
        setTimeout(() => {
          setDeployStatus(null);
          setRateLimit(null);
        }, 5000);
        return;
      }

      if (data.success) {
        setDeployStatus('success');
        setDeployMessage(`Successfully deployed! Workflow ID: ${data.workflow_id}`);
        setRateLimit(data.rate_limit);

        // Save to deployment history
        saveToHistory({
          workflow_id: data.workflow_id,
          workflow_name: workflow.name,
          deployed_at: new Date().toISOString(),
          location_id: credentials.locationId
        });

        if (onDeploymentSuccess) {
          onDeploymentSuccess(data);
        }

        setTimeout(() => {
          setDeployStatus(null);
          setDeployMessage('');
        }, 5000);
      } else {
        setDeployStatus('error');
        setDeployMessage(data.message || 'Deployment failed');

        if (data.validation) {
          setValidation(data.validation);
          setShowValidation(true);
        }

        if (onDeploymentError) {
          onDeploymentError(data);
        }

        setTimeout(() => {
          setDeployStatus(null);
        }, 5000);
      }
    } catch (error) {
      setDeployStatus('error');
      setDeployMessage('Deployment failed: Unable to connect to server');
      console.error('Deployment error:', error);

      if (onDeploymentError) {
        onDeploymentError({ error: error.message });
      }

      setTimeout(() => {
        setDeployStatus(null);
      }, 5000);
    }
  };

  const saveToHistory = (deployment) => {
    try {
      const history = JSON.parse(localStorage.getItem('ghl_deployment_history') || '[]');
      history.unshift(deployment);

      // Keep only last 50 deployments
      if (history.length > 50) {
        history.splice(50);
      }

      localStorage.setItem('ghl_deployment_history', JSON.stringify(history));
    } catch (error) {
      console.error('Failed to save deployment history:', error);
    }
  };

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
        gap: '12px',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <Rocket size={24} color="#3b82f6" />
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#111827' }}>
            Deploy to GHL
          </h3>
          <p style={{ margin: '2px 0 0 0', fontSize: '13px', color: '#6b7280' }}>
            {workflow?.name || 'Untitled Workflow'}
          </p>
        </div>
      </div>

      {/* Workflow Info */}
      <div style={{
        background: '#f9fafb',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '16px',
        fontSize: '13px',
        color: '#374151'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ color: '#6b7280' }}>Nodes:</span>
          <span style={{ fontWeight: '500' }}>{workflow?.nodes?.length || 0}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ color: '#6b7280' }}>Connections:</span>
          <span style={{ fontWeight: '500' }}>{workflow?.connections?.length || 0}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#6b7280' }}>Credentials:</span>
          <span style={{ fontWeight: '500', color: credentials ? '#10b981' : '#ef4444' }}>
            {credentials ? 'Configured' : 'Not configured'}
          </span>
        </div>
      </div>

      {/* Status Message */}
      {deployStatus && (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background:
            deployStatus === 'success' ? '#f0fdf4' :
            deployStatus === 'error' ? '#fef2f2' :
            deployStatus === 'validating' || deployStatus === 'deploying' ? '#eff6ff' : '#f9fafb',
          border: `1px solid ${
            deployStatus === 'success' ? '#86efac' :
            deployStatus === 'error' ? '#fecaca' :
            deployStatus === 'validating' || deployStatus === 'deploying' ? '#bfdbfe' : '#e5e7eb'
          }`
        }}>
          {(deployStatus === 'validating' || deployStatus === 'deploying') && (
            <Loader size={16} style={{ animation: 'spin 1s linear infinite', color: '#3b82f6' }} />
          )}
          {deployStatus === 'success' && <CheckCircle size={16} color="#10b981" />}
          {deployStatus === 'error' && <XCircle size={16} color="#ef4444" />}
          <span style={{
            fontSize: '14px',
            color:
              deployStatus === 'success' ? '#15803d' :
              deployStatus === 'error' ? '#b91c1c' :
              '#1e40af'
          }}>
            {deployMessage}
          </span>
        </div>
      )}

      {/* Rate Limit Info */}
      {rateLimit && (
        <div style={{
          marginBottom: '16px',
          padding: '10px 12px',
          background: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '8px',
          fontSize: '13px',
          color: '#1e40af',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>API Rate Limit:</span>
          <span style={{ fontWeight: '500' }}>
            {rateLimit.remaining} requests remaining
            {rateLimit.reset_in > 0 && ` (resets in ${Math.ceil(rateLimit.reset_in)}s)`}
          </span>
        </div>
      )}

      {/* Validation Results */}
      {showValidation && validation && (
        <div style={{
          marginBottom: '16px',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '10px 12px',
            background: validation.valid ? '#f0fdf4' : '#fef2f2',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {validation.valid ? (
                <CheckCircle size={16} color="#10b981" />
              ) : (
                <XCircle size={16} color="#ef4444" />
              )}
              <span style={{
                fontSize: '14px',
                fontWeight: '500',
                color: validation.valid ? '#15803d' : '#b91c1c'
              }}>
                {validation.valid ? 'Validation Passed' : 'Validation Failed'}
              </span>
            </div>
            <button
              onClick={() => setShowValidation(false)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '18px',
                color: '#6b7280',
                padding: '0 4px'
              }}
            >
              ×
            </button>
          </div>

          {/* Errors */}
          {validation.errors && validation.errors.length > 0 && (
            <div style={{ padding: '12px', background: 'white' }}>
              <div style={{
                fontSize: '13px',
                fontWeight: '500',
                color: '#ef4444',
                marginBottom: '8px'
              }}>
                Errors ({validation.errors.length}):
              </div>
              <ul style={{
                margin: 0,
                paddingLeft: '20px',
                fontSize: '13px',
                color: '#6b7280',
                lineHeight: '1.6'
              }}>
                {validation.errors.map((error, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    <strong>{error.code}:</strong> {error.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {validation.warnings && validation.warnings.length > 0 && (
            <div style={{ padding: '12px', background: 'white', borderTop: '1px solid #e5e7eb' }}>
              <div style={{
                fontSize: '13px',
                fontWeight: '500',
                color: '#f59e0b',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <AlertCircle size={14} />
                Warnings ({validation.warnings.length}):
              </div>
              <ul style={{
                margin: 0,
                paddingLeft: '20px',
                fontSize: '13px',
                color: '#6b7280',
                lineHeight: '1.6'
              }}>
                {validation.warnings.map((warning, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    <strong>{warning.code}:</strong> {warning.message}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={validateWorkflow}
          disabled={deployStatus === 'validating' || deployStatus === 'deploying'}
          style={{
            flex: 1,
            padding: '12px 16px',
            background: 'white',
            color: '#6b7280',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: (deployStatus === 'validating' || deployStatus === 'deploying') ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            opacity: (deployStatus === 'validating' || deployStatus === 'deploying') ? 0.6 : 1
          }}
          onMouseOver={(e) => {
            if (deployStatus !== 'validating' && deployStatus !== 'deploying') {
              e.target.style.background = '#f9fafb';
            }
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'white';
          }}
        >
          Validate Only
        </button>

        <button
          onClick={handleDeploy}
          disabled={!credentials || deployStatus === 'validating' || deployStatus === 'deploying'}
          style={{
            flex: 2,
            padding: '12px 16px',
            background: (!credentials || deployStatus === 'validating' || deployStatus === 'deploying') ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: (!credentials || deployStatus === 'validating' || deployStatus === 'deploying') ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => {
            if (credentials && deployStatus !== 'validating' && deployStatus !== 'deploying') {
              e.target.style.background = '#2563eb';
            }
          }}
          onMouseOut={(e) => {
            if (credentials && deployStatus !== 'validating' && deployStatus !== 'deploying') {
              e.target.style.background = '#3b82f6';
            }
          }}
        >
          {deployStatus === 'deploying' ? (
            <>
              <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
              Deploying...
            </>
          ) : (
            <>
              <Upload size={16} />
              Deploy to GHL
            </>
          )}
        </button>
      </div>

      {/* Help Text */}
      {!credentials && (
        <div style={{
          marginTop: '12px',
          padding: '10px 12px',
          background: '#fffbeb',
          border: '1px solid #fde68a',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#92400e',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={14} />
          <span>Configure your API credentials in Settings to enable deployment</span>
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default DeploymentPanel;
