"""
Unified Search Engine - Main Module
Built with BMAD-METHOD for Epic US: Unified Search

Queries all collections, detects intent, scores relevance,
and returns organized results ready for display.

Extensible architecture supports adding new collections easily.
"""

import asyncio
import time
from typing import List, Dict, Optional

from .intent_detector import QueryIntentDetector
from .relevance_scorer import RelevanceScorer
from .result_grouper import ResultGrouper


class UnifiedSearch:
    """
    Unified search system that queries multiple collections,
    ranks results intelligently, and groups for display
    """

    # Collections currently active and indexed
    ACTIVE_COLLECTIONS = [
        'ghl-docs',             # 960 documentation items
        'ghl-knowledge-base'    # 281 GHL slash commands (NOW POPULATED!)
    ]

    # Collections ready to activate when data exists
    READY_COLLECTIONS = [
        # ghl-knowledge-base moved to ACTIVE (populated with 281 commands)
    ]

    # Future collections (add when data exists)
    FUTURE_COLLECTIONS = [
        'workflows',      # User-created workflows
        'conversations',  # Chat history
        'templates',      # Workflow templates
        'setup',          # Setup guides
        'api-endpoints'   # API documentation
    ]

    def __init__(self, chroma_client):
        """
        Initialize unified search

        Args:
            chroma_client: ChromaDB client instance
        """
        self.chroma_client = chroma_client
        self.intent_detector = QueryIntentDetector()
        self.scorer = RelevanceScorer()
        self.grouper = ResultGrouper()

    async def search(
        self,
        query: str,
        limit: int = 20,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Execute unified search across all collections

        Args:
            query: Search query string
            limit: Max results to return (default 20)
            user_context: Optional user preferences/history

        Returns:
            {
                'query': str,
                'intent': str,
                'total_results': int,
                'results': {
                    'topAnswer': {...},
                    'commands': [...],
                    'documentation': [...]
                },
                'suggestions': [str],
                'search_time_ms': float
            }
        """
        start_time = time.time()

        # Validate query
        if not query or not query.strip():
            return self._empty_results(query)

        # 1. Detect query intent
        intent = self.intent_detector.detect_intent(query)
        collection_pref = self.intent_detector.get_collection_preference(intent)

        # 2. Search all collections in parallel
        all_results = await self._parallel_search(query)

        if not all_results:
            return self._empty_results(query, intent)

        # 3. Score all results
        scored_results = self._score_results(
            all_results,
            query,
            intent,
            collection_pref,
            user_context
        )

        # 4. Normalize scores for display (0-100 range)
        scored_results = self.scorer.normalize_scores(scored_results)

        # 5. Sort by relevance (highest first)
        scored_results.sort(
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )

        # Take top N results
        top_results = scored_results[:limit]

        # 6. Group by collection for organized display
        grouped_results = self.grouper.group_by_collection(top_results)

        # 7. Format for display
        formatted_results = self._format_results(grouped_results)

        # 8. Generate related suggestions
        suggestions = self._generate_suggestions(query, intent, top_results)

        search_time = (time.time() - start_time) * 1000  # Convert to ms

        return {
            'query': query,
            'intent': intent,
            'total_results': len(scored_results),
            'results': formatted_results,
            'suggestions': suggestions,
            'search_time_ms': round(search_time, 2)
        }

    async def _parallel_search(self, query: str) -> List[Dict]:
        """
        Search all active collections in parallel

        Args:
            query: Search query

        Returns:
            List of all search results from all collections
        """

        async def search_collection(collection_name: str):
            """Search a single collection"""
            try:
                collection = self.chroma_client.get_collection(collection_name)

                # Skip empty collections
                if collection.count() == 0:
                    return []

                results = collection.query(
                    query_texts=[query],
                    n_results=10  # Get top 10 from each collection
                )

                # Format results
                formatted = []
                if results and results.get('ids'):
                    for i in range(len(results['ids'][0])):
                        formatted.append({
                            'id': results['ids'][0][i],
                            'document': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                            'distance': results['distances'][0][i] if results.get('distances') else 0,
                            'collection': collection_name
                        })

                return formatted

            except Exception as e:
                print(f"[WARN] Error searching {collection_name}: {e}")
                return []

        # Search all active collections + ready collections
        collections_to_search = self.ACTIVE_COLLECTIONS + self.READY_COLLECTIONS

        tasks = [search_collection(col) for col in collections_to_search]
        results_by_collection = await asyncio.gather(*tasks)

        # Flatten results
        all_results = []
        for results in results_by_collection:
            all_results.extend(results)

        return all_results

    def _score_results(
        self,
        results: List[Dict],
        query: str,
        intent: str,
        collection_pref: Dict,
        user_context: Optional[Dict]
    ) -> List[Dict]:
        """Score all results for relevance"""
        scored = []

        for result in results:
            score = self.scorer.calculate_score(
                result,
                query,
                intent,
                collection_pref,
                user_context
            )

            result['relevance_score'] = score
            scored.append(result)

        return scored

    def _format_results(self, grouped_results: Dict) -> Dict:
        """Format results for display"""
        formatted = {}

        if grouped_results.get('topAnswer'):
            formatted['topAnswer'] = self.grouper.format_result_for_display(
                grouped_results['topAnswer']
            )

        if grouped_results.get('commands'):
            formatted['commands'] = [
                self.grouper.format_result_for_display(r)
                for r in grouped_results['commands']
            ]

        if grouped_results.get('documentation'):
            formatted['documentation'] = [
                self.grouper.format_result_for_display(r)
                for r in grouped_results['documentation']
            ]

        formatted['total_by_type'] = grouped_results.get('total_by_type', {})

        return formatted

    def _generate_suggestions(
        self,
        query: str,
        intent: str,
        results: List[Dict]
    ) -> List[str]:
        """Generate related search suggestions"""
        suggestions = []
        query_lower = query.lower()

        # Intent-based suggestions
        if 'how to' not in query_lower and intent != 'HOW_TO':
            suggestions.append(f"how to {query}")

        if 'example' not in query_lower and intent != 'EXAMPLE':
            suggestions.append(f"{query} examples")

        if 'what is' not in query_lower and intent != 'WHAT_IS':
            suggestions.append(f"what is {query}")

        # Category-based suggestions from top results
        if results:
            categories = set()
            for result in results[:5]:  # Look at top 5 results
                category = result.get('metadata', {}).get('category')
                if category and category != 'General':
                    categories.add(category)

            for category in list(categories)[:2]:  # Max 2 category suggestions
                suggestions.append(f"{query} {category.lower()}")

        return suggestions[:5]  # Max 5 suggestions

    def _empty_results(self, query: str, intent: str = 'GENERAL') -> Dict:
        """Return empty results structure"""
        return {
            'query': query,
            'intent': intent,
            'total_results': 0,
            'results': {
                'topAnswer': None,
                'commands': [],
                'documentation': [],
                'total_by_type': {'commands': 0, 'documentation': 0}
            },
            'suggestions': [
                "Try simpler terms",
                "Check your spelling",
                "Use more general keywords"
            ],
            'search_time_ms': 0
        }
