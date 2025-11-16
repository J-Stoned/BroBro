import React, { useState, useEffect } from 'react';
import { Trash2, Copy, X } from 'lucide-react';
import ConditionBuilder from './workflow/ConditionBuilder';

/**
 * WorkflowPropertiesPanel Component
 * Epic 10: Story 10.1
 * Epic 12: Story 12.1 - Added ConditionBuilder integration
 *
 * Right sidebar showing workflow info or selected node properties
 */

const WorkflowPropertiesPanel = ({
  workflow,
  selectedNode,
  onUpdateNode,
  onDeleteNode,
  onDuplicateNode,
  onUpdateWorkflow,
  onClose
}) => {
  const [localNodeData, setLocalNodeData] = useState(null);

  useEffect(() => {
    if (selectedNode) {
      setLocalNodeData({ ...selectedNode });
    } else {
      setLocalNodeData(null);
    }
  }, [selectedNode]);

  const handleNodeFieldChange = (field, value) => {
    setLocalNodeData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNodeParamChange = (paramKey, value) => {
    setLocalNodeData(prev => ({
      ...prev,
      params: {
        ...prev.params,
        [paramKey]: value
      }
    }));
  };

  const handleSaveNode = () => {
    if (localNodeData && onUpdateNode) {
      onUpdateNode(localNodeData.id, localNodeData);
    }
  };

  const handleWorkflowFieldChange = (field, value) => {
    if (onUpdateWorkflow) {
      onUpdateWorkflow({
        ...workflow,
        [field]: value
      });
    }
  };

  // If node selected, show node properties
  if (selectedNode && localNodeData) {
    return (
      <div className="workflow-properties-panel" style={{
        width: '300px',
        height: '100%',
        background: 'white',
        borderLeft: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', margin: 0 }}>
            Node Properties
          </h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex'
            }}
          >
            <X size={18} color="#6b7280" />
          </button>
        </div>

        {/* Scrollable content */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px'
        }}>
          {/* Node Type */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              marginBottom: '6px',
              textTransform: 'uppercase'
            }}>
              Type
            </label>
            <div style={{
              padding: '8px 12px',
              background: '#f9fafb',
              borderRadius: '6px',
              fontSize: '14px',
              color: '#374151',
              textTransform: 'capitalize'
            }}>
              {localNodeData.type}
            </div>
          </div>

          {/* Node Title */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              marginBottom: '6px',
              textTransform: 'uppercase'
            }}>
              Title
            </label>
            <input
              type="text"
              value={localNodeData.title}
              onChange={(e) => handleNodeFieldChange('title', e.target.value)}
              onBlur={handleSaveNode}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '14px',
                fontFamily: 'inherit'
              }}
            />
          </div>

          {/* Node Description */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              marginBottom: '6px',
              textTransform: 'uppercase'
            }}>
              Description
            </label>
            <textarea
              value={localNodeData.description || ''}
              onChange={(e) => handleNodeFieldChange('description', e.target.value)}
              onBlur={handleSaveNode}
              rows={3}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '14px',
                fontFamily: 'inherit',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Condition Builder for condition nodes */}
          {localNodeData.type === 'condition' && (
            <div style={{ marginBottom: '16px' }}>
              <ConditionBuilder
                conditions={localNodeData.conditions || []}
                onChange={(conditions, logicOperator) => {
                  setLocalNodeData(prev => ({
                    ...prev,
                    conditions,
                    logicOperator
                  }));
                  // Auto-save
                  if (onUpdateNode) {
                    onUpdateNode(localNodeData.id, {
                      ...localNodeData,
                      conditions,
                      logicOperator
                    });
                  }
                }}
                availableVariables={workflow.variables || []}
              />
            </div>
          )}

          {/* Node Parameters */}
          {localNodeData.params && Object.keys(localNodeData.params).length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#6b7280',
                marginBottom: '10px',
                textTransform: 'uppercase'
              }}>
                Parameters
              </label>
              {Object.entries(localNodeData.params).map(([key, value]) => (
                <div key={key} style={{ marginBottom: '12px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    color: '#6b7280',
                    marginBottom: '4px',
                    textTransform: 'capitalize'
                  }}>
                    {key.replace(/_/g, ' ')}
                  </label>
                  {typeof value === 'boolean' ? (
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => handleNodeParamChange(key, e.target.checked)}
                      onBlur={handleSaveNode}
                      style={{ width: '20px', height: '20px', cursor: 'pointer' }}
                    />
                  ) : typeof value === 'number' ? (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => handleNodeParamChange(key, parseInt(e.target.value) || 0)}
                      onBlur={handleSaveNode}
                      style={{
                        width: '100%',
                        padding: '6px 10px',
                        border: '1px solid #e5e7eb',
                        borderRadius: '4px',
                        fontSize: '13px'
                      }}
                    />
                  ) : (
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => handleNodeParamChange(key, e.target.value)}
                      onBlur={handleSaveNode}
                      style={{
                        width: '100%',
                        padding: '6px 10px',
                        border: '1px solid #e5e7eb',
                        borderRadius: '4px',
                        fontSize: '13px'
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Node Position */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              marginBottom: '6px',
              textTransform: 'uppercase'
            }}>
              Position
            </label>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '8px'
            }}>
              <div>
                <label style={{ fontSize: '11px', color: '#9ca3af', display: 'block', marginBottom: '4px' }}>X</label>
                <input
                  type="number"
                  value={localNodeData.position.x}
                  readOnly
                  style={{
                    width: '100%',
                    padding: '6px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '13px',
                    background: '#f9fafb'
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#9ca3af', display: 'block', marginBottom: '4px' }}>Y</label>
                <input
                  type="number"
                  value={localNodeData.position.y}
                  readOnly
                  style={{
                    width: '100%',
                    padding: '6px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '13px',
                    background: '#f9fafb'
                  }}
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div style={{
            display: 'flex',
            gap: '8px',
            marginTop: '24px',
            paddingTop: '16px',
            borderTop: '1px solid #e5e7eb'
          }}>
            <button
              onClick={() => onDuplicateNode && onDuplicateNode(localNodeData.id)}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                padding: '8px',
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                color: '#374151'
              }}
            >
              <Copy size={14} />
              Duplicate
            </button>
            <button
              onClick={() => onDeleteNode && onDeleteNode(localNodeData.id)}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                padding: '8px',
                background: 'white',
                border: '1px solid #fee2e2',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                color: '#ef4444'
              }}
            >
              <Trash2 size={14} />
              Delete
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Otherwise show workflow properties
  return (
    <div className="workflow-properties-panel" style={{
      width: '300px',
      height: '100%',
      background: 'white',
      borderLeft: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', margin: 0 }}>
          Workflow Properties
        </h3>
      </div>

      {/* Scrollable content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px'
      }}>
        {/* Workflow Name */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            marginBottom: '6px',
            textTransform: 'uppercase'
          }}>
            Name
          </label>
          <input
            type="text"
            value={workflow.name || ''}
            onChange={(e) => handleWorkflowFieldChange('name', e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        {/* Workflow Description */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            marginBottom: '6px',
            textTransform: 'uppercase'
          }}>
            Description
          </label>
          <textarea
            value={workflow.description || ''}
            onChange={(e) => handleWorkflowFieldChange('description', e.target.value)}
            rows={4}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
        </div>

        {/* Quick Stats */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: '#f9fafb',
          borderRadius: '8px'
        }}>
          <h4 style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#6b7280',
            marginBottom: '12px',
            textTransform: 'uppercase'
          }}>
            Quick Stats
          </h4>
          <div style={{ fontSize: '14px', color: '#374151' }}>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontWeight: '500' }}>Nodes:</span> {workflow.nodes?.length || 0}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontWeight: '500' }}>Connections:</span> {workflow.connections?.length || 0}
            </div>
            <div>
              <span style={{ fontWeight: '500' }}>Difficulty:</span>{' '}
              <span style={{ textTransform: 'capitalize' }}>{workflow.difficulty || 'beginner'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowPropertiesPanel;
