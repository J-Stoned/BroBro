/**
 * Test Fixtures Index
 *
 * Central export for all test fixtures and mocks
 */

export * from './environment.js';
export * from './mcp-messages.js';
export * from './tool-responses.js';
export * from './error-scenarios.js';

// Re-export defaults for convenience
import environmentFixtures from './environment.js';
import mcpMessageFixtures from './mcp-messages.js';
import toolResponseFixtures from './tool-responses.js';
import errorScenarioFixtures from './error-scenarios.js';

export default {
  environment: environmentFixtures,
  mcpMessages: mcpMessageFixtures,
  toolResponses: toolResponseFixtures,
  errorScenarios: errorScenarioFixtures,
};
