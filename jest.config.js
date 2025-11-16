/**
 * Jest Configuration for GHL Wiz
 *
 * Configured for TypeScript and ES modules support
 */

export default {
  // Use ts-jest preset for TypeScript support
  preset: 'ts-jest',

  // Test environment
  testEnvironment: 'node',

  // Roots to search for tests
  roots: ['<rootDir>/tests', '<rootDir>/mcp-servers', '<rootDir>/scripts'],

  // Test file patterns
  testMatch: [
    '**/*.test.ts',
    '**/*.spec.ts',
    '**/*.test.js',
    '**/*.spec.js'
  ],

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // Transform TypeScript files
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      useESM: true,
    }],
  },

  // ES modules support
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },

  // Coverage collection
  collectCoverageFrom: [
    'mcp-servers/**/*.ts',
    'scripts/**/*.js',
    'scripts/**/*.ts',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/coverage/**',
    '!**/*.test.ts',
    '!**/*.spec.ts',
    '!**/*.test.js',
    '!**/*.spec.js'
  ],

  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Coverage reporters
  coverageReporters: ['text', 'lcov', 'html'],

  // Coverage directory
  coverageDirectory: '<rootDir>/coverage',

  // Clear mocks between tests
  clearMocks: true,

  // Verbose output
  verbose: true,

  // Test timeout (10 seconds)
  testTimeout: 10000,

  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/chroma_db/',
    '/kb/'
  ],

  // Setup files
  setupFilesAfterEnv: [],

  // Global setup/teardown
  globalSetup: undefined,
  globalTeardown: undefined,
};
