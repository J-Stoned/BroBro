"""
Multi-Factor Relevance Scoring for Search Results
Built with BMAD-METHOD for Epic US: Unified Search

Scores results based on:
1. Semantic similarity (from ChromaDB)
2. Intent-based collection boosting
3. Query term exact matching
4. Content completeness
5. User context (favorites, recent)
6. Intent-specific boosts
"""

from typing import Dict, Optional


class RelevanceScorer:
    """Calculate relevance scores for search results"""

    def calculate_score(
        self,
        result: Dict,
        query: str,
        intent: str,
        collection_preference: Dict,
        user_context: Optional[Dict] = None
    ) -> float:
        """
        Multi-factor relevance scoring

        Factors:
        1. Semantic similarity (from ChromaDB distance)
        2. Intent-based collection boosting
        3. Query term exact matching
        4. Content completeness (has examples, code snippets)
        5. User context (recently used, favorites)
        6. Intent-specific boosts

        Args:
            result: Search result dict
            query: User's search query
            intent: Detected intent type
            collection_preference: Intent-based collection preferences
            user_context: Optional user history/preferences

        Returns:
            Score 0-200+ (higher = more relevant)
        """
        score = 0.0

        # 1. Base semantic similarity (0-100)
        # ChromaDB returns distance (lower = more similar)
        # Convert to similarity score (higher = more similar)
        distance = result.get('distance', 1.0)
        similarity_score = max(0, (1 - distance) * 100)
        score += similarity_score

        # 2. Intent-based collection boosting
        result_collection = result.get('collection', '')
        primary_collection = collection_preference.get('primary', '')
        boost_amount = collection_preference.get('boost', 0)

        if result_collection == primary_collection:
            score += boost_amount

        # 3. Query term exact matching
        query_lower = query.lower()
        metadata = result.get('metadata', {})

        title = metadata.get('title', '').lower()
        content = result.get('document', '').lower()

        # Exact title match bonus
        if query_lower in title:
            score += 25

        # Partial title word matching
        query_words = set(query_lower.split())
        title_words = set(title.split())
        matching_words = query_words & title_words

        if query_words:
            match_ratio = len(matching_words) / len(query_words)
            score += match_ratio * 15

        # Content match
        if query_lower in content:
            score += 10

        # 4. Completeness boost
        if metadata.get('has_examples'):
            score += 10
        if metadata.get('has_code_snippets'):
            score += 10
        if metadata.get('difficulty') == 'beginner':
            score += 5  # Boost beginner-friendly content

        # 5. User context boost
        if user_context:
            result_id = result.get('id')

            if result_id in user_context.get('recently_used', []):
                score += 15

            if result_id in user_context.get('favorites', []):
                score += 25

        # 6. Intent-specific boosts
        if intent == 'HOW_TO' and metadata.get('has_examples'):
            score += 15

        if intent == 'TROUBLESHOOT':
            # Boost troubleshooting-related content
            troubleshoot_keywords = ['error', 'issue', 'problem', 'fix', 'troubleshoot']
            content_has_troubleshoot = any(kw in content for kw in troubleshoot_keywords)
            if content_has_troubleshoot:
                score += 20

        if intent == 'SETUP':
            # Boost setup/configuration content
            setup_keywords = ['setup', 'configure', 'install', 'initialize']
            content_has_setup = any(kw in content for kw in setup_keywords)
            if content_has_setup:
                score += 15

        return score

    def normalize_scores(self, results: list) -> list:
        """
        Normalize scores to 0-100 range for display

        Args:
            results: List of search results with relevance_score

        Returns:
            Same list with added relevance_score_normalized (0-100)
        """
        if not results:
            return results

        scores = [r.get('relevance_score', 0) for r in results]
        max_score = max(scores) if scores else 1

        if max_score == 0:
            max_score = 1  # Avoid division by zero

        for result in results:
            original = result.get('relevance_score', 0)
            result['relevance_score_normalized'] = int((original / max_score) * 100)

        return results
