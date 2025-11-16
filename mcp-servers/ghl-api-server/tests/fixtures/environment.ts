/**
 * Test Fixtures - Environment Variables
 *
 * Mock environment variables for testing Story 3.1 components
 */

/**
 * Base test environment configuration
 */
export const TEST_ENV_BASE = {
  NODE_ENV: 'test',
  LOG_LEVEL: 'ERROR', // Reduce noise during tests
};

/**
 * Development environment simulation
 */
export const TEST_ENV_DEVELOPMENT = {
  ...TEST_ENV_BASE,
  NODE_ENV: 'development',
  LOG_LEVEL: 'DEBUG',
};

/**
 * Production environment simulation
 */
export const TEST_ENV_PRODUCTION = {
  ...TEST_ENV_BASE,
  NODE_ENV: 'production',
  LOG_LEVEL: 'INFO',
};

/**
 * Environment with all required variables (for future stories)
 */
export const TEST_ENV_COMPLETE = {
  ...TEST_ENV_BASE,
  // GHL OAuth (Story 3.2)
  GHL_CLIENT_ID: 'test-client-id-12345',
  GHL_CLIENT_SECRET: 'test-client-secret-67890',
  GHL_REDIRECT_URI: 'http://localhost:3000/oauth/callback',

  // MCP Server
  MCP_SERVER_NAME: 'ghl-api',
  MCP_SERVER_VERSION: '1.0.0',
  MCP_TRANSPORT: 'stdio',

  // Encryption (Story 3.2)
  ENCRYPTION_KEY: 'test-encryption-key-32-chars-long-abcdef',
};

/**
 * Environment with missing required variables (for error testing)
 */
export const TEST_ENV_INCOMPLETE = {
  NODE_ENV: 'test',
  // Missing LOG_LEVEL intentionally
};

/**
 * Environment with invalid values
 */
export const TEST_ENV_INVALID = {
  ...TEST_ENV_BASE,
  LOG_LEVEL: 'INVALID_LEVEL',
  MCP_TRANSPORT: 'invalid-transport',
};

/**
 * Helper function to set test environment
 */
export function setTestEnv(env: Record<string, string>): void {
  Object.keys(env).forEach(key => {
    process.env[key] = env[key];
  });
}

/**
 * Helper function to clear test environment
 */
export function clearTestEnv(env: Record<string, string>): void {
  Object.keys(env).forEach(key => {
    delete process.env[key];
  });
}

/**
 * Helper function to reset environment to test defaults
 */
export function resetTestEnv(): void {
  clearTestEnv(process.env as Record<string, string>);
  setTestEnv(TEST_ENV_BASE);
}

export default {
  TEST_ENV_BASE,
  TEST_ENV_DEVELOPMENT,
  TEST_ENV_PRODUCTION,
  TEST_ENV_COMPLETE,
  TEST_ENV_INCOMPLETE,
  TEST_ENV_INVALID,
  setTestEnv,
  clearTestEnv,
  resetTestEnv,
};
