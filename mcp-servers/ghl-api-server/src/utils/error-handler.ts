/**
 * Error Handler Utility
 *
 * Provides centralized error classification and retry logic for the MCP server.
 *
 * Design decisions:
 * - Classify errors by type to enable appropriate handling strategies
 * - Distinguish retryable vs. non-retryable errors
 * - Provide user-friendly error messages
 * - Extract retry information from HTTP headers
 * - Support exponential backoff for retries
 */

import { logger } from './logger.js';

/**
 * Error types for classification
 *
 * Why separate types:
 * - Enables different handling strategies per error type
 * - Makes error patterns searchable in logs
 * - Helps with debugging and monitoring
 */
export enum ErrorType {
  AUTHENTICATION = 'AUTHENTICATION_ERROR',
  RATE_LIMIT = 'RATE_LIMIT_ERROR',
  VALIDATION = 'VALIDATION_ERROR',
  NETWORK = 'NETWORK_ERROR',
  API = 'API_ERROR',
  UNKNOWN = 'UNKNOWN_ERROR'
}

/**
 * Structured error object
 */
export interface MCPError {
  type: ErrorType;
  message: string;
  details?: any;
  retryable: boolean;
  retryAfter?: number; // Seconds to wait before retry
}

/**
 * Error Handler class
 *
 * Why static methods:
 * - No state needed - pure error transformation
 * - Can be used without instantiation
 * - Easy to test and mock
 */
export class ErrorHandler {
  /**
   * Classify and structure an error
   *
   * @param error - Raw error from API call or system
   * @returns Structured MCPError with classification
   */
  static handleError(error: unknown): MCPError {
    logger.debug('Handling error', { error });

    // Handle axios HTTP errors
    if (this.isAxiosError(error)) {
      return this.handleAxiosError(error);
    }

    // Handle standard Error objects
    if (error instanceof Error) {
      return {
        type: ErrorType.UNKNOWN,
        message: error.message,
        details: { stack: error.stack },
        retryable: false
      };
    }

    // Handle unknown error types
    return {
      type: ErrorType.UNKNOWN,
      message: 'An unknown error occurred',
      details: error,
      retryable: false
    };
  }

  /**
   * Handle axios HTTP errors with detailed classification
   *
   * Why separate method:
   * - Axios errors have specific structure (response, status, headers)
   * - HTTP status codes determine error type and retry strategy
   * - Keeps main handleError method clean
   */
  private static handleAxiosError(error: any): MCPError {
    const status = error.response?.status;
    const responseData = error.response?.data;

    // 401/403 - Authentication errors
    // Why not retryable: Requires user intervention (re-authentication)
    if (status === 401 || status === 403) {
      return {
        type: ErrorType.AUTHENTICATION,
        message: 'Authentication failed. Please re-authenticate with GoHighLevel.',
        details: responseData,
        retryable: false
      };
    }

    // 429 - Rate limit errors
    // Why retryable: Temporary condition, will resolve after waiting
    if (status === 429) {
      const retryAfter = this.parseRetryAfter(error.response?.headers['retry-after']);
      return {
        type: ErrorType.RATE_LIMIT,
        message: `Rate limit exceeded. ${retryAfter ? `Retry after ${retryAfter} seconds.` : 'Please try again later.'}`,
        details: { retryAfter, responseData },
        retryable: true,
        retryAfter
      };
    }

    // 400/422 - Validation errors
    // Why not retryable: Invalid input requires correction
    if (status === 400 || status === 422) {
      return {
        type: ErrorType.VALIDATION,
        message: 'Invalid request parameters.',
        details: responseData,
        retryable: false
      };
    }

    // 404 - Not found
    // Why not retryable: Resource doesn't exist
    if (status === 404) {
      return {
        type: ErrorType.API,
        message: 'Resource not found.',
        details: responseData,
        retryable: false
      };
    }

    // 5xx - Server errors
    // Why retryable: Temporary server issues
    if (status && status >= 500) {
      return {
        type: ErrorType.API,
        message: 'GoHighLevel API server error. Please try again.',
        details: responseData,
        retryable: true
      };
    }

    // Network errors (no response received)
    // Why retryable: Network issues are often transient
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.code === 'ENOTFOUND') {
      return {
        type: ErrorType.NETWORK,
        message: 'Network error. Check your internet connection.',
        details: { code: error.code },
        retryable: true
      };
    }

    // Unknown HTTP error
    return {
      type: ErrorType.API,
      message: error.message || 'API request failed',
      details: { status, responseData },
      retryable: status ? status >= 500 : false
    };
  }

  /**
   * Parse Retry-After header from HTTP response
   *
   * @param retryAfter - Value from Retry-After header (seconds or date)
   * @returns Number of seconds to wait, or undefined
   */
  private static parseRetryAfter(retryAfter: string | undefined): number | undefined {
    if (!retryAfter) {
      return undefined;
    }

    // Try parsing as number (seconds)
    const seconds = parseInt(retryAfter, 10);
    if (!isNaN(seconds)) {
      return seconds;
    }

    // Try parsing as HTTP date
    const date = new Date(retryAfter);
    if (!isNaN(date.getTime())) {
      const now = new Date();
      return Math.max(0, Math.floor((date.getTime() - now.getTime()) / 1000));
    }

    return undefined;
  }

  /**
   * Check if error is from axios
   *
   * Why type guard:
   * - TypeScript type safety
   * - Prevents runtime errors when accessing axios-specific properties
   */
  private static isAxiosError(error: any): boolean {
    return error && error.isAxiosError === true;
  }

  /**
   * Format error for user-friendly display
   *
   * @param error - Structured MCPError
   * @returns Human-readable error message
   */
  static formatErrorForUser(error: MCPError): string {
    let message = `[${error.type}] ${error.message}`;

    // Add details if available (but avoid exposing sensitive data)
    if (error.details && typeof error.details === 'object') {
      // Filter out potentially sensitive fields
      const safeDetails = this.sanitizeDetails(error.details);
      if (Object.keys(safeDetails).length > 0) {
        message += `\n\nDetails: ${JSON.stringify(safeDetails, null, 2)}`;
      }
    }

    // Add retry information
    if (error.retryable) {
      message += '\n\nThis error is retryable. The request will be automatically retried.';
      if (error.retryAfter) {
        message += ` Waiting ${error.retryAfter} seconds before retry.`;
      }
    }

    return message;
  }

  /**
   * Remove sensitive data from error details
   *
   * Why sanitize:
   * - Prevents accidental exposure of tokens, passwords, API keys
   * - Safe to log and display to users
   */
  private static sanitizeDetails(details: any): any {
    const sensitive = ['token', 'password', 'secret', 'apiKey', 'api_key', 'authorization', 'cookie'];
    const sanitized: any = {};

    for (const [key, value] of Object.entries(details)) {
      const lowerKey = key.toLowerCase();
      if (sensitive.some(s => lowerKey.includes(s))) {
        sanitized[key] = '[REDACTED]';
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = this.sanitizeDetails(value);
      } else {
        sanitized[key] = value;
      }
    }

    return sanitized;
  }

  /**
   * Calculate exponential backoff delay
   *
   * @param attempt - Retry attempt number (0-indexed)
   * @param baseDelay - Base delay in milliseconds (default: 1000ms)
   * @param maxDelay - Maximum delay in milliseconds (default: 30000ms)
   * @returns Delay in milliseconds
   *
   * Why exponential backoff:
   * - Reduces load on failing service
   * - Increases chance of recovery
   * - Standard practice for retry logic
   */
  static getBackoffDelay(attempt: number, baseDelay: number = 1000, maxDelay: number = 30000): number {
    const delay = baseDelay * Math.pow(2, attempt);
    return Math.min(delay, maxDelay);
  }

  /**
   * Determine if error should be retried
   *
   * @param error - Structured MCPError
   * @param attempt - Current retry attempt number
   * @param maxRetries - Maximum number of retries allowed
   * @returns Whether to retry the operation
   */
  static shouldRetry(error: MCPError, attempt: number, maxRetries: number = 3): boolean {
    return error.retryable && attempt < maxRetries;
  }
}
