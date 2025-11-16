/**
 * GHL API Client - GoHighLevel API Wrapper
 *
 * Story 3.4: Workflow Management Tools
 * Provides a clean interface to the GoHighLevel API with:
 * - OAuth token management (automatic retrieval and refresh)
 * - Rate limiting integration (respects GHL API limits)
 * - Error handling (GHL-specific error messages)
 * - Request/response logging
 *
 * Why this wrapper:
 * - Centralizes OAuth and rate limiting logic
 * - Provides consistent error handling across all API calls
 * - Makes tool implementations simpler (just call ghlClient.request())
 * - Single source of truth for GHL API configuration
 *
 * GHL API Documentation:
 * - Base URL: https://services.leadconnectorhq.com
 * - API Version: 2021-07-28 (in headers)
 * - Authentication: OAuth 2.0 Bearer token
 * - Rate Limits: 100 req/10s burst, 200k/day
 */

import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { oauthManager } from '../auth/oauth-manager.js';
import { rateLimiter } from '../utils/rate-limiter.js';
import { logger } from '../utils/logger.js';

/**
 * GHL API configuration constants
 */
const GHL_API_CONFIG = {
  baseURL: 'https://services.leadconnectorhq.com',
  apiVersion: '2021-07-28',
  timeout: 30000 // 30 second timeout
} as const;

/**
 * GHL API request options
 */
export interface GHLRequestOptions {
  /** HTTP method */
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  /** API endpoint path (without base URL) */
  endpoint: string;
  /** Request body data */
  data?: any;
  /** Query parameters */
  params?: Record<string, any>;
  /** Additional headers */
  headers?: Record<string, string>;
  /** Request timeout (ms) - overrides default */
  timeout?: number;
}

/**
 * GHL API Error Response
 */
export interface GHLErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  details?: any;
}

/**
 * GoHighLevel API Client
 *
 * Handles all communication with the GHL API including:
 * - OAuth token injection
 * - Rate limiting
 * - Error handling
 * - Request/response logging
 */
export class GHLClient {
  private baseURL: string;
  private apiVersion: string;
  private timeout: number;

  constructor() {
    this.baseURL = GHL_API_CONFIG.baseURL;
    this.apiVersion = GHL_API_CONFIG.apiVersion;
    this.timeout = GHL_API_CONFIG.timeout;

    logger.info('GHL API Client initialized', {
      baseURL: this.baseURL,
      apiVersion: this.apiVersion,
      timeout: `${this.timeout}ms`
    });
  }

  /**
   * Make an authenticated request to the GHL API
   *
   * This is the main method that all tools should use. It handles:
   * 1. Rate limiting (queues request if limits exceeded)
   * 2. OAuth token retrieval (with automatic refresh)
   * 3. Request execution
   * 4. Error handling and formatting
   *
   * @param options - Request configuration
   * @returns Promise resolving to API response data
   * @throws GHLError on API errors
   */
  async request<T = any>(options: GHLRequestOptions): Promise<T> {
    const { method, endpoint, data, params, headers, timeout } = options;

    // Log request (but not sensitive data)
    logger.debug('GHL API request initiated', {
      method,
      endpoint,
      hasData: !!data,
      hasParams: !!params
    });

    // Execute request with rate limiting
    return await rateLimiter.execute(async () => {
      try {
        // Get OAuth access token (with automatic refresh if needed)
        const accessToken = await oauthManager.getAccessToken();

        // Build request configuration
        const axiosConfig: AxiosRequestConfig = {
          method,
          url: `${this.baseURL}${endpoint}`,
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Version': this.apiVersion,
            'Content-Type': 'application/json',
            ...headers
          },
          timeout: timeout || this.timeout,
          data,
          params
        };

        // Execute request
        const response: AxiosResponse<T> = await axios(axiosConfig);

        // Log successful response
        logger.info('GHL API request successful', {
          method,
          endpoint,
          status: response.status,
          statusText: response.statusText
        });

        return response.data;

      } catch (error) {
        // Handle and format GHL API errors
        throw this.handleError(error, method, endpoint);
      }
    });
  }

  /**
   * GET request helper
   */
  async get<T = any>(endpoint: string, params?: Record<string, any>): Promise<T> {
    return this.request<T>({ method: 'GET', endpoint, params });
  }

  /**
   * POST request helper
   */
  async post<T = any>(endpoint: string, data: any): Promise<T> {
    return this.request<T>({ method: 'POST', endpoint, data });
  }

  /**
   * PUT request helper
   */
  async put<T = any>(endpoint: string, data: any): Promise<T> {
    return this.request<T>({ method: 'PUT', endpoint, data });
  }

  /**
   * PATCH request helper
   */
  async patch<T = any>(endpoint: string, data: any): Promise<T> {
    return this.request<T>({ method: 'PATCH', endpoint, data });
  }

  /**
   * DELETE request helper
   */
  async delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>({ method: 'DELETE', endpoint });
  }

  /**
   * Handle GHL API errors and convert to user-friendly format
   *
   * GHL API error patterns:
   * - 401: Invalid/expired token (should trigger OAuth refresh)
   * - 403: Insufficient permissions
   * - 404: Resource not found
   * - 422: Validation error
   * - 429: Rate limit exceeded
   * - 500/502/503: GHL server errors
   */
  private handleError(error: unknown, method: string, endpoint: string): Error {
    // Handle Axios errors (HTTP errors from GHL API)
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<GHLErrorResponse>;
      const status = axiosError.response?.status;
      const ghlError = axiosError.response?.data;

      logger.error('GHL API request failed', {
        method,
        endpoint,
        status,
        error: ghlError?.message || axiosError.message
      });

      // 401: Authentication error
      if (status === 401) {
        return new Error(
          'GHL API authentication failed. Your access token may be invalid or expired. ' +
          'Please try again - the system will automatically refresh your token.'
        );
      }

      // 403: Permission error
      if (status === 403) {
        return new Error(
          'Permission denied. Your GHL account does not have access to this resource. ' +
          'Check your OAuth scopes or contact your GHL admin.'
        );
      }

      // 404: Not found
      if (status === 404) {
        return new Error(
          `Resource not found at ${endpoint}. ` +
          'Please verify the ID is correct and the resource exists.'
        );
      }

      // 422: Validation error
      if (status === 422) {
        const details = ghlError?.details || ghlError?.message || 'Invalid request data';
        return new Error(
          `GHL API validation error: ${details}. ` +
          'Please check your request parameters and try again.'
        );
      }

      // 429: Rate limit
      if (status === 429) {
        const retryAfter = axiosError.response?.headers['retry-after'];
        return new Error(
          `GHL API rate limit exceeded. ` +
          (retryAfter ? `Please retry after ${retryAfter} seconds.` : 'Please try again later.')
        );
      }

      // 500/502/503: GHL server errors
      if (status && status >= 500) {
        return new Error(
          `GHL API server error (${status}). ` +
          'This is a temporary issue with GoHighLevel. Please try again in a few moments.'
        );
      }

      // Generic HTTP error
      return new Error(
        `GHL API request failed (${status}): ${ghlError?.message || axiosError.message}`
      );
    }

    // Handle network errors (no response from server)
    if (error instanceof Error) {
      if (error.message.includes('ECONNREFUSED')) {
        return new Error(
          'Cannot connect to GHL API. Please check your internet connection.'
        );
      }

      if (error.message.includes('ETIMEDOUT')) {
        return new Error(
          'GHL API request timed out. The server is taking too long to respond. ' +
          'Please try again.'
        );
      }

      // Generic error
      return new Error(`GHL API request failed: ${error.message}`);
    }

    // Unknown error type
    return new Error('GHL API request failed with unknown error');
  }

  /**
   * Check if GHL API is reachable (health check)
   *
   * Useful for diagnostics and testing.
   * Note: This doesn't consume rate limit quota.
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Simple request to verify connectivity
      // Using /health or similar endpoint if available
      await axios.get(`${this.baseURL}/health`, { timeout: 5000 });
      return true;
    } catch (error) {
      logger.warn('GHL API health check failed', { error });
      return false;
    }
  }

  /**
   * Get current location ID from OAuth token
   *
   * Convenience method for tools that need locationId
   */
  getLocationId(): string {
    const tokenStore = oauthManager.getTokenStore();
    if (!tokenStore?.locationId) {
      throw new Error(
        'No location ID available. Please authenticate with GoHighLevel first.'
      );
    }
    return tokenStore.locationId;
  }

  /**
   * Get API configuration details
   *
   * Useful for debugging and tool descriptions
   */
  getConfig() {
    const tokenStore = oauthManager.getTokenStore();
    return {
      baseURL: this.baseURL,
      apiVersion: this.apiVersion,
      timeout: this.timeout,
      authenticated: oauthManager.isAuthenticated(),
      locationId: tokenStore?.locationId || null
    };
  }
}

// Export singleton instance
export const ghlClient = new GHLClient();
