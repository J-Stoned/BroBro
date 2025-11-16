/**
 * Test Fixtures - Expected Tool Responses
 *
 * Sample expected outputs from MCP tools for validation testing
 */

/**
 * Successful test_connection response
 */
export const TEST_CONNECTION_SUCCESS = {
  status: 'connected',
  server: 'ghl-api',
  version: '1.0.0',
  timestamp: '2025-10-26T12:00:00.000Z', // Will vary in actual tests
};

/**
 * Helper: Create test_connection response with current timestamp
 */
export function createTestConnectionResponse(timestamp?: string) {
  return {
    status: 'connected',
    server: 'ghl-api',
    version: '1.0.0',
    timestamp: timestamp || new Date().toISOString(),
  };
}

/**
 * Tool response validation schema (for reference)
 */
export const TEST_CONNECTION_SCHEMA = {
  type: 'object',
  required: ['status', 'server', 'version', 'timestamp'],
  properties: {
    status: {
      type: 'string',
      enum: ['connected'],
    },
    server: {
      type: 'string',
      const: 'ghl-api',
    },
    version: {
      type: 'string',
      pattern: '^\\d+\\.\\d+\\.\\d+$',
    },
    timestamp: {
      type: 'string',
      format: 'date-time',
    },
  },
};

/**
 * Error scenarios for test_connection
 */
export const TEST_CONNECTION_ERRORS = {
  SERVER_NOT_INITIALIZED: {
    error: 'Server not initialized',
    code: 'SERVER_NOT_READY',
  },
  INTERNAL_ERROR: {
    error: 'Internal server error',
    code: 'INTERNAL_ERROR',
  },
};

/**
 * Future tool responses (for Stories 3.4, 3.5)
 * These are placeholders for when additional tools are implemented
 */

// Story 3.4 - Workflow tools (placeholder)
export const WORKFLOW_LIST_SUCCESS = {
  workflows: [],
  total: 0,
  locationId: 'loc_123',
};

// Story 3.5 - Contact tools (placeholder)
export const CONTACT_GET_SUCCESS = {
  id: 'contact_123',
  name: 'John Doe',
  email: 'john@example.com',
};

/**
 * Helper: Validate response matches schema
 */
export function validateTestConnectionResponse(response: any): boolean {
  return (
    typeof response === 'object' &&
    response !== null &&
    response.status === 'connected' &&
    response.server === 'ghl-api' &&
    typeof response.version === 'string' &&
    typeof response.timestamp === 'string' &&
    !isNaN(Date.parse(response.timestamp))
  );
}

/**
 * Helper: Assert response is valid test_connection
 */
export function assertValidTestConnection(response: any): void {
  if (!validateTestConnectionResponse(response)) {
    throw new Error(
      `Invalid test_connection response: ${JSON.stringify(response)}`
    );
  }
}

export default {
  TEST_CONNECTION_SUCCESS,
  TEST_CONNECTION_SCHEMA,
  TEST_CONNECTION_ERRORS,
  WORKFLOW_LIST_SUCCESS,
  CONTACT_GET_SUCCESS,
  createTestConnectionResponse,
  validateTestConnectionResponse,
  assertValidTestConnection,
};
