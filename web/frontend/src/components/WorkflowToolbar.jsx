import React from 'react';
import {
  Save, Download, Upload, Undo, Redo, ZoomIn, ZoomOut,
  Maximize2, Grid, Plus, FileJson, FileText, Cloud, CheckCircle, Zap, Sparkles, GitCommit, HelpCircle
} from 'lucide-react';

/**
 * WorkflowToolbar Component
 * Epic 10: Story 10.1
 *
 * Top toolbar with file operations, edit controls, and view options
 */

const WorkflowToolbar = ({
  onSave,
  onExportJSON,
  onExportDeployment,
  onImport,
  onImportFromGHL,
  onUndo,
  onRedo,
  onFitToScreen,
  onToggleGrid,
  onAddNode,
  onValidate,
  onTest,
  onGenerateWithAI,
  onVersionHistory,
  onShowHelp,
  canUndo = false,
  canRedo = false,
  isDirty = false
}) => {
  return (
    <div className="workflow-toolbar" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '8px 16px',
      background: 'white',
      borderBottom: '1px solid #e5e7eb'
    }}>
      {/* File operations */}
      <div className="toolbar-group" style={{ display: 'flex', gap: '4px', paddingRight: '12px', borderRight: '1px solid #e5e7eb' }}>
        <ToolbarButton
          icon={<Save size={16} />}
          label="Save"
          onClick={onSave}
          disabled={!isDirty}
          title="Save workflow (Ctrl+S)"
        />
        <ToolbarButton
          icon={<FileJson size={16} />}
          label="Export JSON"
          onClick={onExportJSON}
          title="Download as JSON"
        />
        <ToolbarButton
          icon={<FileText size={16} />}
          label="Deploy"
          onClick={onExportDeployment}
          title="Get deployment guide"
        />
        <ToolbarButton
          icon={<Upload size={16} />}
          label="Import"
          onClick={onImport}
          title="Load workflow from JSON"
        />
        <ToolbarButton
          icon={<Cloud size={16} />}
          label="Import GHL"
          onClick={onImportFromGHL}
          title="Import workflow from GHL account"
        />
      </div>

      {/* Edit operations */}
      <div className="toolbar-group" style={{ display: 'flex', gap: '4px', paddingRight: '12px', borderRight: '1px solid #e5e7eb' }}>
        <ToolbarButton
          icon={<Undo size={16} />}
          label="Undo"
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo (Ctrl+Z)"
        />
        <ToolbarButton
          icon={<Redo size={16} />}
          label="Redo"
          onClick={onRedo}
          disabled={!canRedo}
          title="Redo (Ctrl+Y)"
        />
      </div>

      {/* View operations */}
      <div className="toolbar-group" style={{ display: 'flex', gap: '4px', paddingRight: '12px', borderRight: '1px solid #e5e7eb' }}>
        <ToolbarButton
          icon={<Maximize2 size={16} />}
          label="Fit"
          onClick={onFitToScreen}
          title="Fit to screen"
        />
        <ToolbarButton
          icon={<Grid size={16} />}
          label="Grid"
          onClick={onToggleGrid}
          title="Toggle grid"
        />
      </div>

      {/* Add node */}
      <div className="toolbar-group" style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={onAddNode}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '500'
          }}
          title="Add new node"
        >
          <Plus size={16} />
          <span>Add Node</span>
        </button>

        {/* Enhancement 4: Validate button */}
        {onValidate && (
          <button
            onClick={onValidate}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
            title="Validate workflow best practices"
          >
            <CheckCircle size={16} />
            <span>Validate</span>
          </button>
        )}

        {/* Enhancement 5: Test Workflow button */}
        {onTest && (
          <button
            onClick={onTest}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              background: '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
            title="Test workflow with mock contact data"
          >
            <Zap size={16} />
            <span>Test Workflow</span>
          </button>
        )}

        {/* Enhancement 8: Generate with AI button */}
        {onGenerateWithAI && (
          <button
            onClick={onGenerateWithAI}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              boxShadow: '0 2px 4px rgba(102, 126, 234, 0.3)'
            }}
            title="Generate workflow with AI"
          >
            <Sparkles size={16} />
            <span>Generate with AI</span>
          </button>
        )}

        {/* Enhancement 9: Version History button */}
        {onVersionHistory && (
          <ToolbarButton
            icon={<GitCommit size={16} />}
            label="History"
            onClick={onVersionHistory}
            title="View version history"
          />
        )}

        {/* Enhancement 7: Help button */}
        {onShowHelp && (
          <ToolbarButton
            icon={<HelpCircle size={16} />}
            label="Help"
            onClick={onShowHelp}
            title="Keyboard shortcuts (Shift+?)"
          />
        )}
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Save indicator */}
      {isDirty && (
        <div style={{
          fontSize: '12px',
          color: '#f59e0b',
          fontWeight: '500'
        }}>
          • Unsaved changes
        </div>
      )}
    </div>
  );
};

const ToolbarButton = ({ icon, label, onClick, disabled = false, title }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        padding: '6px 10px',
        background: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '6px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        fontSize: '13px',
        color: '#374151',
        transition: 'all 0.2s'
      }}
      onMouseOver={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = '#f9fafb';
          e.currentTarget.style.borderColor = '#d1d5db';
        }
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'white';
        e.currentTarget.style.borderColor = '#e5e7eb';
      }}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
};

export default WorkflowToolbar;
