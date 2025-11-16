import React from 'react';

/**
 * WorkflowConnection Component
 * Epic 10: Story 10.1
 *
 * Renders connections between workflow nodes as Bezier curves
 */

// Connection type colors
const CONNECTION_TYPES = {
  default: {
    color: '#9ca3af',
    hoverColor: '#6b7280'
  },
  success: {
    color: '#10b981',
    hoverColor: '#059669'
  },
  error: {
    color: '#ef4444',
    hoverColor: '#dc2626'
  },
  data: {
    color: '#3b82f6',
    hoverColor: '#2563eb'
  }
};

const WorkflowConnection = ({
  connection,
  fromNode,
  toNode,
  isSelected,
  isHovered,
  onSelect,
  onMouseEnter,
  onMouseLeave
}) => {
  if (!fromNode || !toNode) return null;

  const connType = CONNECTION_TYPES[connection.type] || CONNECTION_TYPES.default;

  // Calculate positions
  const startX = fromNode.position.x + 200; // Right side of source node
  const startY = fromNode.position.y + 60;  // Middle of node height
  const endX = toNode.position.x;           // Left side of target node
  const endY = toNode.position.y + 60;

  // Calculate Bezier curve control points
  const dx = endX - startX;
  const dy = endY - startY;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Control point offset (horizontal only for cleaner curves)
  const cpOffset = Math.min(distance * 0.5, 150);

  const cp1x = startX + cpOffset;
  const cp1y = startY;
  const cp2x = endX - cpOffset;
  const cp2y = endY;

  // Build SVG path
  const path = `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${endY}`;

  // Calculate midpoint for label
  const midX = (startX + cp1x + cp2x + endX) / 4;
  const midY = (startY + cp1y + cp2y + endY) / 4;

  // Arrow marker ID
  const markerId = `arrow-${connection.id}`;

  const strokeColor = isSelected
    ? connType.hoverColor
    : (isHovered ? connType.hoverColor : connType.color);

  const strokeWidth = isSelected || isHovered ? 3 : 2;

  const handleClick = (e) => {
    e.stopPropagation();
    if (onSelect) {
      onSelect(connection.id);
    }
  };

  return (
    <g className="workflow-connection">
      {/* Define arrow marker */}
      <defs>
        <marker
          id={markerId}
          markerWidth="10"
          markerHeight="10"
          refX="8"
          refY="3"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <path
            d="M0,0 L0,6 L9,3 z"
            fill={strokeColor}
          />
        </marker>
      </defs>

      {/* Invisible wider path for easier selection */}
      <path
        d={path}
        fill="none"
        stroke="transparent"
        strokeWidth="20"
        style={{ cursor: 'pointer' }}
        onClick={handleClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      />

      {/* Visible connection path */}
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        markerEnd={`url(#${markerId})`}
        style={{
          cursor: 'pointer',
          transition: 'stroke 0.2s, stroke-width 0.2s'
        }}
        onClick={handleClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      />

      {/* Label (if exists) */}
      {connection.label && (
        <g transform={`translate(${midX}, ${midY - 10})`}>
          <rect
            x="-20"
            y="-10"
            width="40"
            height="20"
            rx="10"
            fill="white"
            stroke={strokeColor}
            strokeWidth="1.5"
          />
          <text
            x="0"
            y="4"
            textAnchor="middle"
            fill={strokeColor}
            fontSize="11"
            fontWeight="600"
            style={{ userSelect: 'none' }}
          >
            {connection.label}
          </text>
        </g>
      )}
    </g>
  );
};

export default WorkflowConnection;
