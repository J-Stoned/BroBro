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
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA busy_timeout = 30000")  # 30 second timeout

            # Migration tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

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

            # Run pending migrations
            self._run_migrations(conn)

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def _run_migrations(self, conn):
        """Run all pending database migrations"""
        cursor = conn.cursor()

        try:
            # Migration V1: Add pinned column to conversations
            self._migrate_v1_add_pinned(cursor, conn)

            # Migration V2: Add backend_type column to conversations
            self._migrate_v2_add_backend_type(cursor, conn)

            # Migration V3: Add FTS5 full-text search
            self._migrate_v3_add_fts5(cursor, conn)

        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            conn.rollback()
            raise

    def _is_migration_applied(self, cursor, version: int, name: str) -> bool:
        """Check if a migration has already been applied"""
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM schema_migrations
                WHERE version = ?
            """, (version,))
            return cursor.fetchone()[0] > 0
        except Exception:
            # Table might not exist yet for first migration
            return False

    def _mark_migration_applied(self, cursor, version: int, name: str):
        """Mark a migration as applied"""
        cursor.execute("""
            INSERT OR IGNORE INTO schema_migrations (version, name)
            VALUES (?, ?)
        """, (version, name))

    def _column_exists(self, cursor, table: str, column: str) -> bool:
        """Check if a column exists in a table (using PRAGMA table_info)"""
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            rows = cursor.fetchall()
            # PRAGMA table_info returns tuples: (cid, name, type, notnull, dflt_value, pk)
            # Column name is at index 1
            for row in rows:
                if row[1] == column:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking column existence: {e}")
            return False

    def _migrate_v1_add_pinned(self, cursor, conn):
        """Migration V1: Add pinned column to conversations table"""
        version = 1
        name = "add_pinned_column"

        if self._is_migration_applied(cursor, version, name):
            logger.info(f"Migration V{version} ({name}) already applied, skipping")
            return

        try:
            if not self._column_exists(cursor, "conversations", "pinned"):
                logger.info(f"Running migration V{version}: {name}")
                cursor.execute("""
                    ALTER TABLE conversations
                    ADD COLUMN pinned BOOLEAN DEFAULT FALSE
                """)
                self._mark_migration_applied(cursor, version, name)
                conn.commit()
                logger.info(f"Migration V{version} ({name}) completed successfully")
            else:
                logger.info(f"Migration V{version} ({name}) skipped - column already exists")
                self._mark_migration_applied(cursor, version, name)
                conn.commit()

        except Exception as e:
            logger.error(f"Error applying migration V{version} ({name}): {e}")
            conn.rollback()
            raise

    def _migrate_v2_add_backend_type(self, cursor, conn):
        """Migration V2: Add backend_type column to conversations table"""
        version = 2
        name = "add_backend_type_column"

        if self._is_migration_applied(cursor, version, name):
            logger.info(f"Migration V{version} ({name}) already applied, skipping")
            return

        try:
            if not self._column_exists(cursor, "conversations", "backend_type"):
                logger.info(f"Running migration V{version}: {name}")
                cursor.execute("""
                    ALTER TABLE conversations
                    ADD COLUMN backend_type TEXT DEFAULT 'claude'
                """)
                self._mark_migration_applied(cursor, version, name)
                conn.commit()
                logger.info(f"Migration V{version} ({name}) completed successfully")
            else:
                logger.info(f"Migration V{version} ({name}) skipped - column already exists")
                self._mark_migration_applied(cursor, version, name)
                conn.commit()

        except Exception as e:
            logger.error(f"Error applying migration V{version} ({name}): {e}")
            conn.rollback()
            raise

    def _migrate_v3_add_fts5(self, cursor, conn):
        """Migration V3: Add FTS5 full-text search for messages"""
        version = 3
        name = "add_fts5_search"

        if self._is_migration_applied(cursor, version, name):
            logger.info(f"Migration V{version} ({name}) already applied, skipping")
            return

        try:
            logger.info(f"Running migration V{version}: {name}")

            # Create FTS5 virtual table for messages
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                    content,
                    tokenize='unicode61 remove_diacritics 2',
                    content=messages,
                    content_rowid=id
                )
            """)

            # Backfill existing messages into FTS5 table
            cursor.execute("""
                INSERT INTO messages_fts(rowid, content)
                SELECT id, content FROM messages WHERE content IS NOT NULL
            """)

            # Create triggers to keep FTS5 index in sync
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
                  INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
                  DELETE FROM messages_fts WHERE rowid = old.id;
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
                  DELETE FROM messages_fts WHERE rowid = old.id;
                  INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
                END
            """)

            self._mark_migration_applied(cursor, version, name)
            conn.commit()
            logger.info(f"Migration V{version} ({name}) completed successfully")

        except Exception as e:
            logger.error(f"Error applying migration V{version} ({name}): {e}")
            conn.rollback()
            raise

    def _sanitize_fts5_query(self, query: str) -> str:
        """
        Sanitize user input for FTS5 MATCH queries.

        FTS5 has special operators: * " ( ) : ^
        This function removes them and wraps in quotes for literal matching.
        """
        if not query or not isinstance(query, str):
            return ""

        # Remove FTS5 special characters
        special_chars = ['*', '"', '(', ')', ':', '^']
        sanitized = query
        for char in special_chars:
            sanitized = sanitized.replace(char, '')

        # Trim whitespace
        sanitized = sanitized.strip()

        # Wrap in quotes for phrase matching (literal search)
        if sanitized:
            return f'"{sanitized}"'
        return ""

    def search_conversations(
        self,
        session_id: str,
        query: str,
        backend_type: Optional[str] = None,
        archived: bool = False,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search conversations by message content using FTS5.

        Args:
            session_id: Session identifier
            query: Search query string
            backend_type: Filter by backend type (optional)
            archived: Include archived conversations (optional)
            limit: Maximum results (default: 20)

        Returns:
            Dict with search results and metadata
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Sanitize the query for FTS5
            fts_query = self._sanitize_fts5_query(query)

            if not fts_query:
                return {
                    'success': True,
                    'conversations': [],
                    'total': 0,
                    'limit': limit
                }

            # Search using FTS5, get unique conversations
            search_query = """
                SELECT DISTINCT c.id, c.session_id, c.title, c.created_at, c.updated_at,
                       c.archived, COALESCE(c.pinned, FALSE) as pinned,
                       COALESCE(c.backend_type, 'claude') as backend_type,
                       snippet(messages_fts, 0, '<mark>', '</mark>', '...', 15) as excerpt
                FROM messages_fts
                JOIN messages m ON messages_fts.rowid = m.id
                JOIN conversations c ON m.conversation_id = c.id
                WHERE messages_fts.content MATCH ?
                  AND c.session_id = ?
            """
            params = [fts_query, session_id]

            if not archived:
                search_query += " AND c.archived = FALSE"

            if backend_type:
                search_query += " AND c.backend_type = ?"
                params.append(backend_type)

            # Sort by pinned DESC, then by updated_at DESC
            search_query += " GROUP BY c.id ORDER BY c.pinned DESC, c.updated_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(search_query, params)
            rows = cursor.fetchall()

            conversations = []
            for row in rows:
                conversations.append({
                    'id': row[0],
                    'session_id': row[1],
                    'title': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'archived': bool(row[5]),
                    'pinned': bool(row[6]),
                    'backend_type': row[7],
                    'excerpt': row[8]
                })

            return {
                'success': True,
                'conversations': conversations,
                'total': len(conversations),
                'limit': limit,
                'query': query
            }

        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return {'success': False, 'error': str(e)}

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
        archived: bool = False,
        backend_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all conversations for a session

        Args:
            session_id: Session identifier
            limit: Maximum results (pagination)
            offset: Results offset (pagination)
            archived: Include archived conversations
            backend_type: Filter by backend type ('claude' or 'gemini', None for all)

        Returns:
            Dict with list of conversations
        """
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Get conversations (sorted by pinned DESC, then updated_at DESC)
            query = """
                SELECT id, session_id, title, created_at, updated_at, archived,
                       COALESCE(pinned, FALSE) as pinned,
                       COALESCE(backend_type, 'claude') as backend_type
                FROM conversations
                WHERE session_id = ?
            """
            params = [session_id]

            if not archived:
                query += " AND archived = FALSE"

            if backend_type:
                query += " AND backend_type = ?"
                params.append(backend_type)

            # Sort by pinned DESC (pinned first), then by updated_at DESC
            query += " ORDER BY pinned DESC, updated_at DESC LIMIT ? OFFSET ?"
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

            if backend_type:
                count_query += " AND backend_type = ?"
                count_params.append(backend_type)

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
                    'archived': bool(row[5]),
                    'pinned': bool(row[6]),
                    'backend_type': row[7]
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
                SELECT id, session_id, title, created_at, updated_at, archived,
                       COALESCE(pinned, FALSE) as pinned,
                       COALESCE(backend_type, 'claude') as backend_type
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
                'archived': bool(conv_row[5]),
                'pinned': bool(conv_row[6]),
                'backend_type': conv_row[7]
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
        archived: Optional[bool] = None,
        pinned: Optional[bool] = None,
        backend_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update conversation metadata

        Args:
            conversation_id: Conversation ID
            title: New title (optional)
            archived: Archive status (optional)
            pinned: Pin status (optional)
            backend_type: Backend type (optional)

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
                # Auto-unpin when archiving
                if archived:
                    updates.append('pinned = ?')
                    params.append(0)

            if backend_type is not None:
                updates.append('backend_type = ?')
                params.append(backend_type)

            if pinned is not None:
                updates.append('pinned = ?')
                params.append(int(pinned))

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

    def set_conversation_pinned(
        self,
        conversation_id: str,
        pinned: bool
    ) -> Dict[str, Any]:
        """
        Set pin status of a conversation

        Args:
            conversation_id: Conversation ID
            pinned: Pin status (True to pin, False to unpin)

        Returns:
            Dict with updated conversation
        """
        return self.update_conversation(conversation_id, pinned=pinned)

    def set_conversation_backend(
        self,
        conversation_id: str,
        backend_type: str
    ) -> Dict[str, Any]:
        """
        Set the backend type for a conversation

        Args:
            conversation_id: Conversation ID
            backend_type: Backend type ('claude' or 'gemini')

        Returns:
            Dict with updated conversation
        """
        if backend_type not in ('claude', 'gemini'):
            return {'success': False, 'error': "Backend type must be 'claude' or 'gemini'"}

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE conversations
                SET backend_type = ?, updated_at = ?
                WHERE id = ?
            """, (backend_type, now, conversation_id))

            conn.commit()

            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Conversation not found'}

            # Return updated conversation
            return self.get_conversation(conversation_id)

        except Exception as e:
            logger.error(f"Error setting conversation backend: {e}")
            conn.rollback()
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
