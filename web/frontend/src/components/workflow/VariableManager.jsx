import React, { useState } from 'react';
import { Copy, Trash2, Plus, X } from 'lucide-react';

/**
 * VariableManager - Epic 12: Story 12.2
 * Manage workflow variables with CRUD operations
 */

const VARIABLE_TYPES = [
  { value: 'text', label: 'Text', icon: '📝', description: 'String values' },
  { value: 'number', label: 'Number', icon: '🔢', description: 'Numeric values' },
  { value: 'date', label: 'Date', icon: '📅', description: 'Date/time values' },
  { value: 'boolean', label: 'Yes/No', icon: '✓/✗', description: 'True/false values' },
  { value: 'array', label: 'List', icon: '📋', description: 'Array of values' },
  { value: 'object', label: 'Object', icon: '🔷', description: 'JSON objects' },
];

const VariableManager = ({ variables = [], onChange }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVariable, setNewVariable] = useState({
    name: '',
    type: 'text',
    defaultValue: '',
    description: ''
  });
  const [copiedId, setCopiedId] = useState(null);

  const addVariable = () => {
    if (!newVariable.name.trim()) {
      alert('Variable name is required');
      return;
    }

    // Validate variable name (alphanumeric and underscores only)
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(newVariable.name)) {
      alert('Variable name must start with a letter and contain only letters, numbers, and underscores');
      return;
    }

    // Check for duplicate names
    if (variables.some(v => v.name === newVariable.name)) {
      alert('Variable name already exists');
      return;
    }

    onChange([...variables, { ...newVariable, id: Date.now().toString() }]);

    // Reset form
    setNewVariable({
      name: '',
      type: 'text',
      defaultValue: '',
      description: ''
    });
    setShowAddForm(false);
  };

  const removeVariable = (id) => {
    if (window.confirm('Remove this variable? This may break workflows that use it.')) {
      onChange(variables.filter(v => v.id !== id));
    }
  };

  const copyVariableRef = (name) => {
    const ref = `{{${name}}}`;
    navigator.clipboard.writeText(ref);
    setCopiedId(name);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getTypeIcon = (type) => {
    return VARIABLE_TYPES.find(t => t.value === type)?.icon || '📝';
  };

  const getTypeLabel = (type) => {
    return VARIABLE_TYPES.find(t => t.value === type)?.label || type;
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <h4 style={{
          margin: '0 0 4px 0',
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          🎯 Variables
        </h4>
        <p style={{
          margin: 0,
          fontSize: '13px',
          color: '#6b7280'
        }}>
          Store and reuse data across your workflow
        </p>
      </div>

      {/* Variables List */}
      {variables.length > 0 && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          marginBottom: '16px'
        }}>
          {variables.map(variable => (
            <div
              key={variable.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px',
                background: '#f9fafb',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.borderColor = '#3b82f6';
                e.currentTarget.style.background = '#eff6ff';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.borderColor = '#e5e7eb';
                e.currentTarget.style.background = '#f9fafb';
              }}
            >
              {/* Type Icon */}
              <div style={{
                fontSize: '24px',
                lineHeight: 1
              }}>
                {getTypeIcon(variable.type)}
              </div>

              {/* Variable Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '4px',
                  flexWrap: 'wrap'
                }}>
                  <code style={{
                    padding: '2px 6px',
                    background: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '13px',
                    fontWeight: '600',
                    color: '#3b82f6',
                    fontFamily: 'monospace'
                  }}>
                    {`{{${variable.name}}}`}
                  </code>
                  <span style={{
                    padding: '2px 8px',
                    background: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '11px',
                    color: '#6b7280',
                    textTransform: 'capitalize'
                  }}>
                    {getTypeLabel(variable.type)}
                  </span>
                </div>

                {variable.description && (
                  <div style={{
                    fontSize: '13px',
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    {variable.description}
                  </div>
                )}

                {variable.defaultValue && (
                  <div style={{
                    fontSize: '12px',
                    color: '#9ca3af'
                  }}>
                    Default: <code style={{
                      padding: '1px 4px',
                      background: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '3px',
                      fontFamily: 'monospace'
                    }}>{String(variable.defaultValue)}</code>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div style={{
                display: 'flex',
                gap: '4px'
              }}>
                <button
                  onClick={() => copyVariableRef(variable.name)}
                  style={{
                    padding: '6px',
                    background: copiedId === variable.name ? '#10b981' : 'white',
                    color: copiedId === variable.name ? 'white' : '#6b7280',
                    border: `1px solid ${copiedId === variable.name ? '#10b981' : '#e5e7eb'}`,
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  title="Copy reference"
                >
                  <Copy size={14} />
                </button>
                <button
                  onClick={() => removeVariable(variable.id)}
                  style={{
                    padding: '6px',
                    background: 'white',
                    color: '#ef4444',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#fef2f2';
                    e.target.style.borderColor = '#ef4444';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = 'white';
                    e.target.style.borderColor = '#e5e7eb';
                  }}
                  title="Remove variable"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {variables.length === 0 && !showAddForm && (
        <div style={{
          textAlign: 'center',
          padding: '32px 16px',
          color: '#6b7280',
          marginBottom: '16px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎯</div>
          <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
            No variables yet
          </div>
          <div style={{ fontSize: '13px' }}>
            Add variables to store and reuse data in your workflow
          </div>
        </div>
      )}

      {/* Add Form */}
      {showAddForm ? (
        <div style={{
          padding: '16px',
          background: '#f9fafb',
          border: '2px solid #3b82f6',
          borderRadius: '8px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <h5 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Add Variable
            </h5>
            <button
              onClick={() => setShowAddForm(false)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                color: '#6b7280'
              }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {/* Name & Type Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '12px',
                  fontWeight: '500',
                  color: '#374151',
                  marginBottom: '4px'
                }}>
                  Variable Name *
                </label>
                <input
                  type="text"
                  value={newVariable.name}
                  onChange={(e) => setNewVariable({ ...newVariable, name: e.target.value })}
                  placeholder="e.g., customerName"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '13px',
                    outline: 'none',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
                <small style={{ fontSize: '11px', color: '#6b7280', display: 'block', marginTop: '2px' }}>
                  Use as: {`{{${newVariable.name || 'variableName'}}}`}
                </small>
              </div>

              <div>
                <label style={{
                  display: 'block',
                  fontSize: '12px',
                  fontWeight: '500',
                  color: '#374151',
                  marginBottom: '4px'
                }}>
                  Type *
                </label>
                <select
                  value={newVariable.type}
                  onChange={(e) => setNewVariable({ ...newVariable, type: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    fontSize: '13px',
                    outline: 'none',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                >
                  {VARIABLE_TYPES.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Default Value */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Default Value
              </label>
              <input
                type="text"
                value={newVariable.defaultValue}
                onChange={(e) => setNewVariable({ ...newVariable, defaultValue: e.target.value })}
                placeholder="Optional default value"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                  fontSize: '13px',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>

            {/* Description */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '4px'
              }}>
                Description
              </label>
              <textarea
                value={newVariable.description}
                onChange={(e) => setNewVariable({ ...newVariable, description: e.target.value })}
                placeholder="What is this variable used for?"
                rows={2}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                  fontSize: '13px',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
              <button
                onClick={addVariable}
                style={{
                  flex: 1,
                  padding: '8px',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
                onMouseOver={(e) => e.target.style.background = '#2563eb'}
                onMouseOut={(e) => e.target.style.background = '#3b82f6'}
              >
                <Plus size={14} />
                Add Variable
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                style={{
                  padding: '8px 16px',
                  background: 'white',
                  color: '#6b7280',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowAddForm(true)}
          style={{
            width: '100%',
            padding: '10px',
            border: '2px dashed #e5e7eb',
            borderRadius: '6px',
            background: 'transparent',
            color: '#6b7280',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}
          onMouseOver={(e) => {
            e.target.style.borderColor = '#3b82f6';
            e.target.style.color = '#3b82f6';
            e.target.style.background = 'rgba(59, 130, 246, 0.05)';
          }}
          onMouseOut={(e) => {
            e.target.style.borderColor = '#e5e7eb';
            e.target.style.color = '#6b7280';
            e.target.style.background = 'transparent';
          }}
        >
          <Plus size={16} />
          Add Variable
        </button>
      )}

      {/* Help Text */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        background: '#fffbeb',
        border: '1px solid #fde68a',
        borderRadius: '6px',
        fontSize: '12px',
        color: '#92400e',
        lineHeight: '1.5'
      }}>
        <strong>💡 Tip:</strong> Use variables to store dynamic data like contact names, order IDs, or custom values. Reference them anywhere using <code style={{
          padding: '1px 4px',
          background: 'white',
          border: '1px solid #fcd34d',
          borderRadius: '3px',
          fontFamily: 'monospace'
        }}>{`{{variableName}}`}</code>
      </div>
    </div>
  );
};

export default VariableManager;
