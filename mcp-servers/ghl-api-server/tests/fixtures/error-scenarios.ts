/**
 * Test Fixtures - Error Scenarios
 *
 * Sample error conditions for comprehensive error handling testing
 */

/**
 * Network errors
 */
export const NETWORK_ERRORS = {
  CONNECTION_REFUSED: {
    name: 'Error',
    message: 'connect ECONNREFUSED 127.0.0.1:443',
    code: 'ECONNREFUSED',
    errno: -111,
    syscall: 'connect',
    retryable: true,
  },
  TIMEOUT: {
    name: 'Error',
    message: 'Request timeout',
    code: 'ETIMEDOUT',
    errno: -110,
    syscall: 'connect',
    retryable: true,
  },
  DNS_LOOKUP_FAILED: {
    name: 'Error',
    message: 'getaddrinfo ENOTFOUND api.gohighlevel.com',
    code: 'ENOTFOUND',
    errno: -3008,
    syscall: 'getaddrinfo',
    retryable: true,
  },
  NETWORK_UNREACHABLE: {
    name: 'Error',
    message: 'Network is unreachable',
    code: 'ENETUNREACH',
    errno: -101,
    syscall: 'connect',
    retryable: true,
  },
};

/**
 * HTTP/API errors
 */
export const HTTP_ERRORS = {
  UNAUTHORIZED_401: {
    name: 'HTTPError',
    message: 'Unauthorized',
    statusCode: 401,
    retryable: false,
    response: {
      statusCode: 401,
      body: { error: 'Invalid or expired token' },
    },
  },
  FORBIDDEN_403: {
    name: 'HTTPError',
    message: 'Forbidden',
    statusCode: 403,
    retryable: false,
    response: {
      statusCode: 403,
      body: { error: 'Insufficient permissions' },
    },
  },
  NOT_FOUND_404: {
    name: 'HTTPError',
    message: 'Not Found',
    statusCode: 404,
    retryable: false,
    response: {
      statusCode: 404,
      body: { error: 'Resource not found' },
    },
  },
  RATE_LIMIT_429: {
    name: 'HTTPError',
    message: 'Too Many Requests',
    statusCode: 429,
    retryable: true,
    response: {
      statusCode: 429,
      headers: {
        'retry-after': '60',
        'x-ratelimit-remaining': '0',
      },
      body: { error: 'Rate limit exceeded' },
    },
  },
  INTERNAL_SERVER_ERROR_500: {
    name: 'HTTPError',
    message: 'Internal Server Error',
    statusCode: 500,
    retryable: true,
    response: {
      statusCode: 500,
      body: { error: 'Internal server error' },
    },
  },
  BAD_GATEWAY_502: {
    name: 'HTTPError',
    message: 'Bad Gateway',
    statusCode: 502,
    retryable: true,
    response: {
      statusCode: 502,
      body: { error: 'Bad gateway' },
    },
  },
  SERVICE_UNAVAILABLE_503: {
    name: 'HTTPError',
    message: 'Service Unavailable',
    statusCode: 503,
    retryable: true,
    response: {
      statusCode: 503,
      body: { error: 'Service temporarily unavailable' },
    },
  },
};

/**
 * Validation errors (Zod)
 */
export const VALIDATION_ERRORS = {
  INVALID_TYPE: {
    name: 'ZodError',
    message: 'Validation error',
    issues: [
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'number',
        path: ['name'],
        message: 'Expected string, received number',
      },
    ],
    retryable: false,
  },
  MISSING_REQUIRED: {
    name: 'ZodError',
    message: 'Validation error',
    issues: [
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'undefined',
        path: ['locationId'],
        message: 'Required',
      },
    ],
    retryable: false,
  },
  INVALID_FORMAT: {
    name: 'ZodError',
    message: 'Validation error',
    issues: [
      {
        code: 'invalid_string',
        validation: 'email',
        path: ['email'],
        message: 'Invalid email format',
      },
    ],
    retryable: false,
  },
};

/**
 * Authentication errors (OAuth)
 */
export const AUTH_ERRORS = {
  TOKEN_EXPIRED: {
    name: 'AuthError',
    message: 'Access token has expired',
    code: 'TOKEN_EXPIRED',
    statusCode: 401,
    retryable: false,
  },
  INVALID_TOKEN: {
    name: 'AuthError',
    message: 'Invalid access token',
    code: 'INVALID_TOKEN',
    statusCode: 401,
    retryable: false,
  },
  REFRESH_FAILED: {
    name: 'AuthError',
    message: 'Failed to refresh access token',
    code: 'REFRESH_FAILED',
    statusCode: 401,
    retryable: false,
  },
  NO_CREDENTIALS: {
    name: 'AuthError',
    message: 'No authentication credentials found',
    code: 'NO_CREDENTIALS',
    retryable: false,
  },
};

/**
 * MCP protocol errors
 */
export const MCP_ERRORS = {
  PARSE_ERROR: {
    code: -32700,
    message: 'Parse error',
  },
  INVALID_REQUEST: {
    code: -32600,
    message: 'Invalid Request',
  },
  METHOD_NOT_FOUND: {
    code: -32601,
    message: 'Method not found',
  },
  INVALID_PARAMS: {
    code: -32602,
    message: 'Invalid params',
  },
  INTERNAL_ERROR: {
    code: -32603,
    message: 'Internal error',
  },
};

/**
 * Helper: Create Error object from scenario
 */
export function createErrorFromScenario(scenario: any): Error {
  const error = new Error(scenario.message);
  error.name = scenario.name || 'Error';
  Object.assign(error, scenario);
  return error;
}

/**
 * Helper: Create HTTP error with status code
 */
export function createHttpError(
  statusCode: number,
  message: string,
  body?: any
): Error {
  const error = new Error(message);
  error.name = 'HTTPError';
  Object.assign(error, {
    statusCode,
    response: {
      statusCode,
      body: body || { error: message },
    },
  });
  return error;
}

/**
 * Helper: Create Zod validation error
 */
export function createValidationError(issues: any[]): Error {
  const error = new Error('Validation error');
  error.name = 'ZodError';
  Object.assign(error, { issues });
  return error;
}

export default {
  NETWORK_ERRORS,
  HTTP_ERRORS,
  VALIDATION_ERRORS,
  AUTH_ERRORS,
  MCP_ERRORS,
  createErrorFromScenario,
  createHttpError,
  createValidationError,
};
