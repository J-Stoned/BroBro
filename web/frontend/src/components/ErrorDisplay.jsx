import React from 'react';
import { AlertCircle, RefreshCw, XCircle } from 'lucide-react';

/**
 * ErrorDisplay Component
 * Displays user-friendly error messages with retry functionality
 */

const ErrorDisplay = ({ error, onRetry, title, message, suggestion }) => {
  // Default error styling
  const defaultTitle = title || 'Error';
  const defaultMessage = message || error?.message || 'Something went wrong';
  const defaultSuggestion = suggestion || null;

  return (
    <div style={{
      padding: '24px',
      background: '#fef2f2',
      border: '1px solid #fecaca',
      borderRadius: '8px',
      maxWidth: '600px',
      margin: '20px auto'
    }}>
      {/* Icon and Title */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        marginBottom: '12px'
      }}>
        <XCircle size={24} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ flex: 1 }}>
          <h3 style={{
            margin: '0 0 8px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#991b1b'
          }}>
            {defaultTitle}
          </h3>
          <p style={{
            margin: '0 0 8px 0',
            fontSize: '14px',
            color: '#7f1d1d',
            lineHeight: '1.5'
          }}>
            {defaultMessage}
          </p>

          {/* Suggestion */}
          {defaultSuggestion && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              background: '#fee2e2',
              borderRadius: '6px',
              border: '1px solid #fca5a5'
            }}>
              <div style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-start'
              }}>
                <AlertCircle size={16} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} />
                <p style={{
                  margin: 0,
                  fontSize: '13px',
                  color: '#7f1d1d'
                }}>
                  {defaultSuggestion}
                </p>
              </div>
            </div>
          )}

          {/* Retry Button */}
          {onRetry && (
            <button
              onClick={onRetry}
              style={{
                marginTop: '16px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                background: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
              onMouseOver={(e) => e.target.style.background = '#b91c1c'}
              onMouseOut={(e) => e.target.style.background = '#dc2626'}
            >
              <RefreshCw size={16} />
              <span>Retry</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Offline Message Component
 * Special component for backend offline state
 */
export const OfflineMessage = ({ onRetry, feature }) => {
  return (
    <div style={{
      padding: '48px 24px',
      textAlign: 'center',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <div style={{
        width: '80px',
        height: '80px',
        background: '#fee2e2',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 24px'
      }}>
        <XCircle size={40} color="#ef4444" />
      </div>

      <h2 style={{
        margin: '0 0 12px 0',
        fontSize: '24px',
        fontWeight: '700',
        color: '#111827'
      }}>
        Backend Server Offline
      </h2>

      <p style={{
        margin: '0 0 24px 0',
        fontSize: '16px',
        color: '#6b7280',
        lineHeight: '1.6'
      }}>
        {feature ? `Cannot load ${feature} because the` : 'The'} backend server is not responding.
        Please ensure the backend is running.
      </p>

      <div style={{
        padding: '16px',
        background: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '8px',
        marginBottom: '24px',
        textAlign: 'left'
      }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '14px',
          fontWeight: '600',
          color: '#1e40af'
        }}>
          To start the backend:
        </h4>
        <ol style={{
          margin: 0,
          paddingLeft: '20px',
          fontSize: '14px',
          color: '#1e3a8a',
          lineHeight: '1.8'
        }}>
          <li>Open a terminal</li>
          <li>Navigate to: <code style={{ background: '#dbeafe', padding: '2px 6px', borderRadius: '3px' }}>
            c:\Users\justi\BroBro\web\backend
          </code></li>
          <li>Run: <code style={{ background: '#dbeafe', padding: '2px 6px', borderRadius: '3px' }}>
            python main.py
          </code></li>
          <li>Wait for: "Uvicorn running on http://0.0.0.0:8000"</li>
        </ol>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => e.target.style.background = '#2563eb'}
          onMouseOut={(e) => e.target.style.background = '#3b82f6'}
        >
          <RefreshCw size={18} />
          <span>Check Connection</span>
        </button>
      )}
    </div>
  );
};

export default ErrorDisplay;
