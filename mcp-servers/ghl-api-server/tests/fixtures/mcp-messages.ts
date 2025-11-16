/**
 * Test Fixtures - MCP Protocol Messages
 *
 * Sample MCP messages for testing protocol compliance
 */

/**
 * MCP Initialize (Handshake) Request
 */
export const MCP_INITIALIZE_REQUEST = {
  jsonrpc: '2.0' as const,
  id: 1,
  method: 'initialize',
  params: {
    protocolVersion: '2024-11-05',
    capabilities: {
      tools: true,
      resources: false,
      prompts: false,
    },
    clientInfo: {
      name: 'test-client',
      version: '1.0.0',
    },
  },
};

/**
 * Expected MCP Initialize Response
 */
export const MCP_INITIALIZE_RESPONSE = {
  jsonrpc: '2.0' as const,
  id: 1,
  result: {
    protocolVersion: '2024-11-05',
    capabilities: {
      tools: true,
    },
    serverInfo: {
      name: 'ghl-api',
      version: '1.0.0',
    },
  },
};

/**
 * MCP Tools List Request
 */
export const MCP_TOOLS_LIST_REQUEST = {
  jsonrpc: '2.0' as const,
  id: 2,
  method: 'tools/list',
  params: {},
};

/**
 * Expected MCP Tools List Response
 */
export const MCP_TOOLS_LIST_RESPONSE = {
  jsonrpc: '2.0' as const,
  id: 2,
  result: {
    tools: [
      {
        name: 'test_connection',
        description: 'Test MCP server connection and verify server is running',
        inputSchema: {
          type: 'object',
          properties: {},
          required: [],
        },
      },
    ],
  },
};

/**
 * MCP Tool Call Request - test_connection
 */
export const MCP_TOOL_CALL_TEST_CONNECTION = {
  jsonrpc: '2.0' as const,
  id: 3,
  method: 'tools/call',
  params: {
    name: 'test_connection',
    arguments: {},
  },
};

/**
 * Expected MCP Tool Call Response - test_connection
 */
export const MCP_TOOL_CALL_TEST_CONNECTION_RESPONSE = {
  jsonrpc: '2.0' as const,
  id: 3,
  result: {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          status: 'connected',
          server: 'ghl-api',
          version: '1.0.0',
          timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T/),
        }),
      },
    ],
  },
};

/**
 * MCP Error Response - Tool Not Found
 */
export const MCP_ERROR_TOOL_NOT_FOUND = {
  jsonrpc: '2.0' as const,
  id: 4,
  error: {
    code: -32601,
    message: 'Tool not found',
    data: {
      toolName: 'nonexistent_tool',
    },
  },
};

/**
 * MCP Error Response - Invalid Parameters
 */
export const MCP_ERROR_INVALID_PARAMS = {
  jsonrpc: '2.0' as const,
  id: 5,
  error: {
    code: -32602,
    message: 'Invalid params',
    data: {
      validationErrors: [],
    },
  },
};

/**
 * MCP Error Response - Internal Error
 */
export const MCP_ERROR_INTERNAL = {
  jsonrpc: '2.0' as const,
  id: 6,
  error: {
    code: -32603,
    message: 'Internal error',
  },
};

/**
 * Helper: Create custom tool call request
 */
export function createToolCallRequest(
  toolName: string,
  args: Record<string, any>,
  id = 100
) {
  return {
    jsonrpc: '2.0' as const,
    id,
    method: 'tools/call',
    params: {
      name: toolName,
      arguments: args,
    },
  };
}

/**
 * Helper: Create custom error response
 */
export function createErrorResponse(
  id: number,
  code: number,
  message: string,
  data?: any
) {
  return {
    jsonrpc: '2.0' as const,
    id,
    error: {
      code,
      message,
      ...(data && { data }),
    },
  };
}

export default {
  MCP_INITIALIZE_REQUEST,
  MCP_INITIALIZE_RESPONSE,
  MCP_TOOLS_LIST_REQUEST,
  MCP_TOOLS_LIST_RESPONSE,
  MCP_TOOL_CALL_TEST_CONNECTION,
  MCP_TOOL_CALL_TEST_CONNECTION_RESPONSE,
  MCP_ERROR_TOOL_NOT_FOUND,
  MCP_ERROR_INVALID_PARAMS,
  MCP_ERROR_INTERNAL,
  createToolCallRequest,
  createErrorResponse,
};
