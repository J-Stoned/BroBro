import React, { useState, useEffect } from 'react';

/**
 * ConditionBuilder - Epic 12: Story 12.1
 * Visual conditional logic builder with multiple operators
 */

const CONDITION_TYPES = [
  { value: 'equals', label: 'Equals', needsValue: true },
  { value: 'not_equals', label: 'Does not equal', needsValue: true },
  { value: 'contains', label: 'Contains', needsValue: true },
  { value: 'not_contains', label: 'Does not contain', needsValue: true },
  { value: 'greater_than', label: 'Greater than', needsValue: true },
  { value: 'less_than', label: 'Less than', needsValue: true },
  { value: 'starts_with', label: 'Starts with', needsValue: true },
  { value: 'ends_with', label: 'Ends with', needsValue: true },
  { value: 'is_empty', label: 'Is empty', needsValue: false },
  { value: 'is_not_empty', label: 'Is not empty', needsValue: false },
  { value: 'matches_regex', label: 'Matches pattern', needsValue: true },
];

const FIELD_SUGGESTIONS = [
  { value: 'contact.email', label: 'Contact Email', type: 'text', category: 'contact' },
  { value: 'contact.phone', label: 'Contact Phone', type: 'text', category: 'contact' },
  { value: 'contact.firstName', label: 'First Name', type: 'text', category: 'contact' },
  { value: 'contact.lastName', label: 'Last Name', type: 'text', category: 'contact' },
  { value: 'contact.tags', label: 'Tags', type: 'array', category: 'contact' },
  { value: 'contact.source', label: 'Lead Source', type: 'text', category: 'contact' },
  { value: 'opportunity.value', label: 'Opportunity Value', type: 'number', category: 'opportunity' },
  { value: 'opportunity.stage', label: 'Opportunity Stage', type: 'text', category: 'opportunity' },
  { value: 'opportunity.status', label: 'Opportunity Status', type: 'text', category: 'opportunity' },
  { value: 'appointment.status', label: 'Appointment Status', type: 'text', category: 'appointment' },
  { value: 'appointment.date', label: 'Appointment Date', type: 'date', category: 'appointment' },
  { value: 'form.name', label: 'Form Name', type: 'text', category: 'form' },
];

const ConditionBuilder = ({ conditions = [], onChange, availableVariables = [] }) => {
  const [logicOperator, setLogicOperator] = useState('and');

  useEffect(() => {
    // Initialize with logicOperator from parent if provided
    if (conditions.length > 0 && conditions[0].logicOperator) {
      setLogicOperator(conditions[0].logicOperator);
    }
  }, []);

  const addCondition = () => {
    const newCondition = {
      id: Date.now().toString(),
      field: '',
      operator: 'equals',
      value: ''
    };
    const updated = [...conditions, newCondition];
    onChange(updated, logicOperator);
  };

  const removeCondition = (id) => {
    const updated = conditions.filter(c => c.id !== id);
    onChange(updated, logicOperator);
  };

  const updateCondition = (id, updates) => {
    const updated = conditions.map(c => c.id === id ? { ...c, ...updates } : c);
    onChange(updated, logicOperator);
  };

  const toggleLogicOperator = () => {
    const newOperator = logicOperator === 'and' ? 'or' : 'and';
    setLogicOperator(newOperator);
    onChange(conditions, newOperator);
  };

  const getOperatorDisplay = (operator) => {
    return CONDITION_TYPES.find(t => t.value === operator)?.label || operator;
  };

  return (
    <div style={{
      padding: '16px',
      background: 'white',
      borderRadius: '8px',
      border: '1px solid #e5e7eb'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#111827' }}>
          🔀 Conditions
        </h4>
        <p style={{ margin: 0, fontSize: '13px', color: '#6b7280' }}>
          Define when this path should be taken
        </p>
      </div>

      {/* Logic Operator Toggle */}
      {conditions.length > 1 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '16px',
          padding: '12px',
          background: '#f9fafb',
          borderRadius: '6px',
          fontSize: '14px',
          color: '#6b7280'
        }}>
          <span>Match</span>
          <button
            onClick={toggleLogicOperator}
            style={{
              padding: '4px 12px',
              border: `2px solid ${logicOperator === 'and' ? '#3b82f6' : '#f59e0b'}`,
              borderRadius: '4px',
              background: 'white',
              color: logicOperator === 'and' ? '#3b82f6' : '#f59e0b',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontSize: '13px'
            }}
          >
            {logicOperator === 'and' ? 'ALL' : 'ANY'}
          </button>
          <span>conditions</span>
        </div>
      )}

      {/* Conditions List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '12px' }}>
        {conditions.map((condition, index) => {
          const operatorConfig = CONDITION_TYPES.find(t => t.value === condition.operator);
          const needsValue = operatorConfig?.needsValue !== false;

          return (
            <div key={condition.id} style={{ position: 'relative' }}>
              {/* Logic Badge */}
              {index > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '-6px',
                  left: '12px',
                  padding: '2px 8px',
                  background: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '600',
                  color: '#6b7280',
                  zIndex: 1
                }}>
                  {logicOperator.toUpperCase()}
                </div>
              )}

              {/* Condition Fields */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: needsValue ? '2fr 1.5fr 2fr auto' : '2fr 2fr auto',
                gap: '8px',
                padding: '12px',
                background: '#f9fafb',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                alignItems: 'end'
              }}>
                {/* Field Selector */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>
                    Field
                  </label>
                  <select
                    value={condition.field}
                    onChange={(e) => updateCondition(condition.id, { field: e.target.value })}
                    style={{
                      padding: '8px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '4px',
                      background: 'white',
                      color: '#111827',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  >
                    <option value="">Select field...</option>
                    <optgroup label="Contact Fields">
                      {FIELD_SUGGESTIONS.filter(f => f.category === 'contact').map(field => (
                        <option key={field.value} value={field.value}>{field.label}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Opportunity Fields">
                      {FIELD_SUGGESTIONS.filter(f => f.category === 'opportunity').map(field => (
                        <option key={field.value} value={field.value}>{field.label}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Appointment Fields">
                      {FIELD_SUGGESTIONS.filter(f => f.category === 'appointment').map(field => (
                        <option key={field.value} value={field.value}>{field.label}</option>
                      ))}
                    </optgroup>
                    {availableVariables.length > 0 && (
                      <optgroup label="Variables">
                        {availableVariables.map(v => (
                          <option key={v.name} value={`var.${v.name}`}>
                            {v.name}
                          </option>
                        ))}
                      </optgroup>
                    )}
                  </select>
                </div>

                {/* Operator Selector */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>
                    Operator
                  </label>
                  <select
                    value={condition.operator}
                    onChange={(e) => updateCondition(condition.id, { operator: e.target.value })}
                    style={{
                      padding: '8px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '4px',
                      background: 'white',
                      color: '#111827',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  >
                    {CONDITION_TYPES.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                {/* Value Input */}
                {needsValue && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <label style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>
                      Value
                    </label>
                    <input
                      type="text"
                      value={condition.value}
                      onChange={(e) => updateCondition(condition.id, { value: e.target.value })}
                      placeholder="Enter value..."
                      style={{
                        padding: '8px',
                        border: '1px solid #e5e7eb',
                        borderRadius: '4px',
                        background: 'white',
                        color: '#111827',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                      onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                    />
                  </div>
                )}

                {/* Remove Button */}
                <button
                  onClick={() => removeCondition(condition.id)}
                  style={{
                    width: '32px',
                    height: '32px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    background: 'white',
                    color: '#ef4444',
                    fontSize: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#fef2f2';
                    e.target.style.borderColor = '#ef4444';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = 'white';
                    e.target.style.borderColor = '#e5e7eb';
                  }}
                  title="Remove condition"
                >
                  ✕
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Condition Button */}
      <button
        onClick={addCondition}
        style={{
          width: '100%',
          padding: '10px',
          border: '2px dashed #e5e7eb',
          borderRadius: '6px',
          background: 'transparent',
          color: '#6b7280',
          fontSize: '14px',
          cursor: 'pointer',
          transition: 'all 0.2s'
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
        + Add Condition
      </button>

      {/* Condition Preview */}
      {conditions.length > 0 && (
        <div style={{
          marginTop: '12px',
          padding: '12px',
          background: '#f9fafb',
          borderRadius: '6px',
          fontSize: '13px'
        }}>
          <strong style={{ display: 'block', marginBottom: '4px', color: '#6b7280' }}>
            Preview:
          </strong>
          <code style={{
            display: 'block',
            padding: '8px',
            background: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            color: '#111827',
            fontFamily: 'monospace',
            fontSize: '12px',
            whiteSpace: 'pre-wrap'
          }}>
            {conditions.map((c, i) => (
              <span key={c.id}>
                {i > 0 && ` ${logicOperator.toUpperCase()} `}
                {c.field || '[field]'} {getOperatorDisplay(c.operator)} {c.value || ''}
              </span>
            )).reduce((prev, curr) => [prev, curr])}
          </code>
        </div>
      )}
    </div>
  );
};

export default ConditionBuilder;
