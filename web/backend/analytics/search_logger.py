"""
Enhancement 6: Search Analytics Logging System
Logs all search queries and user interactions for analytics
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path("web/backend/database/search_logs.db")


class SearchLogger:
    """
    Logs search queries and interactions for analytics dashboard

    Tracks:
    - Search queries with results count
    - Clicked results
    - Zero-result queries (documentation gaps)
    - Command usage
    """

    def __init__(self):
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with all required tables"""
        try:
            # Create database directory
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            # Search queries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    intent TEXT,
                    results_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    session_id TEXT
                )
            """)

            # Clicked results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS result_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id INTEGER,
                    result_id TEXT,
                    result_title TEXT,
                    result_type TEXT,
                    position INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_id) REFERENCES search_queries (id)
                )
            """)

            # Zero-result queries (for documentation gaps)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zero_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    intent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)

            # Command usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT NOT NULL,
                    command_title TEXT,
                    action TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context TEXT
                )
            """)

            # Create indices for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_timestamp
                ON search_queries(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clicks_query_id
                ON result_clicks(query_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_zero_results_query
                ON zero_results(query)
            """)

            conn.commit()
            conn.close()

            logger.info(f"Analytics database initialized at {DB_PATH}")

        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            raise

    def log_search(
        self,
        query: str,
        intent: str,
        results_count: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """
        Log a search query

        Args:
            query: The search query string
            intent: Classified intent (HOW_TO, WHAT_IS, etc.)
            results_count: Number of results returned
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            query_id for linking clicks
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO search_queries (query, intent, results_count, user_id, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (query, intent, results_count, user_id, session_id))

            query_id = cursor.lastrowid

            # Log zero results for tracking documentation gaps
            if results_count == 0:
                cursor.execute("""
                    INSERT INTO zero_results (query, intent)
                    VALUES (?, ?)
                """, (query, intent))

            conn.commit()
            conn.close()

            return query_id

        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            return -1

    def log_click(
        self,
        query_id: int,
        result_id: str,
        result_title: str,
        result_type: str,
        position: int
    ):
        """
        Log a clicked search result

        Args:
            query_id: ID from log_search()
            result_id: Unique identifier of clicked result
            result_title: Title/name of clicked result
            result_type: Type (command, doc, example)
            position: Position in search results (1-based)
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO result_clicks
                (query_id, result_id, result_title, result_type, position)
                VALUES (?, ?, ?, ?, ?)
            """, (query_id, result_id, result_title, result_type, position))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to log click: {e}")

    def log_command_usage(
        self,
        command_id: str,
        command_title: str,
        action: str,
        context: Optional[str] = None
    ):
        """
        Log command usage

        Args:
            command_id: Unique command identifier
            command_title: Human-readable command name
            action: Action taken (viewed, added_to_workflow, executed)
            context: Optional context (workflow_builder, chat, etc.)
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO command_usage (command_id, command_title, action, context)
                VALUES (?, ?, ?, ?)
            """, (command_id, command_title, action, context))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")


# Singleton instance
search_logger = SearchLogger()
