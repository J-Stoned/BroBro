/**
 * API Utility Functions
 * Centralized API calling with error handling and retry logic
 */

// Use relative path to proxy through dev server (which forwards to backend)
// This works with any backend port and handles CORS automatically
const API_BASE_URL = '';

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(message, statusCode, isNetworkError = false) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.isNetworkError = isNetworkError;
  }
}

/**
 * Check if backend is available
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    });
    const data = await response.json();
    return {
      isOnline: response.ok,
      status: data.status,
      data
    };
  } catch (error) {
    return {
      isOnline: false,
      status: 'offline',
      error: error.message
    };
  }
}

/**
 * Make API request with error handling
 * @param {string} endpoint - API endpoint (e.g., '/api/search')
 * @param {object} options - Fetch options
 * @param {number} timeout - Request timeout in ms (default: 30000)
 */
export async function apiRequest(endpoint, options = {}, timeout = 30000) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    clearTimeout(timeoutId);

    // Handle non-OK responses
    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;

      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // Response body not JSON
      }

      throw new APIError(errorMessage, response.status, false);
    }

    // Parse JSON response
    const data = await response.json();
    return { success: true, data };

  } catch (error) {
    // Network errors (backend offline, timeout, etc.)
    if (error.name === 'AbortError') {
      throw new APIError(
        'Request timed out. The backend server may be slow or unresponsive.',
        408,
        true
      );
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(
        'Cannot connect to backend server. Please ensure the backend is running at http://localhost:8000',
        0,
        true
      );
    }

    // Re-throw APIError as-is
    if (error instanceof APIError) {
      throw error;
    }

    // Unknown error
    throw new APIError(
      error.message || 'An unknown error occurred',
      500,
      true
    );
  }
}

/**
 * GET request helper
 */
export async function apiGet(endpoint, timeout = 30000) {
  return apiRequest(endpoint, { method: 'GET' }, timeout);
}

/**
 * POST request helper - returns the fetch response object for compatibility
 */
export async function apiPost(endpoint, body, timeout = 30000) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(body),
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    // Return error response for compatibility with existing code
    const isAbort = error.name === 'AbortError';
    const message = isAbort ? 'Request timed out - backend may be slow or unresponsive' : (error.message || 'Network error');

    return new Response(
      JSON.stringify({
        detail: message,
        error: message
      }),
      {
        status: isAbort ? 408 : 0,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

/**
 * Retry logic wrapper
 * @param {Function} fn - Async function to retry
 * @param {number} retries - Number of retries (default: 3)
 * @param {number} delay - Delay between retries in ms (default: 1000)
 */
export async function withRetry(fn, retries = 3, delay = 1000) {
  let lastError;

  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on 4xx errors (client errors)
      if (error instanceof APIError &&
          error.statusCode >= 400 &&
          error.statusCode < 500 &&
          error.statusCode !== 408) {
        throw error;
      }

      // Wait before retrying (exponential backoff)
      if (i < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }

  throw lastError;
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error) {
  if (error instanceof APIError) {
    // Handle timeout errors specifically
    if (error.statusCode === 408) {
      return {
        title: 'Request Timeout',
        message: 'The request took too long to complete. The AI is processing a complex query.',
        isRetryable: true,
        suggestion: 'Try simplifying your question or wait a moment before retrying.'
      };
    }

    if (error.isNetworkError) {
      return {
        title: 'Connection Error',
        message: error.message,
        isRetryable: true,
        suggestion: 'Please check that the backend server is running and try again.'
      };
    }

    if (error.statusCode === 503) {
      return {
        title: 'Service Unavailable',
        message: 'The backend service is temporarily unavailable.',
        isRetryable: true,
        suggestion: 'Check that GOOGLE_API_KEY and ANTHROPIC_API_KEY are configured. Verify backend is running.'
      };
    }

    if (error.statusCode === 500) {
      return {
        title: 'Server Error',
        message: error.message,
        isRetryable: true,
        suggestion: 'An error occurred on the server. Please try again.'
      };
    }

    return {
      title: 'Error',
      message: error.message,
      isRetryable: error.statusCode >= 500,
      suggestion: null
    };
  }

  // Handle regular Error objects (including timeout errors)
  if (error instanceof Error) {
    // Check if it's a timeout error
    if (error.message && error.message.toLowerCase().includes('timeout')) {
      return {
        title: 'Request Timeout',
        message: error.message,
        isRetryable: true,
        suggestion: 'The request took too long. Try simplifying your question or wait before retrying.'
      };
    }

    return {
      title: 'Error',
      message: error.message || 'An unexpected error occurred',
      isRetryable: true,
      suggestion: 'Please try again.'
    };
  }

  return {
    title: 'Unknown Error',
    message: error?.message || 'An unexpected error occurred',
    isRetryable: true,
    suggestion: 'Please try again.'
  };
}

/**
 * Safe error message for rendering in JSX
 * Handles both string errors and error objects
 */
export function getErrorText(error) {
  if (!error) return '';
  if (typeof error === 'string') return error;

  // Try common error object properties
  if (error.message) return error.message;
  if (error.title) return error.title;
  if (error.msg) return error.msg;
  if (error.error) return typeof error.error === 'string' ? error.error : getErrorText(error.error);

  // Try to stringify and extract useful info
  try {
    const str = JSON.stringify(error);
    if (str && str !== '{}') return str;
  } catch (e) {
    // Ignore stringify errors
  }

  // Last resort: toString
  try {
    return String(error);
  } catch (e) {
    return 'An error occurred';
  }
}

export default {
  apiRequest,
  apiGet,
  apiPost,
  withRetry,
  checkBackendHealth,
  getErrorMessage,
  APIError
};
