"""
Enhancement 6: Search Analytics Query Functions
Provides analytics data for dashboard visualization
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path("web/backend/database/search_logs.db")


class SearchAnalytics:
    """
    Query search analytics data for dashboard display
    """

    def get_overview_stats(self, days: int = 30) -> Dict:
        """
        Get overview statistics for dashboard

        Returns:
            Dict with total_searches, click_through_rate, zero_results, etc.
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            # Total searches
            cursor.execute("""
                SELECT COUNT(*) FROM search_queries
                WHERE timestamp >= ?
            """, (since_date,))
            total_searches = cursor.fetchone()[0]

            # Zero-result searches
            cursor.execute("""
                SELECT COUNT(*) FROM zero_results
                WHERE timestamp >= ?
            """, (since_date,))
            zero_results = cursor.fetchone()[0]

            # Total clicks
            cursor.execute("""
                SELECT COUNT(*) FROM result_clicks
                WHERE timestamp >= ?
            """, (since_date,))
            total_clicks = cursor.fetchone()[0]

            conn.close()

            # Calculate rates
            ctr = (total_clicks / total_searches * 100) if total_searches > 0 else 0
            zero_rate = (zero_results / total_searches * 100) if total_searches > 0 else 0

            return {
                'total_searches': total_searches,
                'total_clicks': total_clicks,
                'zero_results': zero_results,
                'click_through_rate': round(ctr, 1),
                'zero_result_rate': round(zero_rate, 1),
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            return {
                'total_searches': 0,
                'total_clicks': 0,
                'zero_results': 0,
                'click_through_rate': 0,
                'zero_result_rate': 0,
                'period_days': days
            }

    def get_popular_searches(self, limit: int = 20, days: int = 30) -> List[Dict]:
        """Get most popular search queries"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT
                    query,
                    COUNT(*) as search_count,
                    AVG(results_count) as avg_results
                FROM search_queries
                WHERE timestamp >= ?
                GROUP BY query
                ORDER BY search_count DESC
                LIMIT ?
            """, (since_date, limit))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'query': row[0],
                    'search_count': row[1],
                    'avg_results': round(row[2], 1) if row[2] else 0
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting popular searches: {e}")
            return []

    def get_popular_commands(self, limit: int = 20, days: int = 30) -> List[Dict]:
        """Get most clicked commands"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT
                    result_id,
                    result_title,
                    result_type,
                    COUNT(*) as click_count,
                    AVG(position) as avg_position
                FROM result_clicks
                WHERE timestamp >= ?
                GROUP BY result_id
                ORDER BY click_count DESC
                LIMIT ?
            """, (since_date, limit))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'command_id': row[0],
                    'title': row[1],
                    'type': row[2],
                    'click_count': row[3],
                    'avg_position': round(row[4], 1) if row[4] else 0
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting popular commands: {e}")
            return []

    def get_zero_result_queries(self, limit: int = 50) -> List[Dict]:
        """
        Get queries that returned no results (documentation gaps)

        These indicate areas where documentation should be added
        """
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    query,
                    COUNT(*) as occurrence_count,
                    MAX(timestamp) as last_searched
                FROM zero_results
                WHERE resolved = FALSE
                GROUP BY query
                ORDER BY occurrence_count DESC
                LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'query': row[0],
                    'occurrence_count': row[1],
                    'last_searched': row[2]
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting zero result queries: {e}")
            return []

    def get_search_trends(self, days: int = 30) -> Dict:
        """Get daily search trends for charting"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT
                    DATE(timestamp) as date,
                    COUNT(*) as search_count,
                    SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) as zero_results
                FROM search_queries
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (since_date,))

            results = cursor.fetchall()
            conn.close()

            return {
                'dates': [row[0] for row in results],
                'search_counts': [row[1] for row in results],
                'zero_results': [row[2] for row in results]
            }

        except Exception as e:
            logger.error(f"Error getting search trends: {e}")
            return {
                'dates': [],
                'search_counts': [],
                'zero_results': []
            }

    def get_intent_distribution(self, days: int = 30) -> Dict:
        """Get distribution of search intents"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT
                    intent,
                    COUNT(*) as count
                FROM search_queries
                WHERE timestamp >= ? AND intent IS NOT NULL
                GROUP BY intent
                ORDER BY count DESC
            """, (since_date,))

            results = cursor.fetchall()
            conn.close()

            total = sum(row[1] for row in results)

            return {
                'intents': [
                    {
                        'intent': row[0],
                        'count': row[1],
                        'percentage': round(row[1] / total * 100, 1) if total > 0 else 0
                    }
                    for row in results
                ]
            }

        except Exception as e:
            logger.error(f"Error getting intent distribution: {e}")
            return {'intents': []}

    def get_command_usage_stats(self, days: int = 30) -> Dict:
        """Get command usage statistics"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            since_date = datetime.now() - timedelta(days=days)

            # Most used commands
            cursor.execute("""
                SELECT
                    command_title,
                    COUNT(*) as usage_count,
                    action
                FROM command_usage
                WHERE timestamp >= ?
                GROUP BY command_title, action
                ORDER BY usage_count DESC
                LIMIT 20
            """, (since_date,))

            results = cursor.fetchall()
            conn.close()

            return {
                'top_commands': [
                    {
                        'title': row[0],
                        'usage_count': row[1],
                        'action': row[2]
                    }
                    for row in results
                ]
            }

        except Exception as e:
            logger.error(f"Error getting command usage stats: {e}")
            return {'top_commands': []}


# Singleton instance
search_analytics = SearchAnalytics()
