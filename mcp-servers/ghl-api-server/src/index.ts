#!/usr/bin/env node

/**
 * GHL API MCP Server - Main Entry Point
 *
 * Story 3.1: MCP Server Foundation (Complete)
 * Story 3.2: OAuth 2.0 Authentication Implementation (Complete)
 *
 * This server provides Model Context Protocol (MCP) tools for interacting with
 * the GoHighLevel API. Built with FastMCP for minimal boilerplate and maximum
 * type safety.
 *
 * Architecture decisions:
 * - FastMCP framework: Zero-config MCP server with built-in Zod validation
 * - Stdio transport: Local development, Claude Desktop integration
 * - Modular tool structure: Each tool category in separate file
 * - OAuth 2.0: Secure authentication with automatic token refresh
 * - AES-256-CBC: Encrypted token storage for security
 * - Comprehensive logging: Track all operations for debugging
 * - Graceful error handling: Catch and log all errors to prevent crashes
 *
 * Implemented features:
 * - Story 3.1: MCP server foundation with test tools
 * - Story 3.2: OAuth 2.0 flow with encrypted token storage and auto-refresh
 *
 * Future enhancements (later stories):
 * - Story 3.3: Rate limiting for API compliance
 * - Story 3.4: Workflow management tools
 * - Story 3.5: Contact, funnel, calendar tools
 * - Story 3.6: HTTP transport for remote deployment
 */

import { FastMCP } from 'fastmcp';
import dotenv from 'dotenv';
import { logger } from './utils/logger.js';
import { ErrorHandler } from './utils/error-handler.js';
import { testConnectionTool } from './tools/test.js';
import {
  authenticateGHLTool,
  testOAuthTool,
  getOAuthStatusTool
} from './tools/auth.js';
import {
  getRateLimitStatusTool,
  resetRateLimitsTool
} from './tools/rate-limit.js';
import {
  createWorkflowTool,
  listWorkflowsTool,
  getWorkflowTool,
  updateWorkflowTool,
  deleteWorkflowTool
} from './tools/workflows.js';
import {
  createContactTool,
  searchContactsTool,
  getContactTool,
  updateContactTool
} from './tools/contacts.js';
import {
  listFunnelsTool,
  getFunnelPagesTool,
  createFunnelTool
} from './tools/funnels.js';
import {
  listFormsTool,
  getFormSubmissionsTool
} from './tools/forms.js';
import {
  listCalendarsTool,
  createAppointmentTool
} from './tools/calendars.js';
// Rate limiter imported and initialized (Story 3.3)
// import { rateLimiter } from './utils/rate-limiter.js';

// Load environment variables from .env file
// Why dotenv: Secure configuration management without hardcoding secrets
dotenv.config();

/**
 * Server configuration
 */
const SERVER_CONFIG = {
  name: 'ghl-api',
  version: '1.0.0',
  description: 'GoHighLevel API MCP Server with OAuth 2.0'
} as const;

/**
 * Validate environment variables on startup
 *
 * Story 3.2 AC #9: Environment variables validated on startup with helpful error messages
 *
 * Why validate on startup:
 * - Fail fast if configuration is invalid
 * - Provide clear guidance for setup
 * - Prevent runtime errors during authentication
 *
 * Note: OAuth credentials are optional at startup (user may not have them yet)
 * ENCRYPTION_KEY is required only when tokens need to be encrypted/decrypted
 */
function validateEnvironment(): void {
  logger.debug('Validating environment variables...');

  const warnings: string[] = [];
  const errors: string[] = [];

  // Check OAuth credentials (warnings only - not required for server to start)
  if (!process.env.GHL_CLIENT_ID) {
    warnings.push(
      'GHL_CLIENT_ID not set. You will need to add this to .env before using OAuth authentication. ' +
      'Get your Client ID from https://marketplace.gohighlevel.com/apps'
    );
  }

  if (!process.env.GHL_CLIENT_SECRET) {
    warnings.push(
      'GHL_CLIENT_SECRET not set. You will need to add this to .env before using OAuth authentication. ' +
      'Get your Client Secret from https://marketplace.gohighlevel.com/apps'
    );
  }

  if (!process.env.GHL_REDIRECT_URI) {
    warnings.push(
      'GHL_REDIRECT_URI not set. Defaulting to http://localhost:3456/oauth/callback. ' +
      'Make sure this matches your GHL Marketplace app configuration.'
    );
    process.env.GHL_REDIRECT_URI = 'http://localhost:3456/oauth/callback';
  }

  // Check encryption key (warning only - will be validated when tokens are accessed)
  if (!process.env.ENCRYPTION_KEY) {
    warnings.push(
      'ENCRYPTION_KEY not set. You will need to add this to .env before using OAuth authentication. ' +
      'Generate one with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"'
    );
  } else {
    // Validate encryption key format
    const key = process.env.ENCRYPTION_KEY;
    if (key.length !== 64) {
      errors.push(
        `ENCRYPTION_KEY must be exactly 64 hex characters (32 bytes). Current length: ${key.length}. ` +
        'Generate a valid key with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"'
      );
    } else if (!/^[0-9a-fA-F]{64}$/.test(key)) {
      errors.push(
        'ENCRYPTION_KEY must contain only hexadecimal characters (0-9, a-f, A-F). ' +
        'Generate a valid key with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"'
      );
    }
  }

  // Log warnings (non-fatal)
  if (warnings.length > 0) {
    logger.warn('Environment configuration warnings:', { warnings });
    logger.info(
      'OAuth features will be unavailable until credentials are configured. ' +
      'See .env.example for setup instructions.'
    );
  }

  // Log errors (fatal)
  if (errors.length > 0) {
    logger.error('Environment configuration errors:', { errors });
    throw new Error(
      'Environment validation failed:\n' +
      errors.map((e, i) => `${i + 1}. ${e}`).join('\n')
    );
  }

  logger.info('Environment validation complete', {
    hasOAuthCredentials: !!(process.env.GHL_CLIENT_ID && process.env.GHL_CLIENT_SECRET),
    hasEncryptionKey: !!process.env.ENCRYPTION_KEY
  });
}

/**
 * Initialize MCP server with FastMCP
 *
 * Why FastMCP:
 * - Minimal boilerplate compared to raw @modelcontextprotocol/sdk
 * - Built-in Zod schema validation
 * - Automatic tool registration and discovery
 * - TypeScript-first with excellent type inference
 * - Production-ready error handling
 */
async function initializeServer(): Promise<FastMCP> {
  logger.info('Initializing GHL API MCP Server...', {
    name: SERVER_CONFIG.name,
    version: SERVER_CONFIG.version
  });

  try {
    // Validate environment variables
    // Story 3.2 AC #9: Environment variables validated on startup
    validateEnvironment();

    // Create FastMCP server instance
    // Transport: stdio (standard input/output) for local Claude Desktop integration
    // Why stdio: Simple, reliable, no network configuration needed for local development
    const server = new FastMCP({
      name: SERVER_CONFIG.name,
      version: SERVER_CONFIG.version
    });

    logger.info('FastMCP server instance created');

    // Register test tools (Story 3.1)
    registerTestTools(server);

    // Register OAuth tools (Story 3.2)
    registerOAuthTools(server);

    // Register rate limiting tools (Story 3.3)
    registerRateLimitTools(server);

    // Register workflow management tools (Story 3.4)
    registerWorkflowTools(server);

    // Register contact management tools (Story 3.5)
    registerContactTools(server);

    // Register funnel management tools (Story 3.5)
    registerFunnelTools(server);

    // Register form management tools (Story 3.5)
    registerFormTools(server);

    // Register calendar management tools (Story 3.5)
    registerCalendarTools(server);

    logger.info('All tools registered successfully');

    return server;

  } catch (error) {
    const mcpError = ErrorHandler.handleError(error);
    logger.error('Failed to initialize MCP server', {
      error: ErrorHandler.formatErrorForUser(mcpError)
    });
    throw error;
  }
}

/**
 * Register test and diagnostic tools
 *
 * Story 3.1: MCP Server Foundation
 *
 * Why separate function:
 * - Clean separation of tool registration logic
 * - Easy to add/remove tools during development
 * - Testable in isolation
 *
 * @param server - FastMCP server instance
 */
function registerTestTools(server: FastMCP): void {
  logger.debug('Registering test tools...');

  // Register test_connection tool
  // Purpose: Verify MCP server is operational
  // AC requirement: Test connection tool implemented (Story 3.1, AC #8)
  server.addTool({
    name: testConnectionTool.name,
    description: testConnectionTool.description,
    parameters: testConnectionTool.schema,
    execute: testConnectionTool.handler
  });

  logger.info('Test tools registered', {
    tools: ['test_connection']
  });
}

/**
 * Register OAuth authentication tools
 *
 * Story 3.2: OAuth 2.0 Authentication Implementation
 * AC #5: test_oauth MCP tool added to verify connection and refresh flow
 *
 * Tools:
 * - authenticate_ghl: Initiate OAuth flow (browser-based)
 * - test_oauth: Verify authentication status and token validity
 * - get_oauth_status: Get detailed OAuth configuration status
 *
 * Why separate function:
 * - Clean separation of concerns
 * - Easy to add more OAuth tools later
 * - Testable in isolation
 *
 * @param server - FastMCP server instance
 */
function registerOAuthTools(server: FastMCP): void {
  logger.debug('Registering OAuth tools...');

  // Register authenticate_ghl tool
  // Purpose: Initiate OAuth 2.0 flow with GoHighLevel
  server.addTool({
    name: authenticateGHLTool.name,
    description: authenticateGHLTool.description,
    parameters: authenticateGHLTool.schema,
    execute: authenticateGHLTool.handler
  });

  // Register test_oauth tool
  // Purpose: Verify OAuth connection status
  // AC requirement: test_oauth tool implemented (Story 3.2, AC #5)
  server.addTool({
    name: testOAuthTool.name,
    description: testOAuthTool.description,
    parameters: testOAuthTool.schema,
    execute: testOAuthTool.handler
  });

  // Register get_oauth_status tool
  // Purpose: Get detailed OAuth configuration and status
  server.addTool({
    name: getOAuthStatusTool.name,
    description: getOAuthStatusTool.description,
    parameters: getOAuthStatusTool.schema,
    execute: getOAuthStatusTool.handler
  });

  logger.info('OAuth tools registered', {
    tools: ['authenticate_ghl', 'test_oauth', 'get_oauth_status']
  });
}

/**
 * Register Rate Limiting Tools
 *
 * Story 3.3: Rate Limiting & Error Handling
 * Tools for monitoring and managing rate limiting
 */
function registerRateLimitTools(server: FastMCP): void {
  // Register get_rate_limit_status tool
  // Purpose: Monitor current rate limiting status
  server.addTool({
    name: getRateLimitStatusTool.name,
    description: getRateLimitStatusTool.description,
    parameters: getRateLimitStatusTool.schema,
    execute: getRateLimitStatusTool.handler
  });

  // Register reset_rate_limits tool
  // Purpose: Reset rate limiting counters (testing only)
  server.addTool({
    name: resetRateLimitsTool.name,
    description: resetRateLimitsTool.description,
    parameters: resetRateLimitsTool.schema,
    execute: resetRateLimitsTool.handler
  });

  logger.info('Rate limiting tools registered', {
    tools: ['get_rate_limit_status', 'reset_rate_limits']
  });
}

/**
 * Register Workflow Management Tools
 *
 * Story 3.4: Workflow Management Tools
 * Tools for creating, listing, updating, and deleting GHL workflows
 *
 * Tools:
 * - create_workflow: Create new workflow with triggers and actions
 * - list_workflows: List all workflows in a location
 * - get_workflow: Get detailed workflow information
 * - update_workflow: Update workflow configuration
 * - delete_workflow: Delete a workflow
 */
function registerWorkflowTools(server: FastMCP): void {
  logger.debug('Registering workflow management tools...');

  // Register create_workflow tool
  server.addTool({
    name: createWorkflowTool.name,
    description: createWorkflowTool.description,
    parameters: createWorkflowTool.schema,
    execute: createWorkflowTool.handler
  });

  // Register list_workflows tool
  server.addTool({
    name: listWorkflowsTool.name,
    description: listWorkflowsTool.description,
    parameters: listWorkflowsTool.schema,
    execute: listWorkflowsTool.handler
  });

  // Register get_workflow tool
  server.addTool({
    name: getWorkflowTool.name,
    description: getWorkflowTool.description,
    parameters: getWorkflowTool.schema,
    execute: getWorkflowTool.handler
  });

  // Register update_workflow tool
  server.addTool({
    name: updateWorkflowTool.name,
    description: updateWorkflowTool.description,
    parameters: updateWorkflowTool.schema,
    execute: updateWorkflowTool.handler
  });

  // Register delete_workflow tool
  server.addTool({
    name: deleteWorkflowTool.name,
    description: deleteWorkflowTool.description,
    parameters: deleteWorkflowTool.schema,
    execute: deleteWorkflowTool.handler
  });

  logger.info('Workflow management tools registered', {
    tools: [
      'create_workflow',
      'list_workflows',
      'get_workflow',
      'update_workflow',
      'delete_workflow'
    ]
  });
}

/**
 * Register Contact Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Tools for creating, searching, updating, and retrieving contacts
 */
function registerContactTools(server: FastMCP): void {
  logger.debug('Registering contact management tools...');

  server.addTool({
    name: createContactTool.name,
    description: createContactTool.description,
    parameters: createContactTool.schema,
    execute: createContactTool.handler
  });

  server.addTool({
    name: searchContactsTool.name,
    description: searchContactsTool.description,
    parameters: searchContactsTool.schema,
    execute: searchContactsTool.handler
  });

  server.addTool({
    name: getContactTool.name,
    description: getContactTool.description,
    parameters: getContactTool.schema,
    execute: getContactTool.handler
  });

  server.addTool({
    name: updateContactTool.name,
    description: updateContactTool.description,
    parameters: updateContactTool.schema,
    execute: updateContactTool.handler
  });

  logger.info('Contact management tools registered', {
    tools: ['create_contact', 'search_contacts', 'get_contact', 'update_contact']
  });
}

/**
 * Register Funnel Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Tools for listing, viewing, and creating funnels
 */
function registerFunnelTools(server: FastMCP): void {
  logger.debug('Registering funnel management tools...');

  server.addTool({
    name: listFunnelsTool.name,
    description: listFunnelsTool.description,
    parameters: listFunnelsTool.schema,
    execute: listFunnelsTool.handler
  });

  server.addTool({
    name: getFunnelPagesTool.name,
    description: getFunnelPagesTool.description,
    parameters: getFunnelPagesTool.schema,
    execute: getFunnelPagesTool.handler
  });

  server.addTool({
    name: createFunnelTool.name,
    description: createFunnelTool.description,
    parameters: createFunnelTool.schema,
    execute: createFunnelTool.handler
  });

  logger.info('Funnel management tools registered', {
    tools: ['list_funnels', 'get_funnel_pages', 'create_funnel']
  });
}

/**
 * Register Form Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Tools for listing forms and retrieving submissions
 */
function registerFormTools(server: FastMCP): void {
  logger.debug('Registering form management tools...');

  server.addTool({
    name: listFormsTool.name,
    description: listFormsTool.description,
    parameters: listFormsTool.schema,
    execute: listFormsTool.handler
  });

  server.addTool({
    name: getFormSubmissionsTool.name,
    description: getFormSubmissionsTool.description,
    parameters: getFormSubmissionsTool.schema,
    execute: getFormSubmissionsTool.handler
  });

  logger.info('Form management tools registered', {
    tools: ['list_forms', 'get_form_submissions']
  });
}

/**
 * Register Calendar Management Tools
 *
 * Story 3.5: Contacts, Funnels, Forms, Calendars Tools
 * Tools for listing calendars and creating appointments
 */
function registerCalendarTools(server: FastMCP): void {
  logger.debug('Registering calendar management tools...');

  server.addTool({
    name: listCalendarsTool.name,
    description: listCalendarsTool.description,
    parameters: listCalendarsTool.schema,
    execute: listCalendarsTool.handler
  });

  server.addTool({
    name: createAppointmentTool.name,
    description: createAppointmentTool.description,
    parameters: createAppointmentTool.schema,
    execute: createAppointmentTool.handler
  });

  logger.info('Calendar management tools registered', {
    tools: ['list_calendars', 'create_appointment']
  });
}

/**
 * Start the MCP server
 *
 * Lifecycle:
 * 1. Initialize server with FastMCP
 * 2. Register all tools
 * 3. Start stdio transport
 * 4. Log success and wait for MCP requests
 *
 * Error handling:
 * - All errors are caught and logged
 * - Server exits with code 1 on fatal errors
 * - Graceful shutdown on SIGINT/SIGTERM
 */
async function startServer(): Promise<void> {
  try {
    logger.info('Starting GHL API MCP Server...', {
      nodeVersion: process.version,
      platform: process.platform
    });

    // Initialize server and register tools
    const server = await initializeServer();

    // Set up graceful shutdown handlers
    // Why: Ensures clean shutdown, closes resources, logs final state
    setupShutdownHandlers(server);

    // Start server with stdio transport
    // This blocks and waits for MCP protocol messages on stdin
    logger.info('Starting stdio transport...');
    await server.start({
      transportType: 'stdio'
    });

    // This log only appears if server.start() returns (which it shouldn't in stdio mode)
    logger.info('MCP server started successfully', {
      transport: 'stdio',
      server: SERVER_CONFIG.name,
      version: SERVER_CONFIG.version
    });

  } catch (error) {
    const mcpError = ErrorHandler.handleError(error);
    logger.error('Failed to start MCP server', {
      error: ErrorHandler.formatErrorForUser(mcpError)
    });

    // Exit with error code to signal failure to parent process
    process.exit(1);
  }
}

/**
 * Set up graceful shutdown handlers
 *
 * Handles:
 * - SIGINT (Ctrl+C)
 * - SIGTERM (kill command)
 * - Uncaught exceptions
 * - Unhandled promise rejections
 *
 * Why comprehensive shutdown handling:
 * - Prevents orphaned processes
 * - Logs final state for debugging
 * - Closes resources cleanly (future: OAuth tokens, DB connections)
 *
 * @param server - FastMCP server instance
 */
function setupShutdownHandlers(server: FastMCP): void {
  // Graceful shutdown on SIGINT (Ctrl+C)
  process.on('SIGINT', async () => {
    logger.info('Received SIGINT, shutting down gracefully...');
    await shutdown(server);
  });

  // Graceful shutdown on SIGTERM (kill command)
  process.on('SIGTERM', async () => {
    logger.info('Received SIGTERM, shutting down gracefully...');
    await shutdown(server);
  });

  // Log uncaught exceptions (should not happen with proper error handling)
  process.on('uncaughtException', (error: Error) => {
    const mcpError = ErrorHandler.handleError(error);
    logger.error('Uncaught exception', {
      error: ErrorHandler.formatErrorForUser(mcpError),
      stack: error.stack
    });
    // Don't exit - let the error bubble up
  });

  // Log unhandled promise rejections
  process.on('unhandledRejection', (reason: any) => {
    const mcpError = ErrorHandler.handleError(reason);
    logger.error('Unhandled promise rejection', {
      error: ErrorHandler.formatErrorForUser(mcpError)
    });
  });
}

/**
 * Perform graceful shutdown
 *
 * Steps:
 * 1. Log shutdown initiation
 * 2. Stop accepting new requests
 * 3. Close any open connections (future: OAuth, DB)
 * 4. Log final state
 * 5. Exit process
 *
 * @param server - FastMCP server instance
 */
async function shutdown(_server: FastMCP): Promise<void> {
  try {
    logger.info('Shutting down server...');

    // Future: Close OAuth sessions, database connections, etc.
    // For now, just log and exit

    logger.info('Server shutdown complete');
    process.exit(0);

  } catch (error) {
    const mcpError = ErrorHandler.handleError(error);
    logger.error('Error during shutdown', {
      error: ErrorHandler.formatErrorForUser(mcpError)
    });
    process.exit(1);
  }
}

/**
 * Main execution
 *
 * Entry point for the server.
 * Catches all errors to prevent uncaught exceptions.
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  // This file is being run directly (not imported)
  startServer().catch((error) => {
    const mcpError = ErrorHandler.handleError(error);
    logger.error('Fatal error in main execution', {
      error: ErrorHandler.formatErrorForUser(mcpError)
    });
    process.exit(1);
  });
}

// Export for testing
export { initializeServer, SERVER_CONFIG };
