import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

/**
 * WorkflowErrorBoundary - Epic 10: Story 10.9
 */

class WorkflowErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Workflow Error:', error, errorInfo);
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
          textAlign: 'center'
        }}>
          <AlertCircle size={64} color="#ef4444" />
          <h2 style={{ marginTop: '24px', fontSize: '24px', fontWeight: '600' }}>
            Something went wrong
          </h2>
          <p style={{ marginTop: '12px', color: '#6b7280', maxWidth: '500px' }}>
            The workflow builder encountered an error. Try refreshing the page or loading a different workflow.
          </p>

          <button onClick={this.handleReset} style={{
            marginTop: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '500'
          }}>
            <RefreshCw size={20} />
            Reload Page
          </button>

          {this.state.error && (
            <details style={{ marginTop: '32px', textAlign: 'left', maxWidth: '600px' }}>
              <summary style={{ cursor: 'pointer', color: '#6b7280', fontSize: '14px' }}>
                Error Details
              </summary>
              <pre style={{
                marginTop: '12px',
                padding: '16px',
                background: '#f9fafb',
                borderRadius: '6px',
                fontSize: '12px',
                overflow: 'auto',
                color: '#ef4444'
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default WorkflowErrorBoundary;
