/**
 * Session Manager for BroBro Chat
 *
 * Manages user session identification for chat history.
 * Each browser session gets a unique ID stored in localStorage.
 */

const SESSION_STORAGE_KEY = 'brobro_session_id';

/**
 * Get or create a session ID for the current user
 * Uses crypto.randomUUID() if available, falls back to timestamp-based ID
 *
 * @returns {string} Unique session identifier
 */
export const getSessionId = () => {
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY);

  // Create new session ID if not exists
  if (!sessionId) {
    // Try to use crypto.randomUUID() (modern browsers)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      sessionId = crypto.randomUUID();
    } else {
      // Fallback: generate UUID-like string using timestamp + random
      const now = Date.now().toString(36);
      const random = Math.random().toString(36).substring(2, 15);
      sessionId = `session_${now}_${random}`;
    }

    // Store in localStorage for persistence
    try {
      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    } catch (e) {
      // Handle quota exceeded or private browsing mode
      console.warn('Could not store session ID in localStorage:', e);
    }
  }

  return sessionId;
};

/**
 * Clear the session ID (for logout/reset)
 */
export const clearSessionId = () => {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  } catch (e) {
    console.warn('Could not clear session ID:', e);
  }
};

/**
 * Get the current session ID without creating a new one
 * Returns null if no session exists
 *
 * @returns {string|null} Current session ID or null
 */
export const getCurrentSessionId = () => {
  return localStorage.getItem(SESSION_STORAGE_KEY);
};

/**
 * Check if a valid session exists
 *
 * @returns {boolean} True if session exists
 */
export const hasSession = () => {
  return !!localStorage.getItem(SESSION_STORAGE_KEY);
};

export default {
  getSessionId,
  clearSessionId,
  getCurrentSessionId,
  hasSession
};
