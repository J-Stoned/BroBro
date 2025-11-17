/**
 * User Preferences API Client
 * Handles all preferences-related API calls
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get user preferences for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} User preferences
 */
export async function getPreferences(sessionId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/conversations/preferences?session_id=${sessionId}`
    );

    if (!response.ok) {
      console.error(`HTTP error! status: ${response.status}`);
      // Return defaults on error
      return {
        theme: 'light',
        notification_enabled: true,
        auto_save_enabled: true,
        preferences: {}
      };
    }

    const data = await response.json();
    return data.data || data;
  } catch (error) {
    console.error('Error fetching preferences:', error);
    // Return defaults on error
    return {
      theme: 'light',
      notification_enabled: true,
      auto_save_enabled: true,
      preferences: {}
    };
  }
}

/**
 * Update user preferences for a session
 * @param {string} sessionId - Session identifier
 * @param {Object} preferences - Preferences to update
 * @param {string} preferences.theme - Theme (light or dark)
 * @param {boolean} preferences.notification_enabled - Enable notifications
 * @param {boolean} preferences.auto_save_enabled - Enable auto-save
 * @param {Object} preferences.preferences - Additional preferences
 * @returns {Promise<Object>} Update response
 */
export async function updatePreferences(sessionId, preferences = {}) {
  try {
    // Build query parameters
    const params = new URLSearchParams({
      session_id: sessionId,
      ...preferences
    });

    // Convert nested preferences object to JSON string if present
    if (preferences.preferences && typeof preferences.preferences === 'object') {
      params.set('preferences', JSON.stringify(preferences.preferences));
    }

    const response = await fetch(
      `${API_BASE_URL}/api/conversations/preferences?${params.toString()}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.data || data;
  } catch (error) {
    console.error('Error updating preferences:', error);
    throw error;
  }
}

export default {
  getPreferences,
  updatePreferences
};
