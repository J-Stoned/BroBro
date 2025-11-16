/**
 * Enhancement 9: Real-time Collaboration Hook
 * Manages WebSocket connection and collaboration state
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export function useCollaboration(workflowId, userId, userName) {
  const [isConnected, setIsConnected] = useState(false);
  const [activeUsers, setActiveUsers] = useState([]);
  const [cursorPositions, setCursorPositions] = useState({});
  const [nodeLocks, setNodeLocks] = useState({});
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);

  // Generate random color for user
  const userColor = useRef(generateUserColor()).current;

  /**
   * Connect to collaboration server
   */
  const connect = useCallback(() => {
    if (!workflowId || !userId || !userName) {
      return;
    }

    try {
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      // Create WebSocket connection
      const ws = new WebSocket(
        `ws://localhost:8000/ws/collaborate?workflow_id=${workflowId}&user_id=${userId}&user_name=${encodeURIComponent(userName)}&user_color=${encodeURIComponent(userColor)}`
      );

      ws.onopen = () => {
        console.log('Collaboration WebSocket connected');
        setIsConnected(true);
        setError(null);

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'heartbeat' }));
          }
        }, 30000); // Every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      wsRef.current = ws;

    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to connect');
    }
  }, [workflowId, userId, userName]);

  /**
   * Disconnect from collaboration server
   */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    setIsConnected(false);
  }, []);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = (message) => {
    const { type, data } = message;

    switch (type) {
      case 'session_state':
        // Initial state
        setActiveUsers(data.active_users || []);
        setCursorPositions(data.cursor_positions || {});
        setNodeLocks(data.node_locks || {});
        break;

      case 'user_joined':
        setActiveUsers((users) => [...users, message.user]);
        break;

      case 'user_left':
        setActiveUsers((users) => users.filter((u) => u.user_id !== message.user_id));
        // Remove cursor position
        setCursorPositions((positions) => {
          const newPositions = { ...positions };
          delete newPositions[message.user_id];
          return newPositions;
        });
        // Release locks
        if (message.locks_released) {
          setNodeLocks((locks) => {
            const newLocks = { ...locks };
            message.locks_released.forEach((nodeId) => {
              delete newLocks[nodeId];
            });
            return newLocks;
          });
        }
        break;

      case 'cursor_update':
        setCursorPositions((positions) => ({
          ...positions,
          [message.user_id]: {
            x: message.position.x,
            y: message.position.y,
            user_name: message.user_name,
            user_color: message.user_color
          }
        }));
        break;

      case 'node_locked':
        setNodeLocks((locks) => ({
          ...locks,
          [message.node_id]: message.user_id
        }));
        break;

      case 'node_unlocked':
        setNodeLocks((locks) => {
          const newLocks = { ...locks };
          delete newLocks[message.node_id];
          return newLocks;
        });
        break;

      case 'workflow_changed':
        // Emit custom event for workflow changes
        window.dispatchEvent(new CustomEvent('collaboration:workflow_changed', {
          detail: {
            user_id: message.user_id,
            user_name: message.user_name,
            data: message.data
          }
        }));
        break;

      case 'lock_failed':
        // Emit custom event for lock failures
        window.dispatchEvent(new CustomEvent('collaboration:lock_failed', {
          detail: {
            node_id: message.node_id,
            locked_by: message.locked_by,
            message: message.message
          }
        }));
        break;

      case 'lock_acquired':
        // Successfully acquired lock
        break;

      case 'user_typing':
        // Emit typing indicator event
        window.dispatchEvent(new CustomEvent('collaboration:user_typing', {
          detail: {
            user_id: message.user_id,
            user_name: message.user_name,
            node_id: message.node_id,
            is_typing: message.is_typing
          }
        }));
        break;

      case 'pong':
        // Heartbeat response
        break;

      default:
        console.warn('Unknown message type:', type);
    }
  };

  /**
   * Update cursor position
   */
  const updateCursor = useCallback((x, y) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'cursor_move',
        data: { x, y }
      }));
    }
  }, []);

  /**
   * Lock a node for editing
   */
  const lockNode = useCallback((nodeId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'node_lock',
        node_id: nodeId
      }));
    }
  }, []);

  /**
   * Unlock a node
   */
  const unlockNode = useCallback((nodeId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'node_unlock',
        node_id: nodeId
      }));
    }
  }, []);

  /**
   * Broadcast workflow update
   */
  const broadcastUpdate = useCallback((updateData) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'workflow_update',
        data: updateData
      }));
    }
  }, []);

  /**
   * Send typing indicator
   */
  const sendTypingIndicator = useCallback((nodeId, isTyping) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing_indicator',
        node_id: nodeId,
        is_typing: isTyping
      }));
    }
  }, []);

  /**
   * Check if node is locked
   */
  const isNodeLocked = useCallback((nodeId) => {
    return nodeId in nodeLocks;
  }, [nodeLocks]);

  /**
   * Check if current user has locked a node
   */
  const hasNodeLock = useCallback((nodeId) => {
    return nodeLocks[nodeId] === userId;
  }, [nodeLocks, userId]);

  /**
   * Get who locked a node
   */
  const getNodeLocker = useCallback((nodeId) => {
    const lockerId = nodeLocks[nodeId];
    if (!lockerId) return null;

    const user = activeUsers.find((u) => u.user_id === lockerId);
    return user ? user.user_name : 'Unknown user';
  }, [nodeLocks, activeUsers]);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    // State
    isConnected,
    activeUsers,
    cursorPositions,
    nodeLocks,
    error,

    // Actions
    updateCursor,
    lockNode,
    unlockNode,
    broadcastUpdate,
    sendTypingIndicator,

    // Helpers
    isNodeLocked,
    hasNodeLock,
    getNodeLocker,
    reconnect: connect
  };
}

/**
 * Generate a random color for user cursor/highlight
 */
function generateUserColor() {
  const colors = [
    '#667eea', // Purple
    '#f56565', // Red
    '#48bb78', // Green
    '#ed8936', // Orange
    '#4299e1', // Blue
    '#9f7aea', // Violet
    '#ed64a6', // Pink
    '#38b2ac', // Teal
  ];

  return colors[Math.floor(Math.random() * colors.length)];
}
