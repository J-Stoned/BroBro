/**
 * Conversation API Client for Chat History
 *
 * Handles all API calls to the backend conversation endpoints.
 * Base URL: /api/conversations
 */

const API_BASE = '/api/conversations';

/**
 * Helper function for API requests
 * @param {string} method - HTTP method
 * @param {string} endpoint - API endpoint
 * @param {object} data - Request body data (optional)
 * @returns {Promise} Response JSON
 */
const apiRequest = async (method, endpoint, data = null) => {
  const url = `${API_BASE}${endpoint}`;

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `API error: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Create a new conversation
 * @param {string} sessionId - User's session ID
 * @param {string} title - Optional conversation title
 * @returns {Promise} Created conversation data
 */
export const createConversation = async (sessionId, title = null) => {
  const response = await apiRequest('POST', '/', {
    session_id: sessionId,
    title,
  });

  if (!response.success) {
    throw new Error(response.error || 'Failed to create conversation');
  }

  return response.data;
};

/**
 * List conversations for a session
 * @param {string} sessionId - User's session ID
 * @param {object} options - Query options
 * @param {number} options.limit - Max results (default: 100)
 * @param {number} options.offset - Pagination offset (default: 0)
 * @param {boolean} options.archived - Include archived (default: false)
 * @returns {Promise} Object with conversations array and metadata
 */
export const listConversations = async (
  sessionId,
  { limit = 100, offset = 0, archived = false } = {}
) => {
  const params = new URLSearchParams({
    session_id: sessionId,
    limit,
    offset,
    archived,
  });

  const url = `${API_BASE}?${params.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list conversations');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to list conversations');
  }

  return {
    conversations: data.conversations || [],
    total: data.total || 0,
    limit: data.limit || limit,
    offset: data.offset || offset,
  };
};

/**
 * Get a conversation with all its messages
 * @param {string} conversationId - Conversation ID
 * @returns {Promise} Conversation object with messages array
 */
export const getConversation = async (conversationId) => {
  const response = await apiRequest('GET', `/${conversationId}`);

  if (!response.success) {
    throw new Error(response.error || 'Failed to get conversation');
  }

  return response.data;
};

/**
 * Update conversation metadata (title, archived status)
 * @param {string} conversationId - Conversation ID
 * @param {object} updates - Updates to apply
 * @param {string} updates.title - New title (optional)
 * @param {boolean} updates.archived - Archive status (optional)
 * @returns {Promise} Updated conversation data
 */
export const updateConversation = async (conversationId, { title = null, archived = null } = {}) => {
  const data = {};
  if (title !== null) data.title = title;
  if (archived !== null) data.archived = archived;

  const response = await apiRequest('PUT', `/${conversationId}`, data);

  if (!response.success) {
    throw new Error(response.error || 'Failed to update conversation');
  }

  return response.data;
};

/**
 * Delete a conversation
 * @param {string} conversationId - Conversation ID
 * @returns {Promise} Success response
 */
export const deleteConversation = async (conversationId) => {
  const response = await apiRequest('DELETE', `/${conversationId}`);

  if (!response.success) {
    throw new Error(response.error || 'Failed to delete conversation');
  }

  return response.data;
};

/**
 * Add a message to a conversation
 * @param {string} conversationId - Conversation ID
 * @param {string} role - Message role ('user' or 'assistant')
 * @param {string} content - Message content
 * @param {object} metadata - Optional metadata object
 * @returns {Promise} Created message data
 */
export const addMessage = async (conversationId, role, content, metadata = null) => {
  const response = await apiRequest('POST', `/${conversationId}/messages`, {
    role,
    content,
    metadata,
  });

  if (!response.success) {
    throw new Error(response.error || 'Failed to add message');
  }

  return response.data;
};

/**
 * Get messages from a conversation (with pagination)
 * @param {string} conversationId - Conversation ID
 * @param {object} options - Query options
 * @param {number} options.limit - Max results (default: 100)
 * @param {number} options.offset - Pagination offset (default: 0)
 * @returns {Promise} Object with messages array and metadata
 */
export const getMessages = async (conversationId, { limit = 100, offset = 0 } = {}) => {
  const params = new URLSearchParams({ limit, offset });

  const url = `${API_BASE}/${conversationId}/messages?${params.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get messages');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to get messages');
  }

  return {
    messages: data.data?.messages || [],
    total: data.data?.total || 0,
    limit: data.data?.limit || limit,
    offset: data.data?.offset || offset,
  };
};

/**
 * Rename a conversation (convenience method)
 * @param {string} conversationId - Conversation ID
 * @param {string} newTitle - New title
 * @returns {Promise} Updated conversation data
 */
export const renameConversation = async (conversationId, newTitle) => {
  return updateConversation(conversationId, { title: newTitle });
};

/**
 * Archive a conversation
 * @param {string} conversationId - Conversation ID
 * @returns {Promise} Updated conversation data
 */
export const archiveConversation = async (conversationId) => {
  return updateConversation(conversationId, { archived: true });
};

/**
 * Unarchive a conversation
 * @param {string} conversationId - Conversation ID
 * @returns {Promise} Updated conversation data
 */
export const unarchiveConversation = async (conversationId) => {
  return updateConversation(conversationId, { archived: false });
};

export default {
  createConversation,
  listConversations,
  getConversation,
  updateConversation,
  deleteConversation,
  addMessage,
  getMessages,
  renameConversation,
  archiveConversation,
  unarchiveConversation,
};
