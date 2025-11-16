import React, { useState, useEffect, useCallback, useRef } from 'react';
import WorkflowCanvas from './WorkflowCanvas';
import WorkflowToolbar from './WorkflowToolbar';
import WorkflowPropertiesPanel from './WorkflowPropertiesPanel';
import DeploymentPanel from './DeploymentPanel';
import DeploymentGuideModal from './DeploymentGuideModal';
import WorkflowImporter from './WorkflowImporter';
import { ValidationPanel } from './workflow/ValidationPanel';
import { TestWorkflowPanel } from './workflow/TestWorkflowPanel';
import { AIWorkflowGenerator } from './workflows/AIWorkflowGenerator';
import { VersionHistory } from './workflows/VersionHistory';
import { ActiveUsers } from './workflows/ActiveUsers';
import { CollaboratorCursor } from './workflows/CollaboratorCursor';
import { useCollaboration } from '../hooks/useCollaboration';
import { useKeyboardShortcutsArray } from '../hooks/useKeyboardShortcuts';
import { CommandPalette } from './CommandPalette';
import { ShortcutsHelp } from './ShortcutsHelp';
import { SHORTCUTS } from '../constants/shortcuts';
import { applyWorkflowFix } from '../lib/workflowFixes';
import { createWorkflow, addNode, updateNode, deleteNode, validateWorkflow, exportWorkflow } from '../lib/workflowState';
import { downloadAsJSON } from '../lib/workflowExporter';
import { getSampleWorkflow } from '../data/sampleWorkflows';
import './WorkflowBuilder.css';

/**
 * WorkflowBuilder Component
 * Epic 10: Story 10.1
 *
 * Main workflow builder container with canvas, toolbar, and properties panel
 */

const WorkflowBuilder = ({
  initialWorkflow = null,
  onSave,
  readonly = false
}) => {
  const [workflow, setWorkflow] = useState(null);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [showDeploymentGuide, setShowDeploymentGuide] = useState(false);
  const [showWorkflowImporter, setShowWorkflowImporter] = useState(false);
  const [showValidationPanel, setShowValidationPanel] = useState(false);
  const [showTestPanel, setShowTestPanel] = useState(false);
  const [highlightedNodeId, setHighlightedNodeId] = useState(null);
  const [showAIGenerator, setShowAIGenerator] = useState(false);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [currentBranch, setCurrentBranch] = useState('main');
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false);
  const canvasRef = useRef(null);

  // Enhancement 9: Collaboration
  const workflowId = workflow?.metadata?.id || 'demo-workflow';
  const userId = 'user-' + Math.random().toString(36).substring(7);
  const userName = 'Demo User';

  const collaboration = useCollaboration(workflowId, userId, userName);

  // Initialize workflow
  useEffect(() => {
    try {
      if (initialWorkflow) {
        setWorkflow(initialWorkflow);
        addToHistory(initialWorkflow);
      } else {
        // Load sample workflow for testing
        const sample = getSampleWorkflow('leadNurture');
        if (sample) {
          setWorkflow(sample);
          addToHistory(sample);
        } else {
          // Create blank workflow
          const blank = createWorkflow({
            name: 'New Workflow',
            description: 'Describe your workflow'
          });
          setWorkflow(blank);
          addToHistory(blank);
        }
      }
    } catch (error) {
      console.error('Error initializing workflow:', error);
      // Create a minimal safe workflow as fallback
      try {
        const fallback = createWorkflow({
          name: 'New Workflow',
          description: 'Describe your workflow'
        });
        setWorkflow(fallback);
        addToHistory(fallback);
      } catch (fallbackError) {
        console.error('Critical error - cannot create workflow:', fallbackError);
        // Set a completely minimal workflow
        setWorkflow({
          nodes: [],
          connections: [],
          metadata: { name: 'New Workflow', description: '' }
        });
      }
    }
  }, [initialWorkflow]);

  // Auto-save to localStorage
  useEffect(() => {
    if (workflow && isDirty) {
      const timeoutId = setTimeout(() => {
        try {
          localStorage.setItem('brobro-workflow-draft', JSON.stringify(workflow));
        } catch (err) {
          console.error('Failed to auto-save workflow:', err);
        }
      }, 5000);

      return () => clearTimeout(timeoutId);
    }
  }, [workflow, isDirty]);

  // Add to history for undo/redo
  const addToHistory = useCallback((newWorkflow) => {
    setHistory(prev => {
      const newHistory = prev.slice(0, historyIndex + 1);
      newHistory.push(newWorkflow);

      // Limit history to 50 items
      if (newHistory.length > 50) {
        newHistory.shift();
        return newHistory;
      }

      return newHistory;
    });
    setHistoryIndex(prev => Math.min(prev + 1, 49));
  }, [historyIndex]);

  // Undo
  const handleUndo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
      setWorkflow(history[historyIndex - 1]);
      setIsDirty(true);
    }
  };

  // Redo
  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1);
      setWorkflow(history[historyIndex + 1]);
      setIsDirty(true);
    }
  };

  // Handle node selection
  const handleNodeSelect = (nodeId) => {
    setSelectedNodeId(nodeId);
  };

  // Handle node move
  const handleNodeMove = (nodeId, newPosition) => {
    if (readonly || !workflow) return;

    const updatedWorkflow = updateNode(workflow, nodeId, {
      position: newPosition
    });

    setWorkflow(updatedWorkflow);
    setIsDirty(true);
    addToHistory(updatedWorkflow);
  };

  // Handle node update
  const handleNodeUpdate = (nodeId, updates) => {
    if (readonly || !workflow) return;

    const updatedWorkflow = updateNode(workflow, nodeId, updates);
    setWorkflow(updatedWorkflow);
    setIsDirty(true);
    addToHistory(updatedWorkflow);
  };

  // Handle node delete
  const handleNodeDelete = (nodeId) => {
    if (readonly || !workflow) return;

    if (window.confirm('Delete this node?')) {
      const updatedWorkflow = deleteNode(workflow, nodeId);
      setWorkflow(updatedWorkflow);
      setSelectedNodeId(null);
      setIsDirty(true);
      addToHistory(updatedWorkflow);
    }
  };

  // Handle node duplicate
  const handleNodeDuplicate = (nodeId) => {
    if (readonly || !workflow) return;

    const nodeToDuplicate = workflow.nodes.find(n => n.id === nodeId);
    if (!nodeToDuplicate) return;

    const updatedWorkflow = addNode(
      workflow,
      nodeToDuplicate.type,
      {
        x: nodeToDuplicate.position.x + 50,
        y: nodeToDuplicate.position.y + 50
      },
      {
        title: `${nodeToDuplicate.title} (Copy)`,
        description: nodeToDuplicate.description,
        params: { ...nodeToDuplicate.params }
      }
    );

    setWorkflow(updatedWorkflow);
    setIsDirty(true);
    addToHistory(updatedWorkflow);
  };

  // Handle workflow update
  const handleWorkflowUpdate = (updatedWorkflow) => {
    setWorkflow(updatedWorkflow);
    setIsDirty(true);
    addToHistory(updatedWorkflow);
  };

  // Handle save
  const handleSave = () => {
    if (!workflow) return;

    const validation = validateWorkflow(workflow);

    if (!validation.valid) {
      alert(`Workflow has errors:\n${validation.errors.map(e => e.message).join('\n')}`);
      return;
    }

    if (validation.warnings.length > 0) {
      const proceed = window.confirm(
        `Workflow has warnings:\n${validation.warnings.map(w => w.message).join('\n')}\n\nSave anyway?`
      );
      if (!proceed) return;
    }

    setIsDirty(false);

    if (onSave) {
      onSave(workflow);
    }

    // Save to localStorage
    try {
      localStorage.setItem('brobro-workflow-saved', JSON.stringify(workflow));
      alert('Workflow saved successfully!');
    } catch (err) {
      console.error('Failed to save workflow:', err);
      alert('Failed to save workflow');
    }
  };

  // Handle export JSON
  const handleExportJSON = () => {
    if (!workflow) return;
    downloadAsJSON(workflow);
  };

  // Handle export deployment
  const handleExportDeployment = () => {
    setShowDeploymentGuide(true);
  };

  // Handle import
  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const imported = JSON.parse(event.target.result);
          setWorkflow(imported);
          setIsDirty(false);
          addToHistory(imported);
          alert('Workflow imported successfully!');
        } catch (err) {
          alert(`Failed to import workflow: ${err.message}`);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  // Handle import from GHL
  const handleImportFromGHL = () => {
    setShowWorkflowImporter(true);
  };

  // Handle GHL workflow import
  const handleGHLWorkflowImport = (importedWorkflow) => {
    setWorkflow(importedWorkflow);
    setIsDirty(false);
    addToHistory(importedWorkflow);
    alert(`Workflow "${importedWorkflow.name}" imported successfully from GHL!`);
  };

  // Handle add node (placeholder)
  const handleAddNode = () => {
    alert('Add node menu coming soon! For now, use templates or import workflows.');
  };

  // Enhancement 4: Handle workflow validation
  const handleValidateWorkflow = () => {
    setShowValidationPanel(true);
  };

  // Enhancement 4: Handle applying workflow fixes
  const handleApplyFix = async (issue) => {
    try {
      const updatedWorkflow = applyWorkflowFix(workflow, issue);
      setWorkflow(updatedWorkflow);
      setIsDirty(true);
      addToHistory(updatedWorkflow);
    } catch (err) {
      console.error('Failed to apply fix:', err);
      alert(`Failed to apply fix: ${err.message}`);
    }
  };

  // Enhancement 5: Handle workflow testing
  const handleTestWorkflow = () => {
    setShowTestPanel(true);
  };

  // Enhancement 5: Handle node highlighting during test execution
  const handleNodeHighlight = (nodeId) => {
    setHighlightedNodeId(nodeId);
    setSelectedNodeId(nodeId);
  };

  // Enhancement 8: Handle AI workflow generation
  const handleGenerateWithAI = () => {
    setShowAIGenerator(true);
  };

  // Enhancement 8: Handle importing AI-generated workflow
  const handleAIImport = (generatedWorkflow) => {
    setWorkflow(generatedWorkflow);
    setIsDirty(true);
    addToHistory(generatedWorkflow);
  };

  // Enhancement 9: Handle version control commit
  const handleCommit = async (message) => {
    try {
      const response = await fetch('http://localhost:8000/api/version-control/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflowId,
          workflow_data: workflow,
          message: message,
          author: userName,
          branch: currentBranch
        })
      });

      const data = await response.json();
      if (data.success) {
        setIsDirty(false);
        alert('Workflow committed successfully!');
      }
    } catch (err) {
      console.error('Commit failed:', err);
      alert('Failed to commit workflow');
    }
  };

  // Enhancement 9: Handle workflow restore from version history
  const handleRestore = (restoredWorkflow) => {
    setWorkflow(restoredWorkflow);
    setIsDirty(true);
    addToHistory(restoredWorkflow);
    setShowVersionHistory(false);
  };

  // Enhancement 9: Track cursor movement
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (collaboration.isConnected) {
        collaboration.updateCursor(e.clientX, e.clientY);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [collaboration]);

  // Enhancement 7: Define actions for Command Palette and shortcuts
  const actions = {
    createWorkflow: () => {
      const blank = createWorkflow({ name: 'New Workflow', description: 'Describe your workflow' });
      setWorkflow(blank);
      setIsDirty(true);
      addToHistory(blank);
    },
    saveWorkflow: handleSave,
    testWorkflow: handleTestWorkflow,
    validateWorkflow: handleValidateWorkflow,
    exportWorkflow: handleExportJSON,
    importWorkflow: () => setShowWorkflowImporter(true),
    generateWithAI: () => setShowAIGenerator(true),
    showVersionHistory: () => setShowVersionHistory(true),
    undo: handleUndo,
    redo: handleRedo,
    copyNode: () => {
      if (selectedNodeId) {
        const node = workflow.nodes.find(n => n.id === selectedNodeId);
        if (node) {
          localStorage.setItem('copiedNode', JSON.stringify(node));
        }
      }
    },
    pasteNode: () => {
      const copied = localStorage.getItem('copiedNode');
      if (copied) {
        try {
          const node = JSON.parse(copied);
          const newNode = { ...node, id: `node-${Date.now()}`, position: { x: node.position.x + 50, y: node.position.y + 50 } };
          handleAddNode(newNode.type, newNode);
        } catch (err) {
          console.error('Failed to paste node:', err);
        }
      }
    },
    deleteNode: () => selectedNodeId && handleNodeDelete(selectedNodeId),
    fitToScreen: () => canvasRef.current?.fitToScreen(),
    toggleGrid: () => setShowGrid(!showGrid),
    showShortcutsHelp: () => setShowShortcutsHelp(true),
    openSearch: () => window.location.href = '/search'
  };

  // Enhancement 7: Register keyboard shortcuts
  useKeyboardShortcutsArray('workflow', [
    { config: SHORTCUTS.workflow.SAVE, handler: actions.saveWorkflow },
    { config: SHORTCUTS.workflow.TEST, handler: actions.testWorkflow },
    { config: SHORTCUTS.workflow.NEW, handler: actions.createWorkflow },
    { config: SHORTCUTS.workflow.DELETE, handler: actions.deleteNode },
    { config: SHORTCUTS.workflow.UNDO, handler: actions.undo },
    { config: SHORTCUTS.workflow.REDO, handler: actions.redo },
    { config: SHORTCUTS.workflow.COPY, handler: actions.copyNode },
    { config: SHORTCUTS.workflow.PASTE, handler: actions.pasteNode },
    { config: SHORTCUTS.global.COMMAND_PALETTE, handler: () => setShowCommandPalette(true) },
    { config: SHORTCUTS.global.HELP, handler: () => setShowShortcutsHelp(true) },
    { config: SHORTCUTS.global.ESCAPE, handler: () => {
      // Close any open modal
      if (showCommandPalette) setShowCommandPalette(false);
      else if (showShortcutsHelp) setShowShortcutsHelp(false);
      else if (showAIGenerator) setShowAIGenerator(false);
      else if (showVersionHistory) setShowVersionHistory(false);
      else if (showValidationPanel) setShowValidationPanel(false);
      else if (showTestPanel) setShowTestPanel(false);
    }}
  ], [
    handleSave,
    handleTestWorkflow,
    handleValidateWorkflow,
    handleUndo,
    handleRedo,
    selectedNodeId,
    showGrid,
    showCommandPalette,
    showShortcutsHelp,
    showAIGenerator,
    showVersionHistory,
    showValidationPanel,
    showTestPanel
  ]);

  if (!workflow) {
    return (
      <div className="workflow-builder-loading">
        <div>Loading workflow...</div>
      </div>
    );
  }

  const selectedNode = selectedNodeId
    ? workflow.nodes.find(n => n.id === selectedNodeId)
    : null;

  return (
    <div className="workflow-builder">
      {/* Toolbar */}
      <WorkflowToolbar
        onSave={handleSave}
        onExportJSON={handleExportJSON}
        onExportDeployment={handleExportDeployment}
        onImport={handleImport}
        onImportFromGHL={handleImportFromGHL}
        onUndo={handleUndo}
        onRedo={handleRedo}
        onFitToScreen={() => canvasRef.current?.fitToScreen()}
        onToggleGrid={() => setShowGrid(!showGrid)}
        onAddNode={handleAddNode}
        onValidate={handleValidateWorkflow}
        onTest={handleTestWorkflow}
        onGenerateWithAI={handleGenerateWithAI}
        onVersionHistory={() => setShowVersionHistory(true)}
        onShowHelp={() => setShowShortcutsHelp(true)}
        canUndo={historyIndex > 0}
        canRedo={historyIndex < history.length - 1}
        isDirty={isDirty}
      />

      <div className="workflow-builder-content">
        {/* Canvas */}
        <div className="workflow-canvas-wrapper">
          <WorkflowCanvas
            ref={canvasRef}
            workflow={workflow}
            selectedNodeId={selectedNodeId}
            onNodeSelect={handleNodeSelect}
            onNodeMove={handleNodeMove}
            onConnectionSelect={() => {}}
            readonly={readonly}
          />
        </div>

        {/* Right Sidebar */}
        <div className="workflow-right-sidebar">
          {/* Deployment Panel */}
          <div style={{ marginBottom: '16px' }}>
            <DeploymentPanel
              workflow={workflow}
              onDeploymentSuccess={(data) => {
                alert(`Workflow deployed successfully!\nWorkflow ID: ${data.workflow_id}`);
                setIsDirty(false);
              }}
              onDeploymentError={(error) => {
                console.error('Deployment failed:', error);
              }}
            />
          </div>

          {/* Properties Panel */}
          <WorkflowPropertiesPanel
            workflow={workflow}
            selectedNode={selectedNode}
            onUpdateNode={handleNodeUpdate}
            onDeleteNode={handleNodeDelete}
            onDuplicateNode={handleNodeDuplicate}
            onUpdateWorkflow={handleWorkflowUpdate}
            onClose={() => setSelectedNodeId(null)}
          />
        </div>
      </div>

      {/* Status Bar */}
      <div className="workflow-status-bar">
        <div className="status-left">
          <span>{workflow.name}</span>
          <span className="separator">•</span>
          <span>{workflow.nodes.length} nodes</span>
          <span className="separator">•</span>
          <span>{workflow.connections.length} connections</span>
        </div>
        <div className="status-right">
          {isDirty && <span className="status-unsaved">● Unsaved changes</span>}
        </div>
      </div>

      {/* Deployment Guide Modal */}
      {showDeploymentGuide && (
        <DeploymentGuideModal
          workflow={workflow}
          onClose={() => setShowDeploymentGuide(false)}
        />
      )}

      {/* Workflow Importer Modal */}
      {showWorkflowImporter && (
        <WorkflowImporter
          onImport={handleGHLWorkflowImport}
          onClose={() => setShowWorkflowImporter(false)}
        />
      )}

      {/* Enhancement 4: Validation Panel Modal */}
      <ValidationPanel
        workflow={workflow}
        isVisible={showValidationPanel}
        onClose={() => setShowValidationPanel(false)}
        onApplyFix={handleApplyFix}
      />

      {/* Enhancement 5: Test Workflow Panel Modal */}
      <TestWorkflowPanel
        workflow={workflow}
        isVisible={showTestPanel}
        onClose={() => {
          setShowTestPanel(false);
          setHighlightedNodeId(null);
        }}
        onHighlightNode={handleNodeHighlight}
      />

      {/* Enhancement 8: AI Workflow Generator Modal */}
      <AIWorkflowGenerator
        isOpen={showAIGenerator}
        onClose={() => setShowAIGenerator(false)}
        onImport={handleAIImport}
      />

      {/* Enhancement 9: Active Users Sidebar */}
      <ActiveUsers
        users={collaboration.activeUsers}
        currentUserId={userId}
      />

      {/* Enhancement 9: Collaborator Cursors */}
      <CollaboratorCursor
        cursorPositions={collaboration.cursorPositions}
      />

      {/* Enhancement 9: Version History Panel */}
      {showVersionHistory && (
        <VersionHistory
          workflowId={workflowId}
          currentBranch={currentBranch}
          onRestore={handleRestore}
          onClose={() => setShowVersionHistory(false)}
        />
      )}

      {/* Enhancement 7: Command Palette */}
      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        actions={actions}
      />

      {/* Enhancement 7: Shortcuts Help */}
      <ShortcutsHelp
        isOpen={showShortcutsHelp}
        onClose={() => setShowShortcutsHelp(false)}
      />
    </div>
  );
};

export default WorkflowBuilder;
