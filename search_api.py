#!/usr/bin/env python3
"""
BroBro - Enhanced Multi-Collection Search API
Hybrid BM25 + Semantic search with query expansion and caching
"""

import time
import json
import os
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
from collections import OrderedDict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


@dataclass
class SearchResult:
    """Single search result with metadata"""
    content: str
    distance: float
    source: Literal['command', 'documentation', 'youtube']
    collection_name: str
    metadata: Dict
    relevance_score: float  # Normalized 0-1 semantic score
    bm25_score: float = 0.0  # BM25 keyword score
    hybrid_score: float = 0.0  # Combined final score


class LRUCache:
    """Simple LRU cache with max capacity"""

    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[any]:
        """Get value from cache, return None if not found"""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: any):
        """Put value in cache"""
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove oldest item
                self.cache.popitem(last=False)
        self.cache[key] = value

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'capacity': self.capacity,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.get_hit_rate()
        }


class QueryExpander:
    """Expands queries using synonym dictionary"""

    def __init__(self, synonyms_file: str = "config/synonyms.json"):
        """Load synonym dictionary"""
        self.synonyms = {}
        if os.path.exists(synonyms_file):
            try:
                with open(synonyms_file, 'r', encoding='utf-8') as f:
                    self.synonyms = json.load(f)
                print(f"  Query expander loaded {len(self.synonyms)} synonym mappings")
            except Exception as e:
                print(f"  WARNING: Could not load synonyms: {e}")

    def expand_query(self, query: str, max_expansions: int = 2) -> str:
        """
        Expand query with synonyms

        Args:
            query: Original query string
            max_expansions: Maximum number of synonym expansions per term

        Returns:
            Expanded query string
        """
        if not self.synonyms:
            return query

        terms = query.lower().split()
        expanded_terms = list(terms)  # Start with original terms

        for term in terms:
            if term in self.synonyms:
                # Add up to max_expansions synonyms
                synonyms = self.synonyms[term][:max_expansions]
                expanded_terms.extend(synonyms)

        return ' '.join(expanded_terms)


class MultiCollectionSearch:
    """
    Enhanced multi-collection search with hybrid BM25 + semantic search,
    query expansion, and LRU caching
    """

    def __init__(
        self,
        chroma_host: str = "localhost",
        chroma_port: int = 8001,
        enable_cache: bool = True,
        cache_size: int = 1000
    ):
        """Initialize enhanced search engine"""

        print("=" * 80)
        print("Initializing BroBro Enhanced Search Engine")
        print("=" * 80)

        # Initialize ChromaDB client
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize embedding model
        print(">> Loading embedding model...")
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Get collections
        self.commands_collection = None
        self.docs_collection = None
        self.youtube_collection = None
        self._init_collections()

        # Build BM25 indices
        print(">> Building BM25 indices for keyword search...")
        self.bm25_indices = {}
        self.documents_cache = {}  # Store documents for BM25
        self._build_bm25_indices()

        # Initialize query expander
        print(">> Initializing query expander...")
        self.query_expander = QueryExpander()

        # Initialize cache
        self.enable_cache = enable_cache
        self.cache = LRUCache(capacity=cache_size) if enable_cache else None

        print("=" * 80)
        print("Enhanced Search Engine Ready!")
        print(f"  Features: Hybrid BM25 + Semantic, Query Expansion, LRU Cache")
        print(f"  Collections: {sum(1 for c in [self.commands_collection, self.docs_collection, self.youtube_collection, self.business_collection] if c) + len(self.data_kb_collections)}")
        print(f"  BM25 Indices: {len(self.bm25_indices)}")
        print(f"  Caching: {'Enabled' if enable_cache else 'Disabled'}")
        print("=" * 80)
        print()

    def _init_collections(self):
        """Initialize all available collections"""
        # GHL collections
        try:
            self.commands_collection = self.client.get_collection(name="ghl-knowledge-base")
            print(f"  OK Connected to ghl-knowledge-base ({self.commands_collection.count()} items)")
        except Exception as e:
            print(f"  WARNING: Could not connect to ghl-knowledge-base: {e}")
            self.commands_collection = None

        try:
            self.docs_collection = self.client.get_collection(name="ghl-docs")
            print(f"  OK Connected to ghl-docs ({self.docs_collection.count()} items)")
        except Exception as e:
            print(f"  WARNING: Could not connect to ghl-docs: {e}")
            self.docs_collection = None

        try:
            self.youtube_collection = self.client.get_collection(name="ghl-youtube")
            print(f"  OK Connected to ghl-youtube ({self.youtube_collection.count()} items)")
        except Exception as e:
            print(f"  WARNING: Could not connect to ghl-youtube: {e}")
            self.youtube_collection = None

        # Data KB collections (books, business knowledge)
        self.business_collection = None
        try:
            self.business_collection = self.client.get_collection(name="ghl-business")
            print(f"  OK Connected to ghl-business ({self.business_collection.count()} items)")
        except Exception as e:
            print(f"  WARNING: Could not connect to ghl-business: {e}")
            self.business_collection = None
        
        # Additional data KB collections if they exist
        self.data_kb_collections = {}
        for col_name in ["ghl-snapshots", "ghl-tutorials", "ghl-best-practices"]:
            try:
                col = self.client.get_collection(name=col_name)
                self.data_kb_collections[col_name] = col
                print(f"  OK Connected to {col_name} ({col.count()} items)")
            except Exception as e:
                print(f"  WARNING: Could not connect to {col_name}: {e}")

    def _build_bm25_indices(self):
        """Build BM25 indices for keyword search"""
        collections = {
            'ghl-knowledge-base': self.commands_collection,
            'ghl-docs': self.docs_collection,
            'ghl-youtube': self.youtube_collection,
            'ghl-business': self.business_collection
        }
        
        # Add data KB collections
        collections.update(self.data_kb_collections)

        for name, collection in collections.items():
            if collection is None:
                continue

            try:
                # Get all documents from collection
                results = collection.get(include=['documents'])
                documents = results['documents']

                # Tokenize documents for BM25
                tokenized_docs = [doc.lower().split() for doc in documents]

                # Build BM25 index
                bm25 = BM25Okapi(tokenized_docs)

                self.bm25_indices[name] = bm25
                self.documents_cache[name] = documents

                print(f"    Built BM25 index for {name} ({len(documents)} docs)")
            except Exception as e:
                print(f"    ERROR building BM25 for {name}: {e}")

    def search(
        self,
        query: str,
        n_results: int = 10,
        collection_filter: Optional[Literal['commands', 'docs', 'youtube', 'all']] = 'all',
        include_metadata: bool = True,
        enable_expansion: bool = True,
        semantic_weight: float = 0.6,
        bm25_weight: float = 0.4
    ) -> List[SearchResult]:
        """
        Perform hybrid search across collections

        Args:
            query: Search query text
            n_results: Total number of results to return
            collection_filter: Which collections to search
            include_metadata: Whether to include full metadata
            enable_expansion: Whether to expand query with synonyms
            semantic_weight: Weight for semantic score (default: 0.6)
            bm25_weight: Weight for BM25 score (default: 0.4)

        Returns:
            List of SearchResult objects, sorted by hybrid relevance
        """

        start_time = time.time()

        # Check cache first
        if self.enable_cache:
            cache_key = f"{query.lower()}|{n_results}|{collection_filter or 'all'}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                elapsed = (time.time() - start_time) * 1000
                stats = self.cache.get_stats()
                print(f"CACHE HIT in {elapsed:.0f}ms (hit rate: {stats['hit_rate']:.1%})")
                return cached_results

        # Expand query if enabled
        original_query = query
        if enable_expansion:
            expanded_query = self.query_expander.expand_query(query)
            if expanded_query != query:
                print(f"Query expanded: '{query}' -> '{expanded_query}'")
                query = expanded_query

        # Generate query embedding for semantic search
        query_embedding = self.model.encode([query])[0].tolist()

        # Tokenize query for BM25 search
        query_tokens = query.lower().split()

        all_results = []

        # Determine which collections to search
        collections_to_search = self._get_collections_to_search(collection_filter)

        # Search each collection with hybrid approach
        for collection_name, collection in collections_to_search.items():
            # Semantic search
            semantic_results = self._semantic_search(
                collection=collection,
                collection_name=collection_name,
                query_embedding=query_embedding,
                n_results=n_results * 2  # Get more candidates for merging
            )

            # BM25 keyword search
            bm25_results = self._bm25_search(
                collection_name=collection_name,
                query_tokens=query_tokens,
                n_results=n_results * 2
            )

            # Merge results with hybrid scoring
            hybrid_results = self._merge_hybrid_results(
                semantic_results=semantic_results,
                bm25_results=bm25_results,
                semantic_weight=semantic_weight,
                bm25_weight=bm25_weight
            )

            all_results.extend(hybrid_results)

        # Final ranking and selection
        final_results = self._merge_and_rank(all_results, n_results)

        # Cache results
        if self.enable_cache:
            cache_key = f"{original_query.lower()}|{n_results}|{collection_filter or 'all'}"
            self.cache.put(cache_key, final_results)

        elapsed = (time.time() - start_time) * 1000

        print(f"\nHybrid search completed in {elapsed:.0f}ms")
        print(f"  Commands: {sum(1 for r in final_results if r.source == 'command')}")
        print(f"  Documentation: {sum(1 for r in final_results if r.source == 'documentation')}")
        print(f"  YouTube: {sum(1 for r in final_results if r.source == 'youtube')}")
        print(f"  Total: {len(final_results)}")
        if self.enable_cache:
            stats = self.cache.get_stats()
            print(f"  Cache hit rate: {stats['hit_rate']:.1%}")
        print()

        return final_results

    def _get_collections_to_search(self, filter_value: Optional[str]) -> Dict:
        """Get collections based on filter"""
        if not filter_value or filter_value == 'all':
            collections = {}
            if self.commands_collection:
                collections['ghl-knowledge-base'] = self.commands_collection
            if self.docs_collection:
                collections['ghl-docs'] = self.docs_collection
            if self.youtube_collection:
                collections['ghl-youtube'] = self.youtube_collection
            if self.business_collection:
                collections['ghl-business'] = self.business_collection
            # Add data KB collections
            for col_name, col in self.data_kb_collections.items():
                collections[col_name] = col
            return collections

        filter_map = {
            'commands': [('ghl-knowledge-base', self.commands_collection)],
            'docs': [('ghl-docs', self.docs_collection)],
            'youtube': [('ghl-youtube', self.youtube_collection)]
        }

        collections = {}
        for name, collection in filter_map.get(filter_value, []):
            if collection:
                collections[name] = collection
        return collections

    def _semantic_search(
        self,
        collection,
        collection_name: str,
        query_embedding: List[float],
        n_results: int
    ) -> List[SearchResult]:
        """Perform semantic vector search"""
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'distances', 'metadatas']
            )

            search_results = []

            if results['documents'] and results['documents'][0]:
                for doc, distance, metadata in zip(
                    results['documents'][0],
                    results['distances'][0],
                    results['metadatas'][0] if results['metadatas'] else [{}] * len(results['documents'][0])
                ):
                    # Convert distance to relevance score
                    relevance = max(0, 1 - (distance / 2))

                    # Determine source type
                    source = self._get_source_type(collection_name)

                    search_results.append(SearchResult(
                        content=doc,
                        distance=distance,
                        source=source,
                        collection_name=collection_name,
                        metadata=metadata or {},
                        relevance_score=relevance
                    ))

            return search_results

        except Exception as e:
            print(f"Error in semantic search for {collection_name}: {e}")
            return []

    def _bm25_search(
        self,
        collection_name: str,
        query_tokens: List[str],
        n_results: int
    ) -> List[Dict]:
        """Perform BM25 keyword search"""
        if collection_name not in self.bm25_indices:
            return []

        try:
            bm25 = self.bm25_indices[collection_name]
            documents = self.documents_cache[collection_name]

            # Get BM25 scores for all documents
            scores = bm25.get_scores(query_tokens)

            # Get top N indices
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]

            # Build results
            bm25_results = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include docs with non-zero scores
                    bm25_results.append({
                        'document': documents[idx],
                        'bm25_score': scores[idx]
                    })

            return bm25_results

        except Exception as e:
            print(f"Error in BM25 search for {collection_name}: {e}")
            return []

    def _merge_hybrid_results(
        self,
        semantic_results: List[SearchResult],
        bm25_results: List[Dict],
        semantic_weight: float,
        bm25_weight: float
    ) -> List[SearchResult]:
        """Merge semantic and BM25 results with weighted scoring"""

        # Normalize BM25 scores to 0-1 range
        if bm25_results:
            max_bm25 = max(r['bm25_score'] for r in bm25_results)
            if max_bm25 > 0:
                for result in bm25_results:
                    result['bm25_score_normalized'] = result['bm25_score'] / max_bm25

        # Create index for fast BM25 lookup by document content
        bm25_by_doc = {r['document']: r.get('bm25_score_normalized', 0.0) for r in bm25_results}

        # Combine scores
        for result in semantic_results:
            bm25_score = bm25_by_doc.get(result.content, 0.0)
            result.bm25_score = bm25_score
            result.hybrid_score = (semantic_weight * result.relevance_score) + (bm25_weight * bm25_score)

        return semantic_results

    def _merge_and_rank(
        self,
        results: List[SearchResult],
        n_results: int
    ) -> List[SearchResult]:
        """Apply final ranking with collection boosts"""

        # Apply collection-specific boosts
        for result in results:
            boost = 1.0
            if result.source == 'command':
                boost = 1.05  # 5% boost for commands
            elif result.source == 'youtube':
                boost = 1.03  # 3% boost for YouTube

            result.hybrid_score *= boost

        # Sort by hybrid score
        sorted_results = sorted(results, key=lambda x: x.hybrid_score, reverse=True)

        return sorted_results[:int(n_results)]

    def _get_source_type(self, collection_name: str) -> Literal['command', 'documentation', 'youtube']:
        """Map collection name to source type"""
        if 'knowledge-base' in collection_name:
            return 'command'
        elif 'youtube' in collection_name:
            return 'youtube'
        else:
            return 'documentation'

    def _query_collection(
        self,
        collection,
        query_embedding: List[float],
        n_results: int,
        source: Literal['command', 'documentation', 'youtube']
    ) -> List[SearchResult]:
        """Legacy method for backward compatibility - delegates to _semantic_search"""
        return self._semantic_search(
            collection=collection,
            collection_name=collection.name,
            query_embedding=query_embedding,
            n_results=n_results
        )

    def format_results(
        self,
        results: List[SearchResult],
        max_content_length: int = 500
    ) -> str:
        """
        Format search results for display

        Args:
            results: List of SearchResult objects
            max_content_length: Maximum characters to display per result

        Returns:
            Formatted string with all results
        """

        if not results:
            return "No results found."

        output = []
        output.append("=" * 80)
        output.append("SEARCH RESULTS")
        output.append("=" * 80)
        output.append("")

        for idx, result in enumerate(results, 1):
            # Source badge
            if result.source == 'command':
                source_badge = "[COMMAND]"
            elif result.source == 'youtube':
                source_badge = "[YOUTUBE]"
            else:
                source_badge = "[DOCS]"

            # Show hybrid score if available, otherwise relevance score
            score_display = f"Hybrid: {result.hybrid_score:.2%}" if result.hybrid_score > 0 else f"Relevance: {result.relevance_score:.2%}"
            output.append(f"[{idx}] {source_badge} ({score_display})")
            output.append("-" * 80)

            # Add metadata if available
            if result.metadata:
                if 'title' in result.metadata:
                    output.append(f"Title: {result.metadata['title']}")
                if 'category' in result.metadata:
                    output.append(f"Category: {result.metadata['category']}")
                if 'url' in result.metadata:
                    output.append(f"URL: {result.metadata['url']}")
                output.append("")

            # Content preview (sanitize unicode for Windows console)
            content = result.content[:max_content_length]
            if len(result.content) > max_content_length:
                content += "..."
            # Replace problematic unicode characters
            content = content.encode('ascii', 'ignore').decode('ascii')
            output.append(content)
            output.append("-" * 80)
            output.append("")

        return "\n".join(output)

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if self.cache:
            return self.cache.get_stats()
        return {'enabled': False}


def main():
    """Example usage and testing"""
    import argparse

    parser = argparse.ArgumentParser(description='BroBro Enhanced Hybrid Search')
    parser.add_argument('query', nargs='+', help='Search query')
    parser.add_argument('--n-results', '-n', type=int, default=10,
                       help='Number of results to return (default: 10)')
    parser.add_argument('--filter', '-f', choices=['commands', 'docs', 'youtube', 'all'],
                       default='all', help='Which collections to search (default: all)')
    parser.add_argument('--no-expansion', action='store_true',
                       help='Disable query expansion')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable query caching')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')

    args = parser.parse_args()

    # Join query words
    query = ' '.join(args.query)

    # Initialize search
    search = MultiCollectionSearch(enable_cache=not args.no_cache)

    # Perform search
    print(f"Searching for: \"{query}\"")
    print(f"Filter: {args.filter}")
    print(f"Max results: {args.n_results}")
    print()

    results = search.search(
        query=query,
        n_results=args.n_results,
        collection_filter=args.filter,
        enable_expansion=not args.no_expansion
    )

    # Output results
    if args.json:
        import json
        output = [{
            'content': r.content,
            'source': r.source,
            'relevance': r.relevance_score,
            'bm25_score': r.bm25_score,
            'hybrid_score': r.hybrid_score,
            'metadata': r.metadata
        } for r in results]
        print(json.dumps(output, indent=2))
    else:
        print(search.format_results(results))

    # Show cache stats if enabled
    if not args.no_cache:
        stats = search.get_cache_stats()
        if stats.get('enabled', True):
            print(f"\nCache Stats: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate']:.1%} hit rate")


if __name__ == '__main__':
    main()
