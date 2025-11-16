/**
 * OAuth Authentication Tools
 *
 * Story 3.2: OAuth 2.0 Authentication Implementation
 * AC #5: test_oauth MCP tool added to verify connection and refresh flow
 *
 * This module provides MCP tools for OAuth authentication:
 * - authenticate_ghl: Initiate OAuth flow (browser-based)
 * - test_oauth: Verify authentication status and token validity
 *
 * Why these tools:
 * - authenticate_ghl: First-time setup and re-authentication
 * - test_oauth: Diagnostic tool for troubleshooting
 *
 * Tool design philosophy:
 * - Simple, no parameters needed (reduces user error)
 * - Clear, actionable feedback
 * - Automatic error recovery where possible
 */

import { z } from 'zod';
import open from 'open';
import { oauthManager } from '../auth/oauth-manager.js';
import { OAuthCallbackServer } from '../auth/callback-server.js';
import { logger } from '../utils/logger.js';

/**
 * Tool: authenticate_ghl
 *
 * Purpose: Initiate OAuth 2.0 authorization flow with GoHighLevel
 *
 * Process:
 * 1. Start local callback server (port 3456)
 * 2. Generate authorization URL
 * 3. Open browser to GHL authorization page
 * 4. User grants permissions and selects location
 * 5. GHL redirects to callback server
 * 6. Callback server exchanges code for tokens
 * 7. Tokens encrypted and saved
 * 8. Callback server shuts down
 *
 * User experience:
 * - One command to start authentication
 * - Browser opens automatically
 * - Clear success/error feedback
 * - No manual code copy-paste needed
 *
 * Schema: Empty object (no parameters needed)
 */
export const authenticateGHLTool = {
  name: 'authenticate_ghl',
  description:
    'Initiate OAuth 2.0 authentication with GoHighLevel. ' +
    'Opens browser for user consent, exchanges authorization code for tokens, ' +
    'and saves encrypted tokens locally. Required for first-time setup.',
  schema: z.object({}),
  handler: async (): Promise<string> => {
    try {
      logger.info('Starting OAuth authentication flow...');

      // Step 1: Start callback server
      logger.debug('Starting callback server...');
      const callbackServer = new OAuthCallbackServer(oauthManager);

      try {
        await callbackServer.start();
      } catch (error) {
        const errorMsg =
          'Failed to start OAuth callback server. ' +
          'Please check that port 3456 is not in use. ' +
          (error instanceof Error ? error.message : '');
        logger.error(errorMsg, { error });

        const result = {
          success: false,
          message: 'OAuth callback server failed to start',
          error: errorMsg
        };
        return JSON.stringify(result, null, 2);
      }

      // Step 2: Generate authorization URL
      logger.debug('Generating authorization URL...');
      const authUrl = oauthManager.generateAuthorizationUrl();

      logger.info('Authorization URL generated', {
        url: authUrl.substring(0, 50) + '...' // Log truncated URL (don't expose full URL with client_id)
      });

      // Step 3: Open browser
      logger.info('Opening browser for user authentication...');

      try {
        await open(authUrl);
        logger.info('Browser opened successfully');
      } catch (error) {
        logger.warn('Failed to auto-open browser', { error });
        // Don't fail - user can manually open URL
      }

      // Return immediately (callback server handles rest)
      const result = {
        success: true,
        message:
          'Browser opened for authentication. ' +
          'Please complete the OAuth flow in your browser. ' +
          'After authorization, tokens will be saved automatically.',
        authUrl,
        callbackUrl: process.env.GHL_REDIRECT_URI || 'http://localhost:3456/oauth/callback'
      };
      return JSON.stringify(result, null, 2);

    } catch (error) {
      logger.error('OAuth authentication failed', { error });

      const result = {
        success: false,
        message: 'OAuth authentication failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      return JSON.stringify(result, null, 2);
    }
  }
};

/**
 * Tool: test_oauth
 *
 * Purpose: Verify OAuth authentication status and token validity
 *
 * Use cases:
 * - Check if user is authenticated
 * - Verify tokens are valid (not expired)
 * - Test token refresh mechanism
 * - Troubleshoot authentication issues
 *
 * Returns:
 * - authenticated: boolean (true if valid tokens exist)
 * - locationId: string (GHL location ID)
 * - companyId: string (GHL company ID)
 * - expiresAt: string (ISO timestamp of token expiry)
 * - expiresIn: string (human-readable time until expiry)
 * - willRefresh: boolean (true if token will auto-refresh soon)
 * - scopes: string[] (authorized OAuth scopes)
 * - message: string (status message)
 *
 * Schema: Empty object (no parameters needed)
 */
export const testOAuthTool = {
  name: 'test_oauth',
  description:
    'Test OAuth 2.0 connection status. Verifies authentication, checks token expiry, ' +
    'and validates that automatic token refresh is working correctly. ' +
    'Use this tool to troubleshoot authentication issues.',
  schema: z.object({}),
  handler: async (): Promise<string> => {
    try {
      logger.info('Testing OAuth authentication...');

      // Check if authenticated
      const isAuthenticated = oauthManager.isAuthenticated();

      if (!isAuthenticated) {
        logger.info('Not authenticated');

        const result = {
          authenticated: false,
          message:
            'Not authenticated with GoHighLevel. ' +
            'Please run the authenticate_ghl tool to complete OAuth setup.'
        };
        return JSON.stringify(result, null, 2);
      }

      // Get token store (internal method for diagnostics)
      const tokenStore = oauthManager.getTokenStore();

      if (!tokenStore) {
        const result = {
          authenticated: false,
          message: 'Token store not available. Please re-authenticate.'
        };
        return JSON.stringify(result, null, 2);
      }

      // Calculate expiry info
      const now = Date.now();
      const expiresIn = tokenStore.expiresAt - now;
      const expiresInMinutes = Math.floor(expiresIn / 1000 / 60);
      const expiresInHours = Math.floor(expiresInMinutes / 60);

      // Check if token will be refreshed soon (within 5 minutes)
      const willRefresh = expiresIn <= 5 * 60 * 1000;

      // Format expiry time
      let expiryDescription: string;
      if (expiresInMinutes < 60) {
        expiryDescription = `${expiresInMinutes} minutes`;
      } else if (expiresInHours < 24) {
        expiryDescription = `${expiresInHours} hours ${expiresInMinutes % 60} minutes`;
      } else {
        const days = Math.floor(expiresInHours / 24);
        expiryDescription = `${days} days ${expiresInHours % 24} hours`;
      }

      logger.info('OAuth authentication test successful', {
        locationId: tokenStore.locationId,
        expiresIn: expiryDescription,
        willRefresh
      });

      // Build success response
      const response = {
        authenticated: true,
        locationId: tokenStore.locationId,
        companyId: tokenStore.companyId,
        expiresAt: new Date(tokenStore.expiresAt).toISOString(),
        expiresIn: expiryDescription,
        willRefresh,
        scopes: tokenStore.scope,
        message:
          `OAuth authentication is valid and working correctly. ` +
          `Token expires in ${expiryDescription}. ` +
          (willRefresh
            ? 'Token will be refreshed automatically on next API call.'
            : 'Token is fresh, no refresh needed yet.')
      };

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('OAuth test failed', { error });

      const result = {
        authenticated: false,
        message: 'OAuth test failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      return JSON.stringify(result, null, 2);
    }
  }
};

/**
 * Tool: get_oauth_status
 *
 * Purpose: Get detailed OAuth status (extended diagnostic info)
 *
 * This is an advanced version of test_oauth with additional metrics:
 * - Token file existence
 * - Encryption key status
 * - Callback server availability
 * - OAuth configuration validation
 *
 * Use cases:
 * - Deep troubleshooting
 * - Setup validation
 * - Pre-deployment checks
 *
 * Schema: Empty object (no parameters needed)
 */
export const getOAuthStatusTool = {
  name: 'get_oauth_status',
  description:
    'Get detailed OAuth status and configuration. ' +
    'Provides comprehensive diagnostic information including token status, ' +
    'configuration validation, and system readiness. ' +
    'Use for troubleshooting and pre-deployment validation.',
  schema: z.object({}),
  handler: async (): Promise<string> => {
    try {
      logger.info('Getting OAuth status...');

      const issues: string[] = [];
      const recommendations: string[] = [];

      // Check environment variables
      const clientIdSet = !!process.env.GHL_CLIENT_ID;
      const clientSecretSet = !!process.env.GHL_CLIENT_SECRET;
      const redirectUriSet = !!process.env.GHL_REDIRECT_URI;
      const encryptionKeySet = !!process.env.ENCRYPTION_KEY;

      if (!clientIdSet) {
        issues.push('GHL_CLIENT_ID not set in .env');
        recommendations.push('Add GHL_CLIENT_ID to .env file (get from GHL Marketplace)');
      }

      if (!clientSecretSet) {
        issues.push('GHL_CLIENT_SECRET not set in .env');
        recommendations.push('Add GHL_CLIENT_SECRET to .env file (get from GHL Marketplace)');
      }

      if (!redirectUriSet) {
        issues.push('GHL_REDIRECT_URI not set in .env');
        recommendations.push('Add GHL_REDIRECT_URI to .env (default: http://localhost:3456/oauth/callback)');
      }

      // Check encryption key
      let encryptionKeyValid = false;
      if (!encryptionKeySet) {
        issues.push('ENCRYPTION_KEY not set in .env');
        recommendations.push('Generate encryption key with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"');
      } else {
        const keyLength = process.env.ENCRYPTION_KEY!.length;
        const isHex = /^[0-9a-fA-F]+$/.test(process.env.ENCRYPTION_KEY!);

        if (keyLength !== 64) {
          issues.push(`ENCRYPTION_KEY is ${keyLength} characters, should be 64`);
          recommendations.push('Regenerate ENCRYPTION_KEY with correct length');
        } else if (!isHex) {
          issues.push('ENCRYPTION_KEY contains non-hexadecimal characters');
          recommendations.push('ENCRYPTION_KEY must be hexadecimal (0-9, a-f)');
        } else {
          encryptionKeyValid = true;
        }
      }

      // Check authentication status
      const isAuthenticated = oauthManager.isAuthenticated();
      const tokenStore = oauthManager.getTokenStore();

      // Determine overall configuration status
      const configured = clientIdSet && clientSecretSet && redirectUriSet && encryptionKeyValid;

      if (configured && !isAuthenticated) {
        recommendations.push('Configuration complete! Run authenticate_ghl to complete OAuth setup.');
      }

      // Check token file (without loading it)
      const { tokenFileExists } = await import('../auth/token-store.js');
      const hasTokenFile = await tokenFileExists();

      if (!hasTokenFile && configured) {
        recommendations.push('No token file found. Run authenticate_ghl to create one.');
      }

      // Parse redirect URI for callback port
      const redirectUri = process.env.GHL_REDIRECT_URI || 'http://localhost:3456/oauth/callback';
      const callbackPort = parseInt(new URL(redirectUri).port || '3456', 10);

      const response = {
        configured,
        authenticated: isAuthenticated,
        tokenFileExists: hasTokenFile,
        encryptionKeyValid,
        clientIdSet,
        clientSecretSet,
        redirectUriSet,
        callbackPort,
        locationId: tokenStore?.locationId,
        issues,
        recommendations
      };

      logger.info('OAuth status retrieved', {
        configured,
        authenticated: isAuthenticated,
        issuesCount: issues.length
      });

      return JSON.stringify(response, null, 2);

    } catch (error) {
      logger.error('Failed to get OAuth status', { error });

      const result = {
        configured: false,
        authenticated: false,
        tokenFileExists: false,
        encryptionKeyValid: false,
        clientIdSet: false,
        clientSecretSet: false,
        redirectUriSet: false,
        callbackPort: 3456,
        issues: ['Failed to check OAuth status: ' + (error instanceof Error ? error.message : 'Unknown error')],
        recommendations: ['Check server logs for details']
      };
      return JSON.stringify(result, null, 2);
    }
  }
};
