/**
 * Workflow Validator
 * Epic 10: Story 10.2
 *
 * Comprehensive validation with helpful error messages
 */

const VALID_NODE_TYPES = ['trigger', 'action', 'condition', 'delay', 'end'];
const VALID_CONNECTION_TYPES = ['default', 'success', 'error', 'data'];

/**
 * Validate complete workflow
 */
export const validateWorkflow = (workflow) => {
  const errors = [];
  const warnings = [];

  if (!workflow) {
    return { valid: false, errors: [{ code: 'NO_WORKFLOW', message: 'Workflow is null or undefined' }], warnings: [] };
  }

  // Validate required fields
  if (!workflow.name || workflow.name.trim() === '') {
    errors.push({ code: 'NO_NAME', message: 'Workflow must have a name' });
  }

  if (!workflow.nodes || !Array.isArray(workflow.nodes)) {
    errors.push({ code: 'NO_NODES', message: 'Workflow must have nodes array' });
    return { valid: false, errors, warnings };
  }

  if (workflow.nodes.length === 0) {
    errors.push({ code: 'EMPTY_WORKFLOW', message: 'Workflow must have at least one node' });
  }

  // Validate trigger count
  const triggers = workflow.nodes.filter(n => n.type === 'trigger');
  if (triggers.length === 0) {
    errors.push({ code: 'NO_TRIGGER', message: 'Workflow must have exactly 1 trigger node' });
  } else if (triggers.length > 1) {
    errors.push({ code: 'MULTIPLE_TRIGGERS', message: `Workflow has ${triggers.length} triggers, should have exactly 1` });
  }

  // Validate each node
  workflow.nodes.forEach((node, index) => {
    const nodeErrors = validateNode(node, index);
    errors.push(...nodeErrors);
  });

  // Validate connections
  if (workflow.connections && Array.isArray(workflow.connections)) {
    workflow.connections.forEach((conn, index) => {
      const connErrors = validateConnection(conn, workflow.nodes, index);
      errors.push(...connErrors);
    });

    // Check for orphaned nodes
    const orphaned = findOrphanedNodes(workflow);
    orphaned.forEach(nodeId => {
      const node = workflow.nodes.find(n => n.id === nodeId);
      warnings.push({
        code: 'ORPHANED_NODE',
        message: `Node "${node?.title || nodeId}" is not connected`,
        nodeId
      });
    });

    // Check for circular connections
    const circular = detectCircular(workflow);
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
 * Validate individual node
 */
export const validateNode = (node, index) => {
  const errors = [];

  if (!node.id) {
    errors.push({ code: 'NODE_NO_ID', message: `Node at index ${index} must have id` });
  }

  if (!node.type) {
    errors.push({ code: 'NODE_NO_TYPE', message: `Node "${node.id || index}" must have type` });
  } else if (!VALID_NODE_TYPES.includes(node.type)) {
    errors.push({
      code: 'NODE_INVALID_TYPE',
      message: `Node "${node.id}" has invalid type "${node.type}". Valid types: ${VALID_NODE_TYPES.join(', ')}`
    });
  }

  if (!node.title || node.title.trim() === '') {
    errors.push({ code: 'NODE_NO_TITLE', message: `Node "${node.id}" must have title` });
  }

  if (!node.position || typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
    errors.push({ code: 'NODE_INVALID_POSITION', message: `Node "${node.id}" must have valid position {x: number, y: number}` });
  }

  if (node.position && (node.position.x < 0 || node.position.y < 0)) {
    errors.push({ code: 'NODE_NEGATIVE_POSITION', message: `Node "${node.id}" has negative position coordinates` });
  }

  return errors;
};

/**
 * Validate individual connection
 */
export const validateConnection = (connection, nodes, index) => {
  const errors = [];

  if (!connection.from) {
    errors.push({ code: 'CONN_NO_FROM', message: `Connection at index ${index} must have "from" field` });
  }

  if (!connection.to) {
    errors.push({ code: 'CONN_NO_TO', message: `Connection at index ${index} must have "to" field` });
  }

  if (connection.from === connection.to) {
    errors.push({ code: 'CONN_SELF_LOOP', message: `Connection cannot connect node to itself: ${connection.from}` });
  }

  // Check nodes exist
  if (connection.from && !nodes.find(n => n.id === connection.from)) {
    errors.push({ code: 'CONN_FROM_NOT_FOUND', message: `Connection references non-existent source node: ${connection.from}` });
  }

  if (connection.to && !nodes.find(n => n.id === connection.to)) {
    errors.push({ code: 'CONN_TO_NOT_FOUND', message: `Connection references non-existent target node: ${connection.to}` });
  }

  if (connection.type && !VALID_CONNECTION_TYPES.includes(connection.type)) {
    errors.push({
      code: 'CONN_INVALID_TYPE',
      message: `Connection has invalid type "${connection.type}". Valid types: ${VALID_CONNECTION_TYPES.join(', ')}`
    });
  }

  return errors;
};

/**
 * Find orphaned nodes
 */
const findOrphanedNodes = (workflow) => {
  if (!workflow.connections || workflow.connections.length === 0) {
    return workflow.nodes.length > 1 ? workflow.nodes.map(n => n.id) : [];
  }

  const connected = new Set();
  workflow.connections.forEach(conn => {
    connected.add(conn.from);
    connected.add(conn.to);
  });

  return workflow.nodes
    .filter(node => !connected.has(node.id))
    .map(node => node.id);
};

/**
 * Detect circular connections (DFS)
 */
const detectCircular = (workflow) => {
  const graph = {};
  workflow.nodes.forEach(node => { graph[node.id] = []; });
  workflow.connections.forEach(conn => {
    if (graph[conn.from]) graph[conn.from].push(conn.to);
  });

  const visited = new Set();
  const recStack = new Set();

  const dfs = (nodeId, path = []) => {
    visited.add(nodeId);
    recStack.add(nodeId);
    path.push(nodeId);

    const neighbors = graph[nodeId] || [];
    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        const cycle = dfs(neighbor, [...path]);
        if (cycle) return cycle;
      } else if (recStack.has(neighbor)) {
        const cycleStart = path.indexOf(neighbor);
        const cyclePath = path.slice(cycleStart).map(id => {
          const node = workflow.nodes.find(n => n.id === id);
          return node ? node.title : id;
        });
        return cyclePath.join(' → ');
      }
    }

    recStack.delete(nodeId);
    return null;
  };

  for (const nodeId of Object.keys(graph)) {
    if (!visited.has(nodeId)) {
      const cycle = dfs(nodeId);
      if (cycle) return cycle;
    }
  }

  return null;
};

/**
 * Check for errors
 */
export const checkForErrors = (workflow) => {
  const result = validateWorkflow(workflow);
  return result.errors;
};

/**
 * Check for warnings
 */
export const checkForWarnings = (workflow) => {
  const result = validateWorkflow(workflow);
  return result.warnings;
};
