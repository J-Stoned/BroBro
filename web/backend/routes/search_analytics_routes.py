"""
Enhancement 6: Search Analytics API Routes
Provides search analytics endpoints for dashboard
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from analytics.search_analytics import search_analytics
    from analytics.search_logger import search_logger
except ImportError:
    search_analytics = None
    search_logger = None

router = APIRouter()
logger = logging.getLogger(__name__)


class ClickLogRequest(BaseModel):
    query_id: int
    result_id: str
    result_title: str
    result_type: str
    position: int


@router.get("/api/search-analytics/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365)
):
    """Get overview analytics for search dashboard"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        stats = search_analytics.get_overview_stats(days)
        popular_searches = search_analytics.get_popular_searches(limit=10, days=days)
        popular_commands = search_analytics.get_popular_commands(limit=10, days=days)

        return {
            "success": True,
            "data": {
                "stats": stats,
                "popular_searches": popular_searches,
                "popular_commands": popular_commands
            }
        }
    except Exception as e:
        logger.error(f"Analytics overview error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/search-analytics/popular-searches")
async def get_popular_searches(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365)
):
    """Get most popular search queries"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        searches = search_analytics.get_popular_searches(limit, days)
        return {"success": True, "data": {"searches": searches, "total": len(searches)}}
    except Exception as e:
        logger.error(f"Popular searches error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/search-analytics/popular-commands")
async def get_popular_commands(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365)
):
    """Get most clicked commands"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        commands = search_analytics.get_popular_commands(limit, days)
        return {"success": True, "data": {"commands": commands, "total": len(commands)}}
    except Exception as e:
        logger.error(f"Popular commands error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/search-analytics/zero-results")
async def get_zero_result_queries(limit: int = Query(50, ge=1, le=100)):
    """Get queries that returned no results"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        queries = search_analytics.get_zero_result_queries(limit)
        return {"success": True, "data": {"queries": queries, "total": len(queries)}}
    except Exception as e:
        logger.error(f"Zero results error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/search-analytics/trends")
async def get_search_trends(days: int = Query(30, ge=7, le=365)):
    """Get daily search trends"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        trends = search_analytics.get_search_trends(days)
        return {"success": True, "data": trends}
    except Exception as e:
        logger.error(f"Trends error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/search-analytics/intents")
async def get_intent_distribution(days: int = Query(30, ge=1, le=365)):
    """Get search intent distribution"""
    try:
        if not search_analytics:
            return {"success": False, "error": "Analytics not available"}

        intents = search_analytics.get_intent_distribution(days)
        return {"success": True, "data": intents}
    except Exception as e:
        logger.error(f"Intents error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/api/search-analytics/log-click")
async def log_result_click(request: ClickLogRequest):
    """Log a clicked search result"""
    try:
        if not search_logger:
            return {"success": False, "error": "Logger not available"}

        search_logger.log_click(
            query_id=request.query_id,
            result_id=request.result_id,
            result_title=request.result_title,
            result_type=request.result_type,
            position=request.position
        )
        return {"success": True, "message": "Click logged"}
    except Exception as e:
        logger.error(f"Click logging error: {e}")
        return {"success": False, "error": str(e)}
