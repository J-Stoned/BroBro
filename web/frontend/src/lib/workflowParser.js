/**
 * Workflow Parser
 * Epic 10: Story 10.2
 *
 * Parse workflow JSON from AI responses with robust error handling
 */

/**
 * Extract JSON from code block
 */
export const extractJsonFromCodeBlock = (text) => {
  if (!text) return null;

  // Try to find ```json ... ``` blocks
  const jsonBlockRegex = /```json\s*\n?([\s\S]*?)\n?```/gi;
  const matches = [...text.matchAll(jsonBlockRegex)];

  if (matches.length > 0) {
    return matches[0][1].trim();
  }

  // Try to find ``` ... ``` blocks (no language)
  const codeBlockRegex = /```\s*\n?([\s\S]*?)\n?```/gi;
  const codeMatches = [...text.matchAll(codeBlockRegex)];

  if (codeMatches.length > 0) {
    const content = codeMatches[0][1].trim();
    // Check if it looks like JSON
    if (content.startsWith('{') || content.startsWith('[')) {
      return content;
    }
  }

  // Try to find raw JSON object
  const jsonObjectRegex = /\{[\s\S]*"nodes"[\s\S]*\}/;
  const jsonMatch = text.match(jsonObjectRegex);
  if (jsonMatch) {
    return jsonMatch[0];
  }

  return null;
};

/**
 * Parse workflow JSON string
 */
export const parseWorkflowJSON = (jsonString) => {
  try {
    const parsed = JSON.parse(jsonString);
    return { success: true, workflow: parsed, error: null };
  } catch (error) {
    return {
      success: false,
      workflow: null,
      error: {
        type: 'PARSE_ERROR',
        message: `Invalid JSON: ${error.message}`,
        details: error
      }
    };
  }
};

/**
 * Validate workflow structure
 */
export const validateWorkflowStructure = (workflow) => {
  const errors = [];

  if (!workflow || typeof workflow !== 'object') {
    errors.push({ field: 'workflow', message: 'Workflow must be an object' });
    return { valid: false, errors };
  }

  // Required fields
  if (!workflow.name) {
    errors.push({ field: 'name', message: 'Workflow must have a name' });
  }

  if (!workflow.nodes || !Array.isArray(workflow.nodes)) {
    errors.push({ field: 'nodes', message: 'Workflow must have nodes array' });
  }

  if (!workflow.connections || !Array.isArray(workflow.connections)) {
    errors.push({ field: 'connections', message: 'Workflow must have connections array' });
  }

  // Validate nodes
  if (workflow.nodes) {
    workflow.nodes.forEach((node, index) => {
      if (!node.id) {
        errors.push({ field: `nodes[${index}].id`, message: 'Node must have id' });
      }
      if (!node.type) {
        errors.push({ field: `nodes[${index}].type`, message: 'Node must have type' });
      }
      if (!node.title) {
        errors.push({ field: `nodes[${index}].title`, message: 'Node must have title' });
      }
      if (!node.position || typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
        errors.push({ field: `nodes[${index}].position`, message: 'Node must have valid position {x, y}' });
      }
    });
  }

  return { valid: errors.length === 0, errors };
};

/**
 * Main parsing function
 */
export const parseWorkflowFromResponse = (aiResponse) => {
  // Extract JSON
  const jsonString = extractJsonFromCodeBlock(aiResponse);

  if (!jsonString) {
    return {
      success: false,
      workflow: null,
      error: {
        type: 'NO_JSON',
        message: 'No workflow JSON found in response',
        suggestion: 'Response should contain workflow in ```json``` code block'
      }
    };
  }

  // Parse JSON
  const parseResult = parseWorkflowJSON(jsonString);
  if (!parseResult.success) {
    return parseResult;
  }

  // Validate structure
  const validation = validateWorkflowStructure(parseResult.workflow);
  if (!validation.valid) {
    return {
      success: false,
      workflow: null,
      error: {
        type: 'VALIDATION_ERROR',
        message: 'Workflow structure is invalid',
        errors: validation.errors
      }
    };
  }

  return {
    success: true,
    workflow: parseResult.workflow,
    error: null
  };
};

/**
 * Sanitize workflow (remove potentially harmful data)
 */
export const sanitizeWorkflow = (workflow) => {
  const sanitized = { ...workflow };

  // Remove script tags or eval from any string fields
  const sanitizeString = (str) => {
    if (typeof str !== 'string') return str;
    return str.replace(/<script[^>]*>.*?<\/script>/gi, '')
              .replace(/eval\s*\(/gi, '')
              .replace(/javascript:/gi, '');
  };

  // Sanitize workflow fields
  if (sanitized.name) sanitized.name = sanitizeString(sanitized.name);
  if (sanitized.description) sanitized.description = sanitizeString(sanitized.description);

  // Sanitize nodes
  if (sanitized.nodes) {
    sanitized.nodes = sanitized.nodes.map(node => ({
      ...node,
      title: sanitizeString(node.title),
      description: sanitizeString(node.description || ''),
      params: node.params ? Object.fromEntries(
        Object.entries(node.params).map(([k, v]) => [
          k,
          typeof v === 'string' ? sanitizeString(v) : v
        ])
      ) : {}
    }));
  }

  return sanitized;
};
