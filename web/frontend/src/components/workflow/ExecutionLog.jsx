/**
 * ExecutionLog Component
 * Enhancement 5: Workflow Testing
 *
 * Displays step-by-step execution log with auto-scroll
 */

import React, { useRef, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';

export function ExecutionLog({ log, isRunning, isComplete }) {
  const logEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={16} className="status-icon success" />;
      case 'failed':
        return <XCircle size={16} className="status-icon error" />;
      case 'skipped':
        return <AlertCircle size={16} className="status-icon warning" />;
      default:
        return <Clock size={16} className="status-icon" />;
    }
  };

  return (
    <div className="execution-log">
      <h3>Execution Log</h3>

      {log.length === 0 && !isRunning && (
        <div className="log-empty">
          <p>Click "Start Test" to begin workflow simulation</p>
        </div>
      )}

      <div className="log-entries">
        {log.map((entry, idx) => (
          <div key={idx} className={`log-entry status-${entry.status}`}>
            <div className="entry-header">
              {getStatusIcon(entry.status)}
              <span className="entry-title">{entry.node_title}</span>
              <span className="entry-type">{entry.node_type}</span>
            </div>

            <div className="entry-result">{entry.result}</div>

            {entry.details && Object.keys(entry.details).length > 0 && (
              <div className="entry-details">
                {entry.details.message_preview && (
                  <div className="detail-item message-preview">
                    <strong>Message:</strong>
                    <p>{entry.details.message_preview}</p>
                  </div>
                )}

                {entry.details.subject && (
                  <div className="detail-item">
                    <strong>Subject:</strong> {entry.details.subject}
                  </div>
                )}

                {entry.details.to && (
                  <div className="detail-item">
                    <strong>To:</strong> {entry.details.to}
                  </div>
                )}

                {entry.details.result && (
                  <div className="detail-item condition-result">
                    <strong>Result:</strong>{' '}
                    <span className={`result-badge ${entry.details.result.toLowerCase()}`}>
                      {entry.details.result}
                    </span>
                  </div>
                )}

                {entry.details.reason && (
                  <div className="detail-item">
                    <strong>Reason:</strong> {entry.details.reason}
                  </div>
                )}

                {entry.details.tag && (
                  <div className="detail-item">
                    <strong>Tag:</strong> {entry.details.tag}
                  </div>
                )}

                {entry.details.action_type && (
                  <div className="detail-item">
                    <strong>Action:</strong> {entry.details.action_type}
                  </div>
                )}
              </div>
            )}

            <div className="entry-timestamp">
              {new Date(entry.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}

        <div ref={logEndRef} />
      </div>

      {isRunning && (
        <div className="log-running">
          <div className="spinner" />
          <span>Executing workflow...</span>
        </div>
      )}

      {isComplete && (
        <div className="log-complete">
          <CheckCircle size={20} />
          <span>Test completed successfully!</span>
        </div>
      )}
    </div>
  );
}
