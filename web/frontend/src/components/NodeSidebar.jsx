import React, { useState, useEffect } from 'react';
import { X, Sparkles, Trash2, ExternalLink } from 'lucide-react';
import './NodeSidebar.css';

/**
 * NodeSidebar Component - GHL Native Style
 *
 * Right sidebar panel that slides in when a node is selected.
 * Matches GoHighLevel's exact design:
 * - ~400px width
 * - White background
 * - Tabs: Edit Action | Statistics
 * - Form fields with proper labels
 * - "Write with AI" button
 * - Delete | Cancel | Save buttons at bottom
 */

const NodeSidebar = ({
  node,
  isOpen,
  onClose,
  onSave,
  onDelete
}) => {
  const [activeTab, setActiveTab] = useState('edit');
  const [formData, setFormData] = useState({
    actionName: '',
    template: '',
    message: '',
    subject: '',
    tag: '',
    duration: '',
    units: 'minutes',
    conditionType: '',
    field: '',
    operator: '',
    value: ''
  });

  // Initialize form data when node changes
  useEffect(() => {
    if (node) {
      setFormData({
        actionName: node.action_name || node.title || '',
        template: node.template || '',
        message: node.message || '',
        subject: node.subject || '',
        tag: node.tag || '',
        duration: node.duration || '',
        units: node.units || 'minutes',
        conditionType: node.condition_type || '',
        field: node.field || '',
        operator: node.operator || '',
        value: node.value || ''
      });
    }
  }, [node]);

  if (!isOpen || !node) return null;

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave(node.id, formData);
    }
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this action?')) {
      if (onDelete) {
        onDelete(node.id);
      }
    }
  };

  const handleWriteWithAI = () => {
    // TODO: Implement AI writing feature
    alert('AI writing feature coming soon!');
  };

  // Get node type display name
  const getNodeTypeName = () => {
    const typeNames = {
      sms: 'SMS',
      email: 'Email',
      tag: 'Tag',
      delay: 'Wait',
      condition: 'Condition',
      trigger: 'Trigger',
      action: 'Action'
    };
    return typeNames[node.type] || 'Action';
  };

  // Get node description
  const getNodeDescription = () => {
    const descriptions = {
      sms: 'Sends a text message to the Contact',
      email: 'Sends an email to the Contact',
      tag: 'Adds or removes a tag from the Contact',
      delay: 'Waits for a specified duration before continuing',
      condition: 'Branches the workflow based on a condition',
      trigger: 'Starts the workflow when conditions are met',
      action: 'Performs an action on the Contact'
    };
    return descriptions[node.type] || 'Configure this action';
  };

  return (
    <div className="node-sidebar-overlay" onClick={onClose}>
      <div className="node-sidebar" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="sidebar-header">
          <div>
            <h2>{getNodeTypeName()}</h2>
            <p className="sidebar-description">{getNodeDescription()}</p>
          </div>
          <button className="close-btn" onClick={onClose} title="Close">
            <X size={20} />
          </button>
        </div>

        {/* Learn More Link */}
        <a href="#" className="learn-more-link">
          <ExternalLink size={14} />
          <span>Learn More</span>
        </a>

        {/* Tabs */}
        <div className="sidebar-tabs">
          <button
            className={activeTab === 'edit' ? 'active' : ''}
            onClick={() => setActiveTab('edit')}
          >
            Edit Action
          </button>
          <button
            className={activeTab === 'statistics' ? 'active' : ''}
            onClick={() => setActiveTab('statistics')}
          >
            Statistics
          </button>
        </div>

        {/* Content */}
        <div className="sidebar-content">
          {activeTab === 'edit' ? (
            <>
              {/* Action Name */}
              <div className="form-group">
                <label>ACTION NAME</label>
                <input
                  type="text"
                  value={formData.actionName}
                  onChange={(e) => handleChange('actionName', e.target.value)}
                  placeholder="Enter action name"
                />
              </div>

              {/* SMS-specific fields */}
              {node.type === 'sms' && (
                <>
                  <div className="form-group">
                    <label>TEMPLATES</label>
                    <select
                      value={formData.template}
                      onChange={(e) => handleChange('template', e.target.value)}
                    >
                      <option value="">Select Template</option>
                      <option value="welcome">Welcome Message</option>
                      <option value="confirmation">Confirmation</option>
                      <option value="reminder">Reminder</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <div className="label-with-button">
                      <label>MESSAGE</label>
                      <button className="write-ai-btn" onClick={handleWriteWithAI}>
                        <Sparkles size={14} />
                        <span>Write with AI</span>
                      </button>
                    </div>
                    <textarea
                      rows={6}
                      value={formData.message}
                      onChange={(e) => handleChange('message', e.target.value)}
                      placeholder="Enter your message..."
                    />
                    <div className="char-count">
                      {formData.message.length} / 160 characters
                    </div>
                  </div>
                </>
              )}

              {/* Email-specific fields */}
              {node.type === 'email' && (
                <>
                  <div className="form-group">
                    <label>SUBJECT</label>
                    <input
                      type="text"
                      value={formData.subject}
                      onChange={(e) => handleChange('subject', e.target.value)}
                      placeholder="Enter email subject"
                    />
                  </div>

                  <div className="form-group">
                    <label>TEMPLATE</label>
                    <select
                      value={formData.template}
                      onChange={(e) => handleChange('template', e.target.value)}
                    >
                      <option value="">Select Template</option>
                      <option value="welcome-email">Welcome Email</option>
                      <option value="newsletter">Newsletter</option>
                      <option value="promo">Promotional Email</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <div className="label-with-button">
                      <label>MESSAGE</label>
                      <button className="write-ai-btn" onClick={handleWriteWithAI}>
                        <Sparkles size={14} />
                        <span>Write with AI</span>
                      </button>
                    </div>
                    <textarea
                      rows={8}
                      value={formData.message}
                      onChange={(e) => handleChange('message', e.target.value)}
                      placeholder="Enter email body..."
                    />
                  </div>
                </>
              )}

              {/* Tag-specific fields */}
              {node.type === 'tag' && (
                <div className="form-group">
                  <label>TAG NAME</label>
                  <input
                    type="text"
                    value={formData.tag}
                    onChange={(e) => handleChange('tag', e.target.value)}
                    placeholder="Enter tag name"
                  />
                </div>
              )}

              {/* Delay-specific fields */}
              {node.type === 'delay' && (
                <>
                  <div className="form-group">
                    <label>DURATION</label>
                    <input
                      type="number"
                      value={formData.duration}
                      onChange={(e) => handleChange('duration', e.target.value)}
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div className="form-group">
                    <label>UNITS</label>
                    <select
                      value={formData.units}
                      onChange={(e) => handleChange('units', e.target.value)}
                    >
                      <option value="minutes">Minutes</option>
                      <option value="hours">Hours</option>
                      <option value="days">Days</option>
                    </select>
                  </div>
                </>
              )}

              {/* Condition-specific fields */}
              {node.type === 'condition' && (
                <>
                  <div className="form-group">
                    <label>CONDITION TYPE</label>
                    <select
                      value={formData.conditionType}
                      onChange={(e) => handleChange('conditionType', e.target.value)}
                    >
                      <option value="">Select Condition</option>
                      <option value="tag_exists">Tag Exists</option>
                      <option value="field_equals">Field Equals</option>
                      <option value="field_contains">Field Contains</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>FIELD</label>
                    <input
                      type="text"
                      value={formData.field}
                      onChange={(e) => handleChange('field', e.target.value)}
                      placeholder="Enter field name"
                    />
                  </div>

                  <div className="form-group">
                    <label>OPERATOR</label>
                    <select
                      value={formData.operator}
                      onChange={(e) => handleChange('operator', e.target.value)}
                    >
                      <option value="">Select Operator</option>
                      <option value="equals">Equals</option>
                      <option value="not_equals">Not Equals</option>
                      <option value="contains">Contains</option>
                      <option value="not_contains">Does Not Contain</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>VALUE</label>
                    <input
                      type="text"
                      value={formData.value}
                      onChange={(e) => handleChange('value', e.target.value)}
                      placeholder="Enter value"
                    />
                  </div>
                </>
              )}
            </>
          ) : (
            // Statistics tab
            <div className="statistics-placeholder">
              <p>Statistics will be available after the workflow is deployed and executed.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
          <button className="delete-btn" onClick={handleDelete}>
            <Trash2 size={16} />
            <span>Delete</span>
          </button>
          <div className="footer-actions">
            <button className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
            <button className="save-btn" onClick={handleSave}>
              Save Action
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeSidebar;
