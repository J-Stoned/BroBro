"""
Enhancement 9: Real-time Collaboration WebSocket Server
Handles real-time collaboration, presence, cursor sync, and node locking
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, List
from datetime import datetime
import json
import asyncio

class CollaborationManager:
    """
    Manages real-time collaboration sessions

    Features:
    - User presence tracking
    - Cursor position synchronization
    - Node locking/unlocking
    - Real-time workflow updates
    - Active users list
    """

    def __init__(self):
        # workflow_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # workflow_id -> user_id -> user info
        self.active_users: Dict[str, Dict[str, Dict]] = {}

        # workflow_id -> user_id -> cursor position
        self.cursor_positions: Dict[str, Dict[str, Dict]] = {}

        # workflow_id -> node_id -> user_id (who has it locked)
        self.node_locks: Dict[str, Dict[str, str]] = {}

        # websocket -> user metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(
        self,
        websocket: WebSocket,
        workflow_id: str,
        user_id: str,
        user_name: str,
        user_color: str = '#667eea'
    ):
        """
        Connect a user to a collaboration session

        Args:
            websocket: WebSocket connection
            workflow_id: Workflow being edited
            user_id: Unique user identifier
            user_name: Display name
            user_color: Cursor/highlight color
        """
        await websocket.accept()

        # Initialize workflow session if needed
        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = set()
            self.active_users[workflow_id] = {}
            self.cursor_positions[workflow_id] = {}
            self.node_locks[workflow_id] = {}

        # Add connection
        self.active_connections[workflow_id].add(websocket)

        # Store user info
        user_info = {
            'user_id': user_id,
            'user_name': user_name,
            'user_color': user_color,
            'connected_at': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat()
        }

        self.active_users[workflow_id][user_id] = user_info
        self.connection_metadata[websocket] = {
            'workflow_id': workflow_id,
            'user_id': user_id,
            **user_info
        }

        # Notify others of new user
        await self.broadcast(
            workflow_id,
            {
                'type': 'user_joined',
                'user': user_info
            },
            exclude=websocket
        )

        # Send current state to new user
        await websocket.send_json({
            'type': 'session_state',
            'data': {
                'active_users': list(self.active_users[workflow_id].values()),
                'cursor_positions': self.cursor_positions[workflow_id],
                'node_locks': self.node_locks[workflow_id]
            }
        })

    def disconnect(self, websocket: WebSocket):
        """Disconnect a user and cleanup"""
        if websocket not in self.connection_metadata:
            return

        metadata = self.connection_metadata[websocket]
        workflow_id = metadata['workflow_id']
        user_id = metadata['user_id']

        # Remove connection
        if workflow_id in self.active_connections:
            self.active_connections[workflow_id].discard(websocket)

            # Remove user info
            if user_id in self.active_users.get(workflow_id, {}):
                del self.active_users[workflow_id][user_id]

            # Remove cursor position
            if user_id in self.cursor_positions.get(workflow_id, {}):
                del self.cursor_positions[workflow_id][user_id]

            # Release all locks held by this user
            locks_to_release = [
                node_id for node_id, locked_by in self.node_locks.get(workflow_id, {}).items()
                if locked_by == user_id
            ]

            for node_id in locks_to_release:
                del self.node_locks[workflow_id][node_id]

            # Cleanup empty workflow sessions
            if not self.active_connections[workflow_id]:
                del self.active_connections[workflow_id]
                del self.active_users[workflow_id]
                del self.cursor_positions[workflow_id]
                del self.node_locks[workflow_id]

        del self.connection_metadata[websocket]

        # Notify others (run as background task since we're not async)
        return {
            'workflow_id': workflow_id,
            'user_id': user_id,
            'locks_released': locks_to_release
        }

    async def broadcast(
        self,
        workflow_id: str,
        message: Dict,
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast message to all connections in a workflow"""
        if workflow_id not in self.active_connections:
            return

        # Remove dead connections
        dead_connections = set()

        for connection in self.active_connections[workflow_id]:
            if connection == exclude:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        # Cleanup dead connections
        for dead in dead_connections:
            self.disconnect(dead)

    async def handle_message(self, websocket: WebSocket, message: Dict):
        """
        Handle incoming WebSocket messages

        Message types:
        - cursor_move: Update cursor position
        - node_lock: Lock a node for editing
        - node_unlock: Release node lock
        - workflow_update: Broadcast workflow change
        - heartbeat: Keep connection alive
        """
        if websocket not in self.connection_metadata:
            return

        metadata = self.connection_metadata[websocket]
        workflow_id = metadata['workflow_id']
        user_id = metadata['user_id']

        message_type = message.get('type')

        if message_type == 'cursor_move':
            # Update cursor position
            cursor_data = message.get('data', {})
            self.cursor_positions[workflow_id][user_id] = {
                'x': cursor_data.get('x', 0),
                'y': cursor_data.get('y', 0),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Broadcast to others
            await self.broadcast(
                workflow_id,
                {
                    'type': 'cursor_update',
                    'user_id': user_id,
                    'user_name': metadata['user_name'],
                    'user_color': metadata['user_color'],
                    'position': self.cursor_positions[workflow_id][user_id]
                },
                exclude=websocket
            )

        elif message_type == 'node_lock':
            # Lock a node for editing
            node_id = message.get('node_id')

            if not node_id:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'node_id required for node_lock'
                })
                return

            # Check if already locked
            if node_id in self.node_locks.get(workflow_id, {}):
                locked_by = self.node_locks[workflow_id][node_id]
                if locked_by != user_id:
                    # Already locked by someone else
                    await websocket.send_json({
                        'type': 'lock_failed',
                        'node_id': node_id,
                        'locked_by': locked_by,
                        'message': f'Node is being edited by {self.active_users[workflow_id].get(locked_by, {}).get("user_name", "another user")}'
                    })
                    return

            # Lock the node
            self.node_locks[workflow_id][node_id] = user_id

            # Confirm to requester
            await websocket.send_json({
                'type': 'lock_acquired',
                'node_id': node_id
            })

            # Notify others
            await self.broadcast(
                workflow_id,
                {
                    'type': 'node_locked',
                    'node_id': node_id,
                    'user_id': user_id,
                    'user_name': metadata['user_name']
                },
                exclude=websocket
            )

        elif message_type == 'node_unlock':
            # Unlock a node
            node_id = message.get('node_id')

            if not node_id:
                return

            # Check if locked by this user
            if node_id in self.node_locks.get(workflow_id, {}):
                if self.node_locks[workflow_id][node_id] == user_id:
                    del self.node_locks[workflow_id][node_id]

                    # Notify everyone
                    await self.broadcast(
                        workflow_id,
                        {
                            'type': 'node_unlocked',
                            'node_id': node_id,
                            'user_id': user_id
                        }
                    )

        elif message_type == 'workflow_update':
            # Broadcast workflow change
            update_data = message.get('data', {})

            await self.broadcast(
                workflow_id,
                {
                    'type': 'workflow_changed',
                    'user_id': user_id,
                    'user_name': metadata['user_name'],
                    'data': update_data
                },
                exclude=websocket
            )

        elif message_type == 'heartbeat':
            # Update last seen
            if workflow_id in self.active_users and user_id in self.active_users[workflow_id]:
                self.active_users[workflow_id][user_id]['last_seen'] = datetime.utcnow().isoformat()

            # Send pong
            await websocket.send_json({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            })

        elif message_type == 'typing_indicator':
            # Broadcast typing indicator
            node_id = message.get('node_id')
            is_typing = message.get('is_typing', False)

            await self.broadcast(
                workflow_id,
                {
                    'type': 'user_typing',
                    'user_id': user_id,
                    'user_name': metadata['user_name'],
                    'node_id': node_id,
                    'is_typing': is_typing
                },
                exclude=websocket
            )

    def get_active_users(self, workflow_id: str) -> List[Dict]:
        """Get list of active users in a workflow"""
        return list(self.active_users.get(workflow_id, {}).values())

    def get_node_locks(self, workflow_id: str) -> Dict[str, str]:
        """Get all node locks for a workflow"""
        return self.node_locks.get(workflow_id, {}).copy()

# Singleton instance
collaboration_manager = CollaborationManager()
