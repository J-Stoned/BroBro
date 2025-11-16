/**
 * Enhancement 8: AI Workflow Generator
 * Generate workflows from natural language descriptions
 */

import React, { useState, useEffect } from 'react';
import { Sparkles, Loader, ArrowRight, RefreshCw, Check, X } from 'lucide-react';
import './AIWorkflowGenerator.css';

export function AIWorkflowGenerator({ isOpen, onClose, onImport }) {
  const [step, setStep] = useState('input'); // input, generating, clarify, preview
  const [description, setDescription] = useState('');
  const [generatedWorkflow, setGeneratedWorkflow] = useState(null);
  const [clarificationQuestions, setClarificationQuestions] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const examplePrompts = [
    "Send 3 nurture emails over 5 days to new leads with product education",
    "Appointment reminder sequence: 24 hours before, 2 hours before, and follow-up after",
    "Re-engage cold leads with 2 emails over 7 days offering special discount",
    "Welcome sequence for new customers with onboarding steps and resources",
    "Abandoned cart recovery: reminder after 1 hour, discount after 24 hours"
  ];

  useEffect(() => {
    if (!isOpen) {
      // Reset when closed
      setDescription('');
      setGeneratedWorkflow(null);
      setClarificationQuestions([]);
      setStep('input');
      setError(null);
    }
  }, [isOpen]);

  const handleGenerate = async () => {
    if (!description.trim()) return;

    setIsGenerating(true);
    setError(null);
    setStep('generating');

    try {
      const response = await fetch('http://localhost:8000/api/ai/generate-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: description
        })
      });

      const data = await response.json();

      if (data.success) {
        if (data.data.clarification_needed) {
          // Need clarification
          setClarificationQuestions(data.data.questions);
          setStep('clarify');
        } else {
          // Workflow generated successfully
          setGeneratedWorkflow(data.data.workflow);
          setStep('preview');
        }
      } else {
        setError(data.data?.error || 'Generation failed');
        setStep('input');
      }
    } catch (err) {
      setError('Network error - is the backend running?');
      setStep('input');
      console.error('Generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClarificationResponse = async (answers) => {
    // Add clarification answers to description and regenerate
    const enhancedDescription = `${description}\n\nAdditional details:\n${answers.join('\n')}`;
    setDescription(enhancedDescription);
    await handleGenerate();
  };

  const handleRefine = async (refinement) => {
    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:8000/api/ai/refine-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow: generatedWorkflow,
          refinement: refinement
        })
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedWorkflow(data.data.workflow);
      }
    } catch (err) {
      console.error('Refinement error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImport = () => {
    if (generatedWorkflow) {
      onImport(generatedWorkflow);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="ai-generator-overlay" onClick={onClose}>
      <div className="ai-generator-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="generator-header">
          <div className="header-title">
            <Sparkles size={24} className="sparkle-icon" />
            <h2>Generate Workflow with AI</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Step 1: Input Description */}
        {step === 'input' && (
          <div className="generator-content">
            <div className="input-section">
              <label>Describe your workflow in plain English</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="E.g., Send 3 emails over 5 days to nurture new leads..."
                rows={4}
                autoFocus
              />

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}
            </div>

            {/* Example Prompts */}
            <div className="examples-section">
              <h3>Try these examples:</h3>
              <div className="examples-list">
                {examplePrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    className="example-prompt"
                    onClick={() => setDescription(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Button */}
            <div className="generator-actions">
              <button className="cancel-btn" onClick={onClose}>
                Cancel
              </button>
              <button
                className="generate-btn"
                onClick={handleGenerate}
                disabled={!description.trim() || isGenerating}
              >
                {isGenerating ? (
                  <>
                    <Loader className="spinner" size={18} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Generate Workflow
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Generating */}
        {step === 'generating' && (
          <div className="generator-content generating">
            <div className="generating-animation">
              <Sparkles size={48} className="sparkle-pulse" />
              <h3>Creating your workflow...</h3>
              <p>AI is analyzing your description and building the perfect automation</p>
            </div>
          </div>
        )}

        {/* Step 3: Clarification Questions */}
        {step === 'clarify' && (
          <div className="generator-content">
            <div className="clarification-section">
              <h3>Need a bit more info</h3>
              <p>To create the perfect workflow, please answer these questions:</p>

              <div className="questions-list">
                {clarificationQuestions.map((question, idx) => (
                  <div key={idx} className="question-item">
                    <label>{question}</label>
                    <input
                      type="text"
                      placeholder="Your answer..."
                      id={`question-${idx}`}
                    />
                  </div>
                ))}
              </div>

              <div className="generator-actions">
                <button className="cancel-btn" onClick={() => setStep('input')}>
                  Back
                </button>
                <button
                  className="generate-btn"
                  onClick={() => {
                    const answers = clarificationQuestions.map((_, idx) => {
                      const input = document.getElementById(`question-${idx}`);
                      return input ? input.value : '';
                    });
                    handleClarificationResponse(answers);
                  }}
                >
                  Generate with Details
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Preview Workflow */}
        {step === 'preview' && generatedWorkflow && (
          <div className="generator-content preview">
            <div className="preview-section">
              <h3>{generatedWorkflow.metadata?.name || 'Generated Workflow'}</h3>
              <p className="workflow-description">
                {generatedWorkflow.metadata?.description || description}
              </p>

              {/* Workflow Stats */}
              <div className="workflow-stats">
                <div className="stat">
                  <span className="stat-value">{generatedWorkflow.nodes?.length || 0}</span>
                  <span className="stat-label">Steps</span>
                </div>
                <div className="stat">
                  <span className="stat-value">
                    {generatedWorkflow.nodes?.filter(n => n.type === 'action').length || 0}
                  </span>
                  <span className="stat-label">Actions</span>
                </div>
                <div className="stat">
                  <span className="stat-value">
                    {generatedWorkflow.nodes?.filter(n => n.type === 'condition').length || 0}
                  </span>
                  <span className="stat-label">Conditions</span>
                </div>
              </div>

              {/* Workflow Preview - Simple list view */}
              <div className="workflow-preview">
                <h4>Workflow Steps:</h4>
                <div className="steps-list">
                  {generatedWorkflow.nodes?.map((node, idx) => (
                    <div key={node.id} className="step-item">
                      <div className="step-number">{idx + 1}</div>
                      <div className="step-content">
                        <div className="step-title">{node.data?.title || 'Untitled'}</div>
                        <div className="step-type">{node.type}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Refinement */}
              <div className="refinement-section">
                <label>Want to refine this workflow?</label>
                <div className="refinement-input">
                  <input
                    type="text"
                    placeholder="E.g., Add a 3rd email after 5 days"
                    id="refinement-input"
                  />
                  <button
                    className="refine-btn"
                    onClick={() => {
                      const input = document.getElementById('refinement-input');
                      if (input && input.value) {
                        handleRefine(input.value);
                        input.value = '';
                      }
                    }}
                    disabled={isGenerating}
                  >
                    {isGenerating ? (
                      <Loader className="spinner" size={16} />
                    ) : (
                      <RefreshCw size={16} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="generator-actions">
              <button className="cancel-btn" onClick={() => setStep('input')}>
                Start Over
              </button>
              <button className="import-btn" onClick={handleImport}>
                <Check size={18} />
                Import Workflow
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
