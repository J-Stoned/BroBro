/**
 * TestWorkflowPanel Component
 * Enhancement 5: Interactive Workflow Testing with Mock Data
 *
 * Allows users to test workflows with mock contact personas
 * Shows step-by-step execution with variable substitution
 */

import React, { useState, useEffect } from 'react';
import { Play, Square, RotateCcw, User, Zap, X } from 'lucide-react';
import { MockContactSelector } from './MockContactSelector';
import { ExecutionLog } from './ExecutionLog';
import './TestWorkflowPanel.css';

export function TestWorkflowPanel({ workflow, isOpen, onClose, onHighlightNode }) {
  const [mockContacts, setMockContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [executionLog, setExecutionLog] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [testResults, setTestResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchMockContacts();
    }
  }, [isOpen]);

  const fetchMockContacts = async () => {
    try {
      const response = await fetch('/api/workflows/mock-contacts');
      const data = await response.json();

      if (data.success) {
        setMockContacts(data.data.contacts);
        setSelectedContact(data.data.contacts[0]); // Select first by default
      }
    } catch (err) {
      console.error('Fetch mock contacts error:', err);
      setError('Failed to load mock contacts');
    }
  };

  const startTest = async () => {
    if (!selectedContact) return;

    setIsRunning(true);
    setIsComplete(false);
    setExecutionLog([]);
    setCurrentStep(0);
    setTestResults(null);
    setError(null);

    try {
      const response = await fetch('/api/workflows/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nodes: workflow.nodes || [],
          connections: workflow.connections || [],
          metadata: workflow.metadata || {},
          mock_contact_id: selectedContact.id,
          speed_multiplier: 1000
        })
      });

      const data = await response.json();

      if (data.success) {
        // Animate execution log
        animateExecutionLog(data.data.execution_log);
        setTestResults(data.data);
      } else {
        setError(data.error || 'Test failed');
        setIsRunning(false);
      }
    } catch (err) {
      console.error('Test execution error:', err);
      setError('Network error during test');
      setIsRunning(false);
    }
  };

  const animateExecutionLog = (log) => {
    let index = 0;

    const interval = setInterval(() => {
      if (index < log.length) {
        const step = log[index];
        setExecutionLog(prev => [...prev, step]);
        setCurrentStep(index + 1);

        // Highlight current node on canvas
        if (onHighlightNode) {
          onHighlightNode(step.node_id);
        }

        index++;
      } else {
        clearInterval(interval);
        setIsRunning(false);
        setIsComplete(true);
        if (onHighlightNode) {
          onHighlightNode(null);
        }
      }
    }, 800); // 800ms between steps for smooth animation
  };

  const stopTest = () => {
    setIsRunning(false);
    if (onHighlightNode) {
      onHighlightNode(null);
    }
  };

  const replayTest = () => {
    setExecutionLog([]);
    setCurrentStep(0);
    setIsComplete(false);
    startTest();
  };

  if (!isOpen) return null;

  return (
    <div className="test-panel-overlay" onClick={onClose}>
      <div className="test-workflow-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="test-panel-header">
          <div className="header-title">
            <Zap size={24} />
            <h2>Test Workflow</h2>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="test-error">
            <p>{error}</p>
          </div>
        )}

        {/* Mock Contact Selector */}
        {mockContacts.length > 0 && (
          <MockContactSelector
            contacts={mockContacts}
            selected={selectedContact}
            onSelect={setSelectedContact}
            disabled={isRunning}
          />
        )}

        {/* Controls */}
        <div className="test-controls">
          <button
            className="start-test-btn"
            onClick={startTest}
            disabled={isRunning || !selectedContact || !workflow.nodes || workflow.nodes.length === 0}
          >
            <Play size={18} />
            {isRunning ? 'Running...' : 'Start Test'}
          </button>

          {isRunning && (
            <button className="stop-test-btn" onClick={stopTest}>
              <Square size={18} />
              Stop
            </button>
          )}

          {isComplete && (
            <button className="replay-btn" onClick={replayTest}>
              <RotateCcw size={18} />
              Replay
            </button>
          )}
        </div>

        {/* Progress */}
        {executionLog.length > 0 && (
          <div className="test-progress">
            <div className="progress-text">
              Step {currentStep} of {workflow.nodes?.length || 0}
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${(currentStep / (workflow.nodes?.length || 1)) * 100}%`
                }}
              />
            </div>
          </div>
        )}

        {/* Execution Log */}
        <ExecutionLog
          log={executionLog}
          isRunning={isRunning}
          isComplete={isComplete}
        />

        {/* Results Summary */}
        {isComplete && testResults && (
          <div className="test-results">
            <h3>Test Complete</h3>
            <div className="results-stats">
              <div className="stat">
                <span className="label">Nodes Executed:</span>
                <span className="value">{testResults.nodes_executed}</span>
              </div>
              <div className="stat">
                <span className="label">Time Simulated:</span>
                <span className="value">{testResults.total_time_simulated}</span>
              </div>
              <div className="stat">
                <span className="label">Actual Duration:</span>
                <span className="value">{testResults.execution_time_actual}</span>
              </div>
            </div>

            {/* Final Contact State */}
            <div className="final-state">
              <h4>Final Contact State</h4>
              <div className="state-item">
                <span className="key">Tags:</span>
                <span className="value">
                  {testResults.final_state.tags?.join(', ') || 'None'}
                </span>
              </div>
              <div className="state-item">
                <span className="key">Emails Received:</span>
                <span className="value">{testResults.final_state.emails_received || 0}</span>
              </div>
              <div className="state-item">
                <span className="key">SMS Received:</span>
                <span className="value">{testResults.final_state.sms_received || 0}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
