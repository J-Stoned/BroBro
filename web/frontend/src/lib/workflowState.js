/**
 * Workflow State Management
 * Epic 10: Story 10.1
 *
 * Manages workflow state, nodes, connections, and history for undo/redo.
 * Provides functions to create, modify, validate, and export workflows.
 */

/**
 * Generate unique ID
 * @param {string} prefix - ID prefix (e.g., 'node', 'conn')
 * @returns {string} Unique ID
 */
export const generateId = (prefix = 'id') => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Create a new blank workflow
 * @param {Object} metadata - Workflow metadata
 * @returns {Object} New workflow object
 */
export const createWorkflow = (metadata = {}) => {
  return {
    id: generateId('wf'),
    name: metadata.name || 'New Workflow',
    description: metadata.description || '',
    niche: metadata.niche || 'general',
    difficulty: metadata.difficulty || 'beginner',
    version: '1.0',
    metadata: {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      source: metadata.source || 'manual',
      ...metadata
    },
    nodes: [],
    connections: []
  };
};

/**
 * Add node to workflow
 * @param {Object} workflow - Current workflow
 * @param {string} type - Node type
 * @param {Object} position - {x, y} position
 * @param {Object} params - Node parameters
 * @returns {Object} Updated workflow
 */
export const addNode = (workflow, type, position = {}, params = {}) => {
  const nodeId = generateId('node');

  const newNode = {
    id: nodeId,
    type,
    title: params.title || getDefaultNodeTitle(type),
    description: params.description || '',
    position: {
      x: position.x || 100,
      y: position.y || 100
    },
    params: params.params || {}
  };

  return {
    ...workflow,
    nodes: [...workflow.nodes, newNode],
    metadata: {
      ...workflow.metadata,
      updatedAt: new Date().toISOString()
    }
  };
};

/**
 * Update existing node
 * @param {Object} workflow - Current workflow
 * @param {string} nodeId - Node ID to update
 * @param {Object} updates - Updates to apply
 * @returns {Object} Updated workflow
 */
export const updateNode = (workflow, nodeId, updates) => {
  return {
    ...workflow,
    nodes: workflow.nodes.map(node =>
      node.id === nodeId ? { ...node, ...updates } : node
    ),
    metadata: {
      ...workflow.metadata,
      updatedAt: new Date().toISOString()
    }
  };
};

/**
 * Delete node and its connections
 * @param {Object} workflow - Current workflow
 * @param {string} nodeId - Node ID to delete
 * @returns {Object} Updated workflow
 */
export const deleteNode = (workflow, nodeId) => {
  return {
    ...workflow,
    nodes: workflow.nodes.filter(node => node.id !== nodeId),
    connections: workflow.connections.filter(
      conn => conn.from !== nodeId && conn.to !== nodeId
    ),
    metadata: {
      ...workflow.metadata,
      updatedAt: new Date().toISOString()
    }
  };
};

/**
 * Add connection between nodes
 * @param {Object} workflow - Current workflow
 * @param {string} fromId - Source node ID
 * @param {string} toId - Target node ID
 * @param {string} type - Connection type
 * @param {string} label - Connection label
 * @returns {Object} Updated workflow
 */
export const addConnection = (workflow, fromId, toId, type = 'default', label = '') => {
  // Validate: Can't connect to self
  if (fromId === toId) {
    throw new Error('Cannot connect node to itself');
  }

  // Validate: Both nodes exist
  const fromNode = workflow.nodes.find(n => n.id === fromId);
  const toNode = workflow.nodes.find(n => n.id === toId);

  if (!fromNode || !toNode) {
    throw new Error('Source or target node does not exist');
  }

  // Check for duplicate connection
  const duplicateExists = workflow.connections.some(
    conn => conn.from === fromId && conn.to === toId
  );

  if (duplicateExists) {
    throw new Error('Connection already exists');
  }

  const connectionId = generateId('conn');

  const newConnection = {
    id: connectionId,
    from: fromId,
    to: toId,
    type,
    label
  };

  return {
    ...workflow,
    connections: [...workflow.connections, newConnection],
    metadata: {
      ...workflow.metadata,
      updatedAt: new Date().toISOString()
    }
  };
};

/**
 * Delete connection
 * @param {Object} workflow - Current workflow
 * @param {string} connectionId - Connection ID to delete
 * @returns {Object} Updated workflow
 */
export const deleteConnection = (workflow, connectionId) => {
  return {
    ...workflow,
    connections: workflow.connections.filter(conn => conn.id !== connectionId),
    metadata: {
      ...workflow.metadata,
      updatedAt: new Date().toISOString()
    }
  };
};

/**
 * Validate workflow structure
 * @param {Object} workflow - Workflow to validate
 * @returns {Object} Validation result {valid, errors, warnings}
 */
export const validateWorkflow = (workflow) => {
  const errors = [];
  const warnings = [];

  // Check required fields
  if (!workflow.name) {
    errors.push({ code: 'NO_NAME', message: 'Workflow must have a name' });
  }

  if (!workflow.nodes || workflow.nodes.length === 0) {
    errors.push({ code: 'NO_NODES', message: 'Workflow must have at least one node' });
  }

  if (workflow.nodes) {
    // Check for exactly 1 trigger
    const triggers = workflow.nodes.filter(n => n.type === 'trigger');
    if (triggers.length === 0) {
      errors.push({ code: 'NO_TRIGGER', message: 'Workflow must have exactly 1 trigger node' });
    } else if (triggers.length > 1) {
      errors.push({ code: 'MULTIPLE_TRIGGERS', message: 'Workflow can only have 1 trigger node' });
    }

    // Check for orphaned nodes (no connections)
    if (workflow.connections && workflow.connections.length > 0) {
      workflow.nodes.forEach(node => {
        const hasConnection = workflow.connections.some(
          conn => conn.from === node.id || conn.to === node.id
        );
        if (!hasConnection && workflow.nodes.length > 1) {
          warnings.push({
            code: 'ORPHANED_NODE',
            message: `Node "${node.title}" is not connected`,
            nodeId: node.id
          });
        }
      });
    }

    // Check for circular connections
    const circular = detectCircularConnections(workflow);
    if (circular) {
      errors.push({
        code: 'CIRCULAR_CONNECTION',
        message: `Circular connection detected: ${circular}`
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
};

/**
 * Detect circular connections
 * @param {Object} workflow - Workflow to check
 * @returns {string|null} Circular path description or null
 */
const detectCircularConnections = (workflow) => {
  const { nodes, connections } = workflow;

  // Build adjacency list
  const graph = {};
  nodes.forEach(node => {
    graph[node.id] = [];
  });
  connections.forEach(conn => {
    if (graph[conn.from]) {
      graph[conn.from].push(conn.to);
    }
  });

  // DFS to detect cycles
  const visited = new Set();
  const recursionStack = new Set();

  const hasCycle = (nodeId, path = []) => {
    visited.add(nodeId);
    recursionStack.add(nodeId);
    path.push(nodeId);

    const neighbors = graph[nodeId] || [];
    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        const cycle = hasCycle(neighbor, [...path]);
        if (cycle) return cycle;
      } else if (recursionStack.has(neighbor)) {
        // Cycle detected
        const cycleStart = path.indexOf(neighbor);
        const cyclePath = path.slice(cycleStart).map(id => {
          const node = nodes.find(n => n.id === id);
          return node ? node.title : id;
        });
        return cyclePath.join(' → ');
      }
    }

    recursionStack.delete(nodeId);
    return null;
  };

  for (const nodeId of Object.keys(graph)) {
    if (!visited.has(nodeId)) {
      const cycle = hasCycle(nodeId);
      if (cycle) return cycle;
    }
  }

  return null;
};

/**
 * Export workflow as JSON
 * @param {Object} workflow - Workflow to export
 * @returns {string} JSON string
 */
export const exportWorkflow = (workflow) => {
  return JSON.stringify(workflow, null, 2);
};

/**
 * Import workflow from JSON
 * @param {string} jsonString - JSON string
 * @returns {Object} Parsed workflow
 */
export const importWorkflow = (jsonString) => {
  try {
    const workflow = JSON.parse(jsonString);

    // Validate required fields
    if (!workflow.name || !workflow.nodes) {
      throw new Error('Invalid workflow structure');
    }

    return workflow;
  } catch (error) {
    throw new Error(`Failed to import workflow: ${error.message}`);
  }
};

/**
 * Get default node title based on type
 * @param {string} type - Node type
 * @returns {string} Default title
 */
const getDefaultNodeTitle = (type) => {
  const titles = {
    trigger: 'New Trigger',
    action: 'New Action',
    condition: 'New Condition',
    delay: 'Wait',
    end: 'End Workflow'
  };
  return titles[type] || 'New Node';
};

/**
 * Clone workflow with new IDs
 * @param {Object} workflow - Workflow to clone
 * @returns {Object} Cloned workflow
 */
export const cloneWorkflow = (workflow) => {
  const idMap = {};

  // Generate new IDs for all nodes
  const newNodes = workflow.nodes.map(node => {
    const newId = generateId('node');
    idMap[node.id] = newId;
    return { ...node, id: newId };
  });

  // Update connections with new IDs
  const newConnections = workflow.connections.map(conn => ({
    ...conn,
    id: generateId('conn'),
    from: idMap[conn.from],
    to: idMap[conn.to]
  }));

  return {
    ...workflow,
    id: generateId('wf'),
    name: `${workflow.name} (Copy)`,
    nodes: newNodes,
    connections: newConnections,
    metadata: {
      ...workflow.metadata,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      source: 'cloned'
    }
  };
};
