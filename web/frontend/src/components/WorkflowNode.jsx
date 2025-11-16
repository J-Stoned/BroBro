import React from 'react';
import {
  Play, Mail, MessageSquare, Tag, Clock, GitBranch, StopCircle,
  MoreVertical, Check
} from 'lucide-react';
import './WorkflowNode.css';

/**
 * WorkflowNode Component - GHL Native Style
 *
 * Clean, minimal white cards matching GoHighLevel's exact design:
 * - Icon + Title + Menu dots
 * - Subtitle/description
 * - No colored borders (white cards with shadows)
 * - ~220px width
 * - Selected state: Blue border + checkbox
 */

// Node type configuration (icons and styling)
const NODE_CONFIG = {
  trigger: {
    icon: Play,
    iconColor: '#3b82f6',
    defaultTitle: 'Trigger',
    defaultSubtitle: 'Start workflow'
  },
  action: {
    icon: MessageSquare,
    iconColor: '#10b981',
    defaultTitle: 'Action',
    defaultSubtitle: 'Perform action'
  },
  sms: {
    icon: MessageSquare,
    iconColor: '#8b5cf6',
    defaultTitle: 'SMS',
    defaultSubtitle: 'Send text message'
  },
  email: {
    icon: Mail,
    iconColor: '#3b82f6',
    defaultTitle: 'Email',
    defaultSubtitle: 'Send email'
  },
  tag: {
    icon: Tag,
    iconColor: '#f59e0b',
    defaultTitle: 'Tag',
    defaultSubtitle: 'Add or remove tag'
  },
  delay: {
    icon: Clock,
    iconColor: '#f59e0b',
    defaultTitle: 'Wait',
    defaultSubtitle: 'Delay action'
  },
  condition: {
    icon: GitBranch,
    iconColor: '#8b5cf6',
    defaultTitle: 'Condition',
    defaultSubtitle: 'Branch workflow'
  },
  end: {
    icon: StopCircle,
    iconColor: '#ef4444',
    defaultTitle: 'End',
    defaultSubtitle: 'Stop workflow'
  }
};

/**
 * Get display text for node
 */
const getNodeDisplay = (node) => {
  const config = NODE_CONFIG[node.type] || NODE_CONFIG.action;

  // Title: Use node.title or construct from node properties
  let title = node.title || config.defaultTitle;

  // For specific node types, enhance the title
  if (node.type === 'trigger' && node.trigger_type) {
    const triggerNames = {
      'contact_created': 'Contact Created',
      'form_submitted': 'Form Submitted',
      'tag_added': 'Tag Added',
      'opportunity_created': 'Opportunity Created'
    };
    title = triggerNames[node.trigger_type] || title;
  }

  // Subtitle: Extract meaningful description
  let subtitle = config.defaultSubtitle;

  if (node.type === 'sms' || node.type === 'email') {
    // Use action name or message preview
    if (node.action_name) {
      subtitle = node.action_name;
    } else if (node.message) {
      subtitle = node.message.substring(0, 40) + (node.message.length > 40 ? '...' : '');
    }
  }

  if (node.type === 'tag') {
    if (node.tag) {
      subtitle = `${node.action === 'remove' ? 'Remove' : 'Add'} ${node.tag}`;
    }
  }

  if (node.type === 'delay') {
    if (node.duration) {
      const formatDuration = (val, units = 'minutes') => {
        if (units === 'minutes' && val < 60) return `${val} min`;
        if (units === 'minutes' && val >= 60) {
          const hours = Math.floor(val / 60);
          return hours === 1 ? '1 hour' : `${hours} hours`;
        }
        return `${val} ${units}`;
      };
      subtitle = `Wait ${formatDuration(node.duration, node.units)}`;
    }
  }

  if (node.type === 'condition') {
    if (node.condition_type) {
      subtitle = node.condition_type.replace(/_/g, ' ');
    }
  }

  // Override subtitle if explicitly provided
  if (node.subtitle) {
    subtitle = node.subtitle;
  }

  return { title, subtitle };
};

const WorkflowNode = ({
  node,
  isSelected,
  onSelect,
  onMenuClick,
  onDragStart,
  onContextMenu,
  scale = 1
}) => {
  const config = NODE_CONFIG[node.type] || NODE_CONFIG.action;
  const Icon = config.icon;
  const { title, subtitle } = getNodeDisplay(node);

  const handleClick = (e) => {
    e.stopPropagation();
    if (onSelect) {
      onSelect(node.id);
    }
  };

  const handleMenuClick = (e) => {
    e.stopPropagation();
    if (onMenuClick) {
      onMenuClick(e, node);
    }
  };

  const handleMouseDown = (e) => {
    if (onDragStart) {
      onDragStart(e, node.id);
    }
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onContextMenu) {
      onContextMenu(e, node);
    }
  };

  return (
    <g
      className={`workflow-node-container ${isSelected ? 'selected' : ''}`}
      transform={`translate(${node.position.x}, ${node.position.y})`}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      style={{ cursor: 'move' }}
    >
      {/* Connection anchor - top */}
      {node.type !== 'trigger' && (
        <circle
          cx="110"
          cy="0"
          r="6"
          fill="#ffffff"
          stroke="#d1d5db"
          strokeWidth="2"
          className="connection-anchor"
        />
      )}

      {/* Card container (using foreignObject for HTML/CSS) */}
      <foreignObject
        x="0"
        y="10"
        width="220"
        height="100"
        onMouseDown={handleMouseDown}
      >
        <div
          className={`workflow-node ${isSelected ? 'selected' : ''}`}
          xmlns="http://www.w3.org/1999/xhtml"
        >
          {/* Selection checkbox */}
          {isSelected && (
            <div className="node-checkbox">
              <Check size={14} color="#3b82f6" strokeWidth={3} />
            </div>
          )}

          {/* Card header */}
          <div className="node-header">
            <span className="node-icon" style={{ color: config.iconColor }}>
              <Icon size={20} strokeWidth={2} />
            </span>
            <span className="node-title">{title}</span>
            <button
              className="node-menu"
              onClick={handleMenuClick}
              title="Node options"
            >
              <MoreVertical size={16} />
            </button>
          </div>

          {/* Card subtitle */}
          {subtitle && (
            <div className="node-subtitle">
              {subtitle}
            </div>
          )}
        </div>
      </foreignObject>

      {/* Connection anchor - bottom */}
      {node.type !== 'end' && (
        <circle
          cx="110"
          cy="90"
          r="6"
          fill="#ffffff"
          stroke="#d1d5db"
          strokeWidth="2"
          className="connection-anchor"
        />
      )}
    </g>
  );
};

export default WorkflowNode;
