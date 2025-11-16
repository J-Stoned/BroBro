/**
 * Workflow Normalizer
 * Epic 10: Story 10.2
 *
 * Fill missing fields with intelligent defaults
 */

import { generateId } from './workflowState';

/**
 * Normalize workflow - fill missing fields
 */
export const normalizeWorkflow = (workflow) => {
  const normalized = { ...workflow };

  // Generate ID if missing
  if (!normalized.id) {
    normalized.id = generateId('wf');
  }

  // Fill metadata
  normalized.metadata = {
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    source: 'imported',
    ...(normalized.metadata || {})
  };

  // Default values
  if (!normalized.name) normalized.name = 'Imported Workflow';
  if (!normalized.description) normalized.description = '';
  if (!normalized.niche) normalized.niche = 'general';
  if (!normalized.difficulty) normalized.difficulty = 'beginner';
  if (!normalized.version) normalized.version = '1.0';

  // Normalize nodes
  if (normalized.nodes) {
    normalized.nodes = normalized.nodes.map((node, index) => normalizeNode(node, index));
  } else {
    normalized.nodes = [];
  }

  // Normalize connections
  if (normalized.connections) {
    normalized.connections = normalized.connections.map((conn, index) => normalizeConnection(conn, index));
  } else {
    normalized.connections = [];
  }

  // Auto-layout if no positions
  if (normalized.nodes.some(n => !n.position || n.position.x === undefined)) {
    normalized.nodes = generateNodePositions(normalized.nodes);
  }

  return normalized;
};

/**
 * Normalize individual node
 */
const normalizeNode = (node, index) => {
  const normalized = { ...node };

  // Generate ID if missing
  if (!normalized.id) {
    normalized.id = generateId('node');
  }

  // Default type
  if (!normalized.type) {
    normalized.type = index === 0 ? 'trigger' : 'action';
  }

  // Default title
  if (!normalized.title) {
    const typeNames = {
      trigger: 'New Trigger',
      action: 'New Action',
      condition: 'New Condition',
      delay: 'Wait',
      end: 'End'
    };
    normalized.title = typeNames[normalized.type] || 'New Node';
  }

  // Default description
  if (!normalized.description) {
    normalized.description = '';
  }

  // Default position
  if (!normalized.position || typeof normalized.position.x !== 'number') {
    normalized.position = { x: 100 + index * 250, y: 150 };
  }

  // Default params
  if (!normalized.params) {
    normalized.params = {};
  }

  return normalized;
};

/**
 * Normalize individual connection
 */
const normalizeConnection = (connection, index) => {
  const normalized = { ...connection };

  // Generate ID if missing
  if (!normalized.id) {
    normalized.id = generateId('conn');
  }

  // Default type
  if (!normalized.type) {
    normalized.type = 'default';
  }

  // Default label
  if (normalized.label === undefined) {
    normalized.label = '';
  }

  return normalized;
};

/**
 * Auto-layout nodes in hierarchical grid
 */
export const generateNodePositions = (nodes) => {
  const positioned = [];
  const typeOffsets = {
    trigger: 0,
    action: 1,
    condition: 2,
    delay: 3,
    end: 4
  };

  const columns = {};
  const ySpacing = 150;
  const xSpacing = 250;

  nodes.forEach(node => {
    const colIndex = typeOffsets[node.type] || 1;

    if (!columns[colIndex]) {
      columns[colIndex] = [];
    }

    columns[colIndex].push(node);
  });

  // Position nodes
  Object.keys(columns).forEach(colIndex => {
    const colNodes = columns[colIndex];
    const x = 50 + parseInt(colIndex) * xSpacing;

    colNodes.forEach((node, rowIndex) => {
      positioned.push({
        ...node,
        position: {
          x,
          y: 100 + rowIndex * ySpacing
        }
      });
    });
  });

  return positioned;
};

/**
 * Sanitize node params
 */
export const sanitizeNodeParams = (node) => {
  if (!node.params || typeof node.params !== 'object') {
    return { ...node, params: {} };
  }

  const sanitized = { ...node };
  const cleanParams = {};

  Object.entries(node.params).forEach(([key, value]) => {
    // Remove null/undefined
    if (value !== null && value !== undefined) {
      cleanParams[key] = value;
    }
  });

  sanitized.params = cleanParams;
  return sanitized;
};

/**
 * Apply workflow defaults
 */
export const applyDefaults = (workflow) => {
  return normalizeWorkflow(workflow);
};
