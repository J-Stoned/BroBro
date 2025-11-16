/**
 * Test Tools
 *
 * Provides simple test and diagnostic tools for the MCP server.
 *
 * Tools:
 * - test_connection: Verify MCP server is operational
 *
 * Why separate file:
 * - Keeps test tools isolated from production tools
 * - Easy to import/remove for different environments
 * - Clear separation of concerns
 */

import { z } from 'zod';
import { logger } from '../utils/logger.js';

/**
 * Test connection tool - Minimal MCP tool for verification
 *
 * Purpose:
 * - Verify MCP server is running and responding
 * - Test MCP protocol handshake
 * - Provide server version and status information
 * - Simple ping/pong style diagnostic
 *
 * @returns Server status information
 */
export const testConnectionTool = {
  name: 'test_connection',
  description: 'Test MCP server connection and verify server is running. Returns server status, version, and current timestamp.',

  // No parameters needed for simple ping test
  schema: z.object({}),

  async handler() {
    logger.debug('test_connection tool invoked');

    const timestamp = new Date().toISOString();
    const response = {
      status: 'connected',
      server: 'ghl-api',
      version: '1.0.0',
      timestamp,
      message: 'GHL API MCP Server is operational'
    };

    logger.info('test_connection successful', { timestamp });

    // Return as formatted text content for MCP protocol
    return {
      content: [
        {
          type: 'text' as const,
          text: JSON.stringify(response, null, 2)
        }
      ]
    };
  }
};
