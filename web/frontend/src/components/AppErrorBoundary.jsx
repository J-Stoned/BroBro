import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

/**
 * AppErrorBoundary - Root level error boundary for entire application
 * Catches any React errors and displays helpful error message instead of blank screen
 */

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '24px',
          textAlign: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}>
          <AlertCircle size={64} color="#ffffff" />
          <h2 style={{ marginTop: '24px', fontSize: '24px', fontWeight: '600', color: '#ffffff' }}>
            Application Error
          </h2>
          <p style={{ marginTop: '12px', color: '#e0e7ff', maxWidth: '500px' }}>
            {this.state.error ? this.state.error.toString() : 'An unexpected error occurred. Please try refreshing the page.'}
          </p>

          <button onClick={this.handleReset} style={{
            marginTop: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: '#ffffff',
            color: '#667eea',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '600'
          }}>
            <RefreshCw size={20} />
            Reload Page
          </button>

          {this.state.error && (
            <details style={{ marginTop: '32px', textAlign: 'left', maxWidth: '600px', color: '#e0e7ff' }}>
              <summary style={{ cursor: 'pointer', fontSize: '14px', fontWeight: '500' }}>
                Error Details
              </summary>
              <pre style={{
                marginTop: '12px',
                padding: '16px',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '6px',
                fontSize: '12px',
                overflow: 'auto',
                color: '#fecaca'
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && '\n\n' + this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default AppErrorBoundary;
