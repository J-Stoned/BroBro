"""
BroBro Unified Search System
Built with BMAD-METHOD for Epic US: Unified Search

Provides intelligent multi-collection search with:
- Intent detection (7 types)
- Relevance scoring (6 factors)
- Result grouping and ranking
- Extensible architecture for future collections
"""

from .unified_search import UnifiedSearch
from .intent_detector import QueryIntentDetector
from .relevance_scorer import RelevanceScorer
from .result_grouper import ResultGrouper

__all__ = [
    'UnifiedSearch',
    'QueryIntentDetector',
    'RelevanceScorer',
    'ResultGrouper'
]
