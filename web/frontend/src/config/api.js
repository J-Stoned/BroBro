/**
 * Centralized API Configuration
 * Uses Vite environment variables with fallback to localhost
 *
 * Environment variables can be set in:
 * - .env files
 * - .env.development
 * - .env.production
 */

// Get API base URL from environment or use localhost default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API endpoints configuration
const API_CONFIG = {
  BASE_URL: API_BASE_URL,

  // Search & Query Endpoints
  SEARCH: `${API_BASE_URL}/api/search`,
  QUERY: `${API_BASE_URL}/api/query`,

  // Chat Endpoints
  CHAT: `${API_BASE_URL}/api/chat`,

  // Analytics Endpoints
  ANALYTICS: {
    BASE: `${API_BASE_URL}/api/analytics`,
    METRICS: `${API_BASE_URL}/api/analytics/metrics`,
    EVENTS: `${API_BASE_URL}/api/analytics/events`,
    WORKFLOWS: `${API_BASE_URL}/api/analytics/workflows`,
    SEARCHES: `${API_BASE_URL}/api/analytics/searches`,
    ALERTS: `${API_BASE_URL}/api/analytics/alerts`,
    REPORTS: `${API_BASE_URL}/api/analytics/reports`,
  },

  // Workflow Endpoints
  WORKFLOWS: {
    BASE: `${API_BASE_URL}/api/workflows`,
    LIST: `${API_BASE_URL}/api/workflows`,
    TEST: `${API_BASE_URL}/api/workflows/test`,
    VALIDATE: `${API_BASE_URL}/api/workflows/validate`,
    DEBUG: `${API_BASE_URL}/api/workflows/debug`,
  },

  // Search Analytics
  SEARCH_ANALYTICS: {
    LOG: `${API_BASE_URL}/api/search/log`,
    ANALYTICS: `${API_BASE_URL}/api/search/analytics`,
    TRENDING: `${API_BASE_URL}/api/search/trending`,
  },

  // AI Generation
  AI_GENERATION: {
    GENERATE: `${API_BASE_URL}/api/ai/generate`,
    REFINE: `${API_BASE_URL}/api/ai/refine`,
    TEMPLATES: `${API_BASE_URL}/api/ai/templates`,
  },

  // Gemini Search
  GEMINI: {
    SEARCH: `${API_BASE_URL}/api/search`,
    STATUS: `${API_BASE_URL}/api/search/status`,
  },

  // Health & Status
  HEALTH: `${API_BASE_URL}/health`,
  STATUS: `${API_BASE_URL}/api/status`,
};

// Axios interceptor configuration
export const axiosConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// WebSocket configuration
export const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL ||
  `ws://${window.location.hostname}:8000/ws/collaborate`;

export default API_CONFIG;
