/**
 * OAuth Manager - OAuth 2.0 Flow and Token Management
 *
 * Story 3.2: OAuth 2.0 Authentication Implementation
 * AC #1: OAuth 2.0 authorization flow implemented
 * AC #3: Access tokens auto-refresh before 24-hour expiry with 5-minute buffer
 * AC #7: Initial authorization flow handles user consent and location selection
 *
 * This module manages the complete OAuth 2.0 lifecycle:
 * - Authorization code exchange for tokens
 * - Automatic token refresh before expiry
 * - Token persistence via encrypted storage
 * - Multi-location support
 *
 * OAuth 2.0 Flow (Authorization Code Grant):
 * 1. User visits authorization URL (browser)
 * 2. User grants permissions and selects location
 * 3. GHL redirects to callback with authorization code
 * 4. App exchanges code for access_token + refresh_token
 * 5. Tokens saved encrypted to .tokens.enc
 * 6. Access token used for API calls (24h expiry)
 * 7. Refresh token used to get new access token before expiry
 *
 * Why Authorization Code Grant:
 * - Most secure OAuth flow for server-side apps
 * - Client secret never exposed to browser
 * - Supports refresh tokens for long-lived access
 * - Industry standard for API integrations
 */

import axios, { AxiosError } from 'axios';
import { logger } from '../utils/logger.js';
import { saveTokens, loadTokens, TokenStore } from './token-store.js';

/**
 * GHL OAuth endpoints
 *
 * Authorization URL: User-facing URL for granting permissions
 * Token URL: API endpoint for exchanging codes and refreshing tokens
 *
 * Source: GHL API documentation + architecture doc section 13.3.2
 */
const GHL_OAUTH_ENDPOINTS = {
  authorization: 'https://marketplace.gohighlevel.com/oauth/chooselocation',
  token: 'https://services.leadconnectorhq.com/oauth/token'
} as const;

/**
 * OAuth scopes required for GHL Wiz
 *
 * Why these scopes:
 * - contacts: Core CRM functionality
 * - workflows: Automation creation and management
 * - calendars: Appointment booking
 * - opportunities: Pipeline management
 * - locations: Multi-location support
 * - forms/surveys: Data collection
 *
 * Source: Story 3.2 dev notes, architecture doc section 13.17.2
 */
const GHL_REQUIRED_SCOPES = [
  'contacts.readonly',
  'contacts.write',
  'workflows.readonly',
  'workflows.write',
  'calendars.readonly',
  'calendars.write',
  'opportunities.readonly',
  'opportunities.write',
  'locations.readonly',
  'forms.readonly',
  'surveys.readonly'
] as const;

/**
 * Token refresh timing
 *
 * Why 5-minute buffer:
 * - Prevents race conditions (request starts before expiry, completes after)
 * - Accounts for clock skew between client and server
 * - Allows time for refresh request to complete
 * - Industry best practice for token refresh timing
 *
 * Token expiry: 24 hours (86400 seconds)
 * Refresh buffer: 5 minutes (300 seconds)
 * Actual refresh time: 23 hours 55 minutes after issue
 */
const TOKEN_REFRESH_BUFFER_MS = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * OAuth Manager class
 *
 * Singleton pattern: One manager per server instance
 * Thread-safe: All async operations properly awaited
 * Auto-loading: Loads existing tokens on first getAccessToken() call
 */
export class OAuth2Manager {
  private tokenStore: TokenStore | null = null;
  private isLoadingTokens = false;
  private isRefreshing = false;

  constructor() {
    logger.debug('OAuth2Manager initialized');
  }

  /**
   * Get valid access token
   *
   * Logic:
   * 1. Load tokens from file if not already loaded
   * 2. Check if token is expired or will expire soon
   * 3. Refresh token if needed
   * 4. Return valid access token
   *
   * This is the main method used by all API tools.
   * Guarantees a valid, non-expired token.
   *
   * @returns Valid access token
   * @throws Error if not authenticated or refresh fails
   */
  async getAccessToken(): Promise<string> {
    // Load tokens on first call
    if (!this.tokenStore && !this.isLoadingTokens) {
      await this.loadTokensFromFile();
    }

    // Check authentication
    if (!this.tokenStore) {
      const errorMsg =
        'Not authenticated with GoHighLevel. Please run the authenticate_ghl tool first.';
      logger.error(errorMsg);
      throw new Error(errorMsg);
    }

    // Check if token needs refresh
    if (this.isTokenExpiringSoon()) {
      logger.info('Access token expiring soon, refreshing...', {
        expiresAt: new Date(this.tokenStore.expiresAt).toISOString(),
        expiresIn: Math.round((this.tokenStore.expiresAt - Date.now()) / 1000 / 60) + ' minutes'
      });

      await this.refreshAccessToken();
    }

    return this.tokenStore.accessToken;
  }

  /**
   * Exchange authorization code for tokens
   *
   * Called by OAuth callback server when user completes authorization.
   *
   * Process:
   * 1. POST to token endpoint with authorization code
   * 2. Receive access_token, refresh_token, expires_in, location metadata
   * 3. Calculate expiry timestamp
   * 4. Save encrypted tokens to file
   *
   * @param authorizationCode - Code from OAuth callback
   * @throws Error if exchange fails or credentials invalid
   */
  async exchangeCodeForTokens(authorizationCode: string): Promise<void> {
    try {
      logger.info('Exchanging authorization code for tokens...');

      // Validate environment variables
      this.validateOAuthConfig();

      // Build token request
      const tokenRequest = {
        client_id: process.env.GHL_CLIENT_ID!,
        client_secret: process.env.GHL_CLIENT_SECRET!,
        grant_type: 'authorization_code',
        code: authorizationCode,
        redirect_uri: process.env.GHL_REDIRECT_URI!
      };

      // Exchange code for tokens
      const response = await axios.post(
        GHL_OAUTH_ENDPOINTS.token,
        new URLSearchParams(tokenRequest),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // Parse response
      const {
        access_token,
        refresh_token,
        expires_in,
        locationId,
        companyId,
        scope
      } = response.data;

      // Calculate expiry timestamp
      // Why Date.now() + (expires_in * 1000):
      // - expires_in is in seconds
      // - Date.now() returns milliseconds
      // - Adding seconds*1000 gives future timestamp in ms
      const expiresAt = Date.now() + (expires_in * 1000);

      // Create token store
      this.tokenStore = {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresAt,
        locationId,
        companyId,
        scope: scope ? scope.split(' ') : GHL_REQUIRED_SCOPES as unknown as string[]
      };

      // Save encrypted tokens
      await saveTokens(this.tokenStore);

      logger.info('OAuth tokens obtained and saved successfully', {
        locationId: this.tokenStore.locationId,
        companyId: this.tokenStore.companyId,
        expiresAt: new Date(expiresAt).toISOString(),
        scopes: this.tokenStore.scope?.length || 0
      });

      // SECURITY: Never log access_token or refresh_token

    } catch (error) {
      this.handleOAuthError(error, 'token exchange');
    }
  }

  /**
   * Refresh access token using refresh token
   *
   * Called automatically when token is expiring soon.
   *
   * Process:
   * 1. POST to token endpoint with refresh_token
   * 2. Receive new access_token (and possibly new refresh_token)
   * 3. Update token store with new values
   * 4. Save encrypted tokens to file
   *
   * Why refresh tokens:
   * - Access tokens expire after 24 hours (security best practice)
   * - Refresh tokens allow seamless renewal without user interaction
   * - User doesn't need to re-authorize every 24 hours
   *
   * @throws Error if refresh fails (user must re-authorize)
   */
  private async refreshAccessToken(): Promise<void> {
    // Prevent concurrent refresh requests
    if (this.isRefreshing) {
      logger.debug('Token refresh already in progress, waiting...');
      // Wait for ongoing refresh to complete
      while (this.isRefreshing) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      return;
    }

    this.isRefreshing = true;

    try {
      logger.info('Refreshing access token...', {
        currentExpiry: new Date(this.tokenStore!.expiresAt).toISOString()
      });

      // Validate environment variables
      this.validateOAuthConfig();

      // Build refresh request
      const refreshRequest = {
        client_id: process.env.GHL_CLIENT_ID!,
        client_secret: process.env.GHL_CLIENT_SECRET!,
        grant_type: 'refresh_token',
        refresh_token: this.tokenStore!.refreshToken
      };

      // Refresh token
      const response = await axios.post(
        GHL_OAUTH_ENDPOINTS.token,
        new URLSearchParams(refreshRequest),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // Parse response
      const {
        access_token,
        refresh_token,
        expires_in,
        scope
      } = response.data;

      // Calculate new expiry
      const expiresAt = Date.now() + (expires_in * 1000);

      // Update token store
      // Why keep old values: GHL may not return all fields in refresh response
      this.tokenStore = {
        ...this.tokenStore!,
        accessToken: access_token,
        refreshToken: refresh_token || this.tokenStore!.refreshToken, // Use new refresh token if provided
        expiresAt,
        scope: scope ? scope.split(' ') : this.tokenStore!.scope
      };

      // Save updated tokens
      await saveTokens(this.tokenStore);

      logger.info('Access token refreshed successfully', {
        newExpiry: new Date(expiresAt).toISOString(),
        expiresIn: Math.round(expires_in / 60 / 60) + ' hours'
      });

    } catch (error) {
      this.handleOAuthError(error, 'token refresh');
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Load tokens from encrypted file
   *
   * Called on first getAccessToken() call.
   * Restores authentication state from previous session.
   *
   * @throws Error if file is corrupted or decryption fails
   */
  private async loadTokensFromFile(): Promise<void> {
    this.isLoadingTokens = true;

    try {
      logger.debug('Loading tokens from encrypted file...');

      this.tokenStore = await loadTokens();

      if (this.tokenStore) {
        logger.info('Tokens loaded from file', {
          locationId: this.tokenStore.locationId,
          expiresAt: new Date(this.tokenStore.expiresAt).toISOString(),
          isExpired: Date.now() >= this.tokenStore.expiresAt
        });
      } else {
        logger.info('No existing tokens found. Authentication required.');
      }

    } catch (error) {
      logger.error('Failed to load tokens from file', { error });
      throw error;
    } finally {
      this.isLoadingTokens = false;
    }
  }

  /**
   * Check if token is expired or expiring soon
   *
   * Why 5-minute buffer:
   * - Prevents using token that expires mid-request
   * - Accounts for clock skew
   * - Allows time for refresh to complete
   *
   * @returns true if token should be refreshed
   */
  private isTokenExpiringSoon(): boolean {
    if (!this.tokenStore) {
      return true;
    }

    const now = Date.now();
    const expiryWithBuffer = this.tokenStore.expiresAt - TOKEN_REFRESH_BUFFER_MS;

    return now >= expiryWithBuffer;
  }

  /**
   * Validate OAuth configuration
   *
   * Checks required environment variables are set.
   * Called before any OAuth operation.
   *
   * @throws Error if configuration is invalid
   */
  private validateOAuthConfig(): void {
    const requiredVars = ['GHL_CLIENT_ID', 'GHL_CLIENT_SECRET', 'GHL_REDIRECT_URI'];

    for (const varName of requiredVars) {
      if (!process.env[varName]) {
        const errorMsg =
          `Missing required environment variable: ${varName}. ` +
          `Please add to .env file. See .env.example for template.`;
        logger.error(errorMsg);
        throw new Error(errorMsg);
      }
    }
  }

  /**
   * Handle OAuth errors with user-friendly messages
   *
   * Common errors:
   * - invalid_client: Wrong client ID or secret
   * - invalid_grant: Authorization code expired or already used
   * - invalid_grant (refresh): Refresh token expired (60 days)
   * - Network errors: Connection issues
   *
   * @param error - Caught error
   * @param operation - OAuth operation being performed
   * @throws Error with user-friendly message
   */
  private handleOAuthError(error: unknown, operation: string): never {
    logger.error(`OAuth ${operation} failed`, { error });

    // Axios HTTP errors
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<any>;
      const status = axiosError.response?.status;
      const errorCode = axiosError.response?.data?.error;
      const errorDescription = axiosError.response?.data?.error_description;

      // Invalid client credentials
      if (status === 401 || errorCode === 'invalid_client') {
        throw new Error(
          'Invalid OAuth credentials. Please check:\n' +
          '1. GHL_CLIENT_ID and GHL_CLIENT_SECRET in .env are correct\n' +
          '2. Credentials match your GHL Marketplace app\n' +
          '3. No extra spaces or quotes in .env values'
        );
      }

      // Invalid or expired authorization code / refresh token
      if (errorCode === 'invalid_grant') {
        if (operation === 'token refresh') {
          throw new Error(
            'Refresh token expired (60-day limit). Please re-authenticate:\n' +
            '1. Run authenticate_ghl tool\n' +
            '2. Complete OAuth flow in browser\n' +
            '3. Tokens will be saved automatically'
          );
        } else {
          throw new Error(
            'Authorization code expired or already used. Please:\n' +
            '1. Start authorization flow again\n' +
            '2. Complete OAuth flow within 60 seconds\n' +
            '3. Do not refresh the callback page'
          );
        }
      }

      // Network errors
      if (axiosError.code === 'ENOTFOUND' || axiosError.code === 'ECONNREFUSED') {
        throw new Error(
          'Network error during OAuth request. Please check:\n' +
          '1. Internet connection is active\n' +
          '2. GHL API is accessible (not blocked by firewall)\n' +
          '3. Try again in a few moments'
        );
      }

      // Other HTTP errors
      throw new Error(
        `OAuth ${operation} failed with status ${status}.\n` +
        `Error: ${errorCode || 'unknown'}\n` +
        `Description: ${errorDescription || 'No details provided'}`
      );
    }

    // Non-Axios errors
    throw new Error(
      `OAuth ${operation} failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }

  /**
   * Generate authorization URL for user
   *
   * Used by authenticate_ghl tool to start OAuth flow.
   *
   * @returns Full authorization URL to open in browser
   */
  generateAuthorizationUrl(): string {
    this.validateOAuthConfig();

    const params = new URLSearchParams({
      client_id: process.env.GHL_CLIENT_ID!,
      redirect_uri: process.env.GHL_REDIRECT_URI!,
      response_type: 'code',
      scope: GHL_REQUIRED_SCOPES.join(' ')
    });

    return `${GHL_OAUTH_ENDPOINTS.authorization}?${params.toString()}`;
  }

  /**
   * Check if user is authenticated
   *
   * Used by test_oauth tool.
   *
   * @returns true if valid tokens exist, false otherwise
   */
  isAuthenticated(): boolean {
    return this.tokenStore !== null && !this.isTokenExpiringSoon();
  }

  /**
   * Get current location ID
   *
   * Used by API tools for location-specific requests.
   *
   * @returns GHL location ID
   * @throws Error if not authenticated
   */
  getLocationId(): string {
    if (!this.tokenStore?.locationId) {
      throw new Error('No location ID available. Please authenticate first.');
    }
    return this.tokenStore.locationId;
  }

  /**
   * Get token store (for test_oauth tool)
   *
   * @returns Current token store or null
   */
  getTokenStore(): TokenStore | null {
    return this.tokenStore;
  }
}

// Export singleton instance
export const oauthManager = new OAuth2Manager();
