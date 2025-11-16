import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, CheckCircle, AlertCircle, Loader, FileDown } from 'lucide-react';
import { getApiKey } from '../lib/encryption';

/**
 * WorkflowImporter - Epic 11: Story 11.4
 * Import existing workflows from GHL account
 */

const WorkflowImporter = ({ onImport, onClose }) => {
  const [workflows, setWorkflows] = useState([]);
  const [credentials, setCredentials] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const creds = await getApiKey();
      setCredentials(creds);
      if (creds) {
        fetchWorkflows(creds);
      }
    } catch (error) {
      console.error('Failed to load credentials:', error);
      setError('Failed to load API credentials');
    }
  };

  const fetchWorkflows = async (creds) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/ghl/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: creds.apiKey,
          location_id: creds.locationId,
          limit: 100
        })
      });

      const data = await response.json();

      if (response.status === 429) {
        setError(`Rate limit exceeded. ${data.detail.message}`);
        setLoading(false);
        return;
      }

      if (data.success) {
        setWorkflows(data.workflows);
        setError(null);
      } else {
        setError(data.message || 'Failed to fetch workflows');
      }
    } catch (err) {
      setError('Failed to connect to server. Is the backend running?');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImportWorkflow = async (workflowId) => {
    if (!credentials) return;

    setImporting(true);
    setSelectedWorkflowId(workflowId);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/ghl/workflows/${workflowId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: credentials.apiKey,
          location_id: credentials.locationId
        })
      });

      const data = await response.json();

      if (response.status === 429) {
        setError(`Rate limit exceeded. ${data.detail.message}`);
        setImporting(false);
        setSelectedWorkflowId(null);
        return;
      }

      if (data.success) {
        // Transform GHL workflow to our format
        const transformedWorkflow = transformGHLWorkflow(data.workflow);

        if (onImport) {
          onImport(transformedWorkflow);
        }

        // Close modal after successful import
        setTimeout(() => {
          if (onClose) onClose();
        }, 500);
      } else {
        setError(data.message || 'Failed to import workflow');
      }
    } catch (err) {
      setError('Failed to import workflow');
      console.error('Import error:', err);
    } finally {
      setImporting(false);
      setSelectedWorkflowId(null);
    }
  };

  const transformGHLWorkflow = (ghlWorkflow) => {
    // Transform GHL workflow format to our internal format
    return {
      id: ghlWorkflow.id,
      name: ghlWorkflow.name || 'Imported Workflow',
      description: ghlWorkflow.description || 'Imported from GHL',
      niche: 'general',
      difficulty: 'intermediate',
      version: ghlWorkflow.version || '1.0',
      nodes: (ghlWorkflow.nodes || []).map(node => ({
        id: node.id,
        type: node.type || 'action',
        title: node.name || node.title || 'Untitled',
        description: node.description || '',
        position: node.position || { x: 100, y: 100 },
        params: node.config || node.params || {}
      })),
      connections: ghlWorkflow.connections || [],
      metadata: {
        createdAt: ghlWorkflow.createdAt || new Date().toISOString(),
        updatedAt: ghlWorkflow.updatedAt || new Date().toISOString(),
        source: 'ghl_import',
        ghl_id: ghlWorkflow.id
      }
    };
  };

  const handleRefresh = () => {
    if (credentials) {
      fetchWorkflows(credentials);
    }
  };

  if (!credentials) {
    return (
      <div className="modal-overlay" onClick={onClose} style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div onClick={(e) => e.stopPropagation()} style={{
          background: 'white',
          borderRadius: '12px',
          padding: '32px',
          maxWidth: '400px',
          textAlign: 'center'
        }}>
          <AlertCircle size={48} color="#f59e0b" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ margin: '0 0 12px 0', fontSize: '18px', fontWeight: '600' }}>
            API Credentials Required
          </h3>
          <p style={{ margin: '0 0 20px 0', fontSize: '14px', color: '#6b7280', lineHeight: '1.5' }}>
            Please configure your GHL API credentials in Settings before importing workflows.
          </p>
          <button onClick={onClose} style={{
            padding: '10px 20px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer'
          }}>
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose} style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: 'white',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '700px',
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <FileDown size={24} color="#3b82f6" />
            <div>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
                Import from GHL
              </h2>
              <p style={{ margin: '2px 0 0 0', fontSize: '13px', color: '#6b7280' }}>
                {workflows.length} workflows available
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleRefresh}
              disabled={loading}
              style={{
                padding: '8px',
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <RefreshCw size={18} color="#6b7280" style={{
                animation: loading ? 'spin 1s linear infinite' : 'none'
              }} />
            </button>
            <button onClick={onClose} style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '24px',
              color: '#6b7280',
              padding: '0 8px'
            }}>
              ×
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            margin: '16px 24px 0',
            padding: '12px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            color: '#b91c1c'
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Workflows List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px 24px'
        }}>
          {loading ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '40px',
              color: '#6b7280'
            }}>
              <Loader size={32} style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
              <span>Loading workflows...</span>
            </div>
          ) : workflows.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#6b7280'
            }}>
              <FileDown size={48} color="#d1d5db" style={{ margin: '0 auto 12px' }} />
              <p style={{ margin: 0, fontSize: '16px' }}>No workflows found</p>
              <p style={{ margin: '4px 0 0 0', fontSize: '14px' }}>
                Create workflows in GHL first, then import them here
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.2s',
                    cursor: 'pointer'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.background = '#eff6ff';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = '#e5e7eb';
                    e.currentTarget.style.background = 'white';
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <h4 style={{
                      margin: 0,
                      fontSize: '15px',
                      fontWeight: '600',
                      color: '#111827',
                      marginBottom: '4px'
                    }}>
                      {workflow.name || 'Untitled Workflow'}
                    </h4>
                    <p style={{
                      margin: 0,
                      fontSize: '13px',
                      color: '#6b7280',
                      marginBottom: '8px'
                    }}>
                      {workflow.description || 'No description'}
                    </p>
                    <div style={{
                      display: 'flex',
                      gap: '16px',
                      fontSize: '12px',
                      color: '#9ca3af'
                    }}>
                      <span>{workflow.nodes?.length || 0} nodes</span>
                      <span>•</span>
                      <span>ID: {workflow.id.substring(0, 8)}...</span>
                      {workflow.status && (
                        <>
                          <span>•</span>
                          <span style={{
                            color: workflow.status === 'active' ? '#10b981' : '#6b7280'
                          }}>
                            {workflow.status}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleImportWorkflow(workflow.id)}
                    disabled={importing && selectedWorkflowId === workflow.id}
                    style={{
                      padding: '8px 16px',
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: (importing && selectedWorkflowId === workflow.id) ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      opacity: (importing && selectedWorkflowId === workflow.id) ? 0.6 : 1
                    }}
                  >
                    {importing && selectedWorkflowId === workflow.id ? (
                      <>
                        <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} />
                        Importing...
                      </>
                    ) : (
                      <>
                        <Download size={14} />
                        Import
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: '#6b7280'
        }}>
          <span>Location: {credentials.locationId.substring(0, 12)}...</span>
          <button onClick={onClose} style={{
            padding: '8px 16px',
            background: 'white',
            color: '#6b7280',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer'
          }}>
            Cancel
          </button>
        </div>
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

export default WorkflowImporter;
