"""
Conversation Manager for Chat History

Manages SQLite database for storing conversations and messages.
Follows the pattern from analytics/search_logger.py
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path("web/backend/database/conversations.db")


class ConversationManager:
    """Manages conversation and message persistence using SQLite"""

    def __init__(self):
        """Initialize conversation manager and database"""
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        # Create directory if it doesn't exist
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    title TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    archived BOOLEAN DEFAULT FALSE
                )
            """)

            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
                )
            """)

            # Create indices for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id)
            """)

            conn.commit()
            logger.info(f"Database initialized at {DB_PATH}")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def create_conversation(
        self,
        session_id: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation

        Args:
            session_id: Session identifier
            title: Optional conversation title (auto-generated if not provided)

        Returns:
            Dict with conversation data and ID
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO conversations (id, session_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, session_id, title, now, now))

            conn.commit()

            return {
                'success': True,
                'id': conversation_id,
                'session_id': session_id,
                'title': title,
                'created_at': now,
                'updated_at': now,
                'archived': False
            }

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def get_conversations(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        archived: bool = False
    ) -> Dict[str, Any]:
        """
        Get all conversations for a session

        Args:
            session_id: Session identifier
            limit: Maximum results (pagination)
            offset: Results offset (pagination)
            archived: Include archived conversations

        Returns:
            Dict with list of conversations
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Get conversations
            query = """
                SELECT id, session_id, title, created_at, updated_at, archived
                FROM conversations
                WHERE session_id = ?
            """
            params = [session_id]

            if not archived:
                query += " AND archived = FALSE"

            query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Get total count
            count_query = """
                SELECT COUNT(*) FROM conversations
                WHERE session_id = ?
            """
            count_params = [session_id]

            if not archived:
                count_query += " AND archived = FALSE"

            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]

            conversations = []
            for row in rows:
                conversations.append({
                    'id': row[0],
                    'session_id': row[1],
                    'title': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'archived': bool(row[5])
                })

            return {
                'success': True,
                'conversations': conversations,
                'total': total,
                'limit': limit,
                'offset': offset
            }

        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a conversation with all its messages

        Args:
            conversation_id: Conversation ID

        Returns:
            Dict with conversation and messages
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Get conversation
            cursor.execute("""
                SELECT id, session_id, title, created_at, updated_at, archived
                FROM conversations
                WHERE id = ?
            """, (conversation_id,))

            conv_row = cursor.fetchone()
            if not conv_row:
                return {'success': False, 'error': 'Conversation not found'}

            conversation = {
                'id': conv_row[0],
                'session_id': conv_row[1],
                'title': conv_row[2],
                'created_at': conv_row[3],
                'updated_at': conv_row[4],
                'archived': bool(conv_row[5])
            }

            # Get messages
            cursor.execute("""
                SELECT id, role, content, timestamp, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))

            msg_rows = cursor.fetchall()
            messages = []

            for msg_row in msg_rows:
                metadata = {}
                if msg_row[4]:
                    try:
                        metadata = json.loads(msg_row[4])
                    except json.JSONDecodeError:
                        metadata = {}

                messages.append({
                    'id': msg_row[0],
                    'role': msg_row[1],
                    'content': msg_row[2],
                    'timestamp': msg_row[3],
                    'metadata': metadata
                })

            return {
                'success': True,
                'conversation': conversation,
                'messages': messages
            }

        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        archived: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update conversation metadata

        Args:
            conversation_id: Conversation ID
            title: New title (optional)
            archived: Archive status (optional)

        Returns:
            Dict with updated conversation
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            now = datetime.now().isoformat()

            # Build update query
            updates = ['updated_at = ?']
            params = [now]

            if title is not None:
                updates.append('title = ?')
                params.append(title)

            if archived is not None:
                updates.append('archived = ?')
                params.append(int(archived))

            params.append(conversation_id)

            query = f"""
                UPDATE conversations
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Conversation not found'}

            # Return updated conversation
            return self.get_conversation(conversation_id)

        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Delete a conversation and all its messages

        Args:
            conversation_id: Conversation ID

        Returns:
            Dict with success status
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Delete messages first (handled by CASCADE)
            cursor.execute("""
                DELETE FROM conversations
                WHERE id = ?
            """, (conversation_id,))

            conn.commit()

            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Conversation not found'}

            return {'success': True, 'message': 'Conversation deleted'}

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation

        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata (sources, timing, etc.)

        Returns:
            Dict with message data
        """
        if role not in ('user', 'assistant'):
            return {'success': False, 'error': "Role must be 'user' or 'assistant'"}

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            now = datetime.now().isoformat()
            metadata_str = json.dumps(metadata) if metadata else None

            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, role, content, now, metadata_str))

            # Update conversation updated_at
            cursor.execute("""
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
            """, (now, conversation_id))

            conn.commit()
            message_id = cursor.lastrowid

            return {
                'success': True,
                'id': message_id,
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'timestamp': now,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get messages from a conversation

        Args:
            conversation_id: Conversation ID
            limit: Maximum results (pagination)
            offset: Results offset (pagination)

        Returns:
            Dict with list of messages
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE conversation_id = ?
            """, (conversation_id,))
            total = cursor.fetchone()[0]

            # Get messages
            cursor.execute("""
                SELECT id, role, content, timestamp, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
                LIMIT ? OFFSET ?
            """, (conversation_id, limit, offset))

            rows = cursor.fetchall()
            messages = []

            for row in rows:
                metadata = {}
                if row[4]:
                    try:
                        metadata = json.loads(row[4])
                    except json.JSONDecodeError:
                        metadata = {}

                messages.append({
                    'id': row[0],
                    'role': row[1],
                    'content': row[2],
                    'timestamp': row[3],
                    'metadata': metadata
                })

            return {
                'success': True,
                'messages': messages,
                'total': total,
                'limit': limit,
                'offset': offset
            }

        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()


# Singleton instance
_manager_instance = None


def get_conversation_manager() -> ConversationManager:
    """Get or create the ConversationManager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ConversationManager()
    return _manager_instance
