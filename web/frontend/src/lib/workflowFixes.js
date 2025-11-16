/**
 * Workflow Fix Implementations
 * Enhancement 4: Story WV-3 - One-Click Fixes
 *
 * Applies automatic fixes to workflow validation issues
 */

/**
 * Apply a fix suggestion to the workflow
 * @param {Object} workflow - Current workflow state
 * @param {Object} issue - Validation issue with fix_suggestion
 * @returns {Object} Updated workflow
 */
export function applyWorkflowFix(workflow, issue) {
  if (!issue.fix_suggestion) {
    throw new Error('No fix suggestion provided');
  }

  const { action } = issue.fix_suggestion;
  const fixHandlers = {
    'add_condition_node': addErrorHandling,
    'add_delay_and_followup': addDelayAndFollowup,
    'add_personalization': addPersonalization,
    'add_unsubscribe_link': addUnsubscribeLink,
    'add_validation_condition': addValidationCondition,
    'add_delay': addDelay,
    'add_tag': addTag,
    'merge_nodes': mergeDuplicateNodes,
    'break_loop': breakInfiniteLoop,
    'connect_node': connectOrphanedNode,
    'add_ab_test': addABTest,
    'add_goal_tracking': addGoalTracking,
    'add_sms_fallback': addSMSFallback
  };

  const handler = fixHandlers[action];
  if (!handler) {
    throw new Error(`Unknown fix action: ${action}`);
  }

  return handler(workflow, issue);
}

/**
 * Add error handling after an action node
 */
function addErrorHandling(workflow, issue) {
  const { after_node, type } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  // Find the target node
  const targetNode = nodes.find(n => n.id === after_node);
  if (!targetNode) {
    throw new Error('Target node not found');
  }

  // Create condition node for error handling
  const conditionNode = {
    id: `node-${Date.now()}`,
    type: 'condition',
    data: {
      title: 'Check Delivery Status',
      description: 'Handle delivery failure',
      condition_type: type || 'check_delivery_status',
      logic: 'if_failed'
    },
    position: {
      x: targetNode.position.x + 250,
      y: targetNode.position.y
    }
  };

  // Create retry/fallback action
  const fallbackNode = {
    id: `node-${Date.now() + 1}`,
    type: 'action',
    data: {
      title: 'Retry or Notify',
      description: 'Handle failed delivery',
      action_type: 'send_internal_notification'
    },
    position: {
      x: targetNode.position.x + 500,
      y: targetNode.position.y + 100
    }
  };

  nodes.push(conditionNode, fallbackNode);

  // Update connections
  const outgoingConnections = connections.filter(c => c.from === after_node);
  connections.push(
    { from: after_node, to: conditionNode.id, label: 'then' },
    { from: conditionNode.id, to: fallbackNode.id, label: 'failed' }
  );

  // Reconnect original outgoing to condition's success path
  if (outgoingConnections.length > 0) {
    connections.push({
      from: conditionNode.id,
      to: outgoingConnections[0].to,
      label: 'success'
    });
  }

  return { ...workflow, nodes, connections };
}

/**
 * Add delay + follow-up action
 */
function addDelayAndFollowup(workflow, issue) {
  const { after_node, delay_duration } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  const targetNode = nodes.find(n => n.id === after_node);
  if (!targetNode) {
    throw new Error('Target node not found');
  }

  // Create delay node
  const delayNode = {
    id: `node-${Date.now()}`,
    type: 'delay',
    data: {
      title: 'Wait',
      description: `${Math.floor(delay_duration / 1440)} day delay`,
      delay_duration: delay_duration || 2880 // 2 days in minutes
    },
    position: {
      x: targetNode.position.x,
      y: targetNode.position.y + 150
    }
  };

  // Create follow-up action
  const followupNode = {
    id: `node-${Date.now() + 1}`,
    type: 'action',
    data: {
      title: 'Follow-up Message',
      description: 'Check in with contact',
      action_type: 'send_email',
      message: 'Hi {{contact.first_name}}, just following up...'
    },
    position: {
      x: targetNode.position.x,
      y: targetNode.position.y + 300
    }
  };

  nodes.push(delayNode, followupNode);

  // Update connections
  connections.push(
    { from: after_node, to: delayNode.id, label: 'then' },
    { from: delayNode.id, to: followupNode.id, label: 'after' }
  );

  return { ...workflow, nodes, connections };
}

/**
 * Add personalization token to message
 */
function addPersonalization(workflow, issue) {
  const { node_id, token } = issue.fix_suggestion;
  const nodes = workflow.nodes.map(node => {
    if (node.id === node_id) {
      const updatedData = { ...node.data };

      // Add personalization to message
      if (updatedData.message) {
        const tokenToAdd = token || '{{contact.first_name}}';
        updatedData.message = `Hi ${tokenToAdd}, ${updatedData.message}`;
      }

      return { ...node, data: updatedData };
    }
    return node;
  });

  return { ...workflow, nodes };
}

/**
 * Add unsubscribe link to email
 */
function addUnsubscribeLink(workflow, issue) {
  const { node_id } = issue.fix_suggestion;
  const nodes = workflow.nodes.map(node => {
    if (node.id === node_id) {
      const updatedData = { ...node.data };

      // Add unsubscribe link to message
      if (updatedData.message) {
        updatedData.message += '\n\n[Unsubscribe]({{unsubscribe_url}})';
      }

      updatedData.has_unsubscribe = true;

      return { ...node, data: updatedData };
    }
    return node;
  });

  return { ...workflow, nodes };
}

/**
 * Add validation condition before action
 */
function addValidationCondition(workflow, issue) {
  const { before_node, check } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  const targetNode = nodes.find(n => n.id === before_node);
  if (!targetNode) {
    throw new Error('Target node not found');
  }

  // Create validation condition
  const validationNode = {
    id: `node-${Date.now()}`,
    type: 'condition',
    data: {
      title: 'Validate Contact Data',
      description: `Check if contact ${check || 'has_email'}`,
      condition_type: 'check_field_exists',
      field: check === 'has_phone' ? 'phone' : 'email'
    },
    position: {
      x: targetNode.position.x - 250,
      y: targetNode.position.y
    }
  };

  nodes.push(validationNode);

  // Update connections - insert validation before target
  const incomingConnections = connections.filter(c => c.to === before_node);
  incomingConnections.forEach(conn => {
    conn.to = validationNode.id;
  });

  connections.push({
    from: validationNode.id,
    to: before_node,
    label: 'valid'
  });

  return { ...workflow, nodes, connections };
}

/**
 * Add delay between actions
 */
function addDelay(workflow, issue) {
  const { between_nodes, delay_hours } = issue.fix_suggestion;
  const [fromNode, toNode] = between_nodes || [];

  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  const sourceNode = nodes.find(n => n.id === fromNode);
  const targetNode = nodes.find(n => n.id === toNode);

  if (!sourceNode || !targetNode) {
    throw new Error('Nodes not found');
  }

  // Create delay node
  const delayNode = {
    id: `node-${Date.now()}`,
    type: 'delay',
    data: {
      title: 'Wait',
      description: `${delay_hours || 24} hour delay`,
      delay_duration: (delay_hours || 24) * 60 // Convert to minutes
    },
    position: {
      x: (sourceNode.position.x + targetNode.position.x) / 2,
      y: (sourceNode.position.y + targetNode.position.y) / 2
    }
  };

  nodes.push(delayNode);

  // Update connections
  const connectionIndex = connections.findIndex(c => c.from === fromNode && c.to === toNode);
  if (connectionIndex >= 0) {
    const originalLabel = connections[connectionIndex].label;
    connections[connectionIndex] = { from: fromNode, to: delayNode.id, label: originalLabel };
    connections.push({ from: delayNode.id, to: toNode, label: 'after' });
  }

  return { ...workflow, nodes, connections };
}

/**
 * Add tracking tag
 */
function addTag(workflow, issue) {
  const { node_id, tag_name } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];

  // Create tag action node
  const tagNode = {
    id: `node-${Date.now()}`,
    type: 'action',
    data: {
      title: 'Add Tag',
      description: `Tag: ${tag_name || 'workflow-completed'}`,
      action_type: 'add_tag',
      tag_name: tag_name || 'workflow-completed'
    },
    position: {
      x: 400,
      y: Math.max(...nodes.map(n => n.position.y)) + 150
    }
  };

  nodes.push(tagNode);

  return { ...workflow, nodes };
}

/**
 * Merge duplicate nodes (placeholder - would need more complex logic)
 */
function mergeDuplicateNodes(workflow, issue) {
  // For now, just mark the duplicates
  console.warn('Merge duplicate nodes: Manual intervention recommended');
  return workflow;
}

/**
 * Break infinite loop (placeholder)
 */
function breakInfiniteLoop(workflow, issue) {
  // Would need cycle detection and breaking logic
  console.warn('Break infinite loop: Manual intervention recommended');
  return workflow;
}

/**
 * Connect orphaned node
 */
function connectOrphanedNode(workflow, issue) {
  const { node_id } = issue.fix_suggestion;
  const connections = [...workflow.connections];
  const nodes = workflow.nodes;

  // Find a logical predecessor (e.g., last trigger or previous action)
  const triggers = nodes.filter(n => n.type === 'trigger');
  const lastTrigger = triggers[triggers.length - 1];

  if (lastTrigger) {
    connections.push({
      from: lastTrigger.id,
      to: node_id,
      label: 'then'
    });
  }

  return { ...workflow, connections };
}

/**
 * Add A/B test variant
 */
function addABTest(workflow, issue) {
  const { node_id } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  const targetNode = nodes.find(n => n.id === node_id);
  if (!targetNode) {
    throw new Error('Target node not found');
  }

  // Create variant B node
  const variantNode = {
    id: `node-${Date.now()}`,
    type: 'action',
    data: {
      ...targetNode.data,
      title: `${targetNode.data.title} (Variant B)`,
      description: 'Alternative version for testing'
    },
    position: {
      x: targetNode.position.x + 250,
      y: targetNode.position.y
    }
  };

  nodes.push(variantNode);

  // Create A/B split condition
  const splitNode = {
    id: `node-${Date.now() + 1}`,
    type: 'condition',
    data: {
      title: 'A/B Split',
      description: '50/50 traffic split',
      condition_type: 'random_split',
      split_percentage: 50
    },
    position: {
      x: targetNode.position.x - 150,
      y: targetNode.position.y - 100
    }
  };

  nodes.push(splitNode);

  return { ...workflow, nodes, connections };
}

/**
 * Add goal tracking
 */
function addGoalTracking(workflow, issue) {
  const nodes = [...workflow.nodes];

  // Add goal tracking node at the end
  const goalNode = {
    id: `node-${Date.now()}`,
    type: 'action',
    data: {
      title: 'Track Goal',
      description: 'Measure workflow success',
      action_type: 'track_goal',
      goal_name: 'workflow_conversion'
    },
    position: {
      x: 400,
      y: Math.max(...nodes.map(n => n.position.y)) + 150
    }
  };

  nodes.push(goalNode);

  return { ...workflow, nodes };
}

/**
 * Add SMS fallback for email
 */
function addSMSFallback(workflow, issue) {
  const { node_id } = issue.fix_suggestion;
  const nodes = [...workflow.nodes];
  const connections = [...workflow.connections];

  const emailNode = nodes.find(n => n.id === node_id);
  if (!emailNode) {
    throw new Error('Email node not found');
  }

  // Create SMS fallback node
  const smsNode = {
    id: `node-${Date.now()}`,
    type: 'action',
    data: {
      title: 'SMS Fallback',
      description: 'Send SMS if email fails',
      action_type: 'send_sms',
      message: 'Quick update for you...'
    },
    position: {
      x: emailNode.position.x + 250,
      y: emailNode.position.y + 150
    }
  };

  nodes.push(smsNode);

  // Would typically connect through an error condition
  connections.push({
    from: node_id,
    to: smsNode.id,
    label: 'if_failed'
  });

  return { ...workflow, nodes, connections };
}
