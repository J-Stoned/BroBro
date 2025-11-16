#!/usr/bin/env python3
"""
FAST AI-Powered Knowledge Base Query System for BroBro
Optimized for speed: 3-5 second responses
"""

import os
import sys
from dotenv import load_dotenv
import chromadb
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Import elite Claude API manager
try:
    from src.services.claude import ClaudeAPIManager
    ELITE_API_AVAILABLE = True
except ImportError:
    ELITE_API_AVAILABLE = False

# Global cached resources
_client = None
_collections = None
_anthropic = None
_api_manager = None

def get_client():
    """Get or create ChromaDB client (cached)"""
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host="localhost", port=8001)
    return _client

def get_collections():
    """Get or create collection references (cached)"""
    global _collections
    if _collections is None:
        client = get_client()
        _collections = {
            'books': client.get_collection(name="ghl-knowledge-base"),
            'docs': client.get_collection(name="ghl-docs"),
            'youtube': client.get_collection(name="ghl-youtube"),
        }
    return _collections

def get_anthropic():
    """Get or create Anthropic client (cached)"""
    global _anthropic
    if _anthropic is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        _anthropic = Anthropic(api_key=api_key)
    return _anthropic

def get_api_manager():
    """Get or create Elite API manager (cached)"""
    global _api_manager
    if _api_manager is None and ELITE_API_AVAILABLE:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _api_manager = ClaudeAPIManager(api_key)
    return _api_manager

def fast_search(query, n_results=5):
    """Fast search across all collections"""
    collections = get_collections()
    all_results = []

    for name, collection in collections.items():
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )

            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    all_results.append({
                        'text': doc[:500],  # Truncate to save tokens
                        'source': results['metadatas'][0][i].get('title', 'Unknown'),
                        'type': name
                    })
        except:
            continue

    return all_results[:n_results]  # Return top 5

def fast_query(user_query):
    """Process query quickly"""
    print(f"\n[*] Query: {user_query}")
    print(f"[*] Searching...")

    # Fast search
    results = fast_search(user_query)

    if not results:
        return "No relevant results found in the knowledge base."

    print(f"[OK] Found {len(results)} results")
    print(f"[*] Generating answer...")

    # Build context from results
    context = "\n\n".join([
        f"Source {i+1} ({r['type']}): {r['source']}\n{r['text']}"
        for i, r in enumerate(results)
    ])

    # Generate fast response with Claude Haiku (much faster than Sonnet)
    api_manager = get_api_manager()

    user_message = f"""Answer this question using ONLY the provided knowledge base content. Be concise and direct.

Question: {user_query}

Knowledge Base Content:
{context}

Provide a clear, actionable answer in 2-3 paragraphs maximum. If the answer isn't in the knowledge base, say so."""

    if api_manager:
        # Use elite API manager with intelligent routing
        elite_response = api_manager.send_message(
            messages=[{"role": "user", "content": user_message}],
            profile="fast-response",  # Use fast-response profile for speed
            user_id="kb_query_fast",
            endpoint="/api/kb/query/fast"
        )

        if not elite_response.success:
            print(f"[WARN] Elite API failed: {elite_response.error}, falling back to standard")
            # Fallback to standard
            anthropic = get_anthropic()
            response = anthropic.messages.create(
                model="claude-haiku-4-5-20241022",
                max_tokens=6000,
                messages=[{"role": "user", "content": user_message}]
            )
            answer = response.content[0].text
        else:
            answer = elite_response.content
            print(f"[ELITE] Cost: ${elite_response.cost:.6f} | Model: {elite_response.model_used}")
    else:
        # Standard client
        anthropic = get_anthropic()
        response = anthropic.messages.create(
            model="claude-haiku-4-5-20241022",  # FAST model (Haiku 4.5)
            max_tokens=6000,  # Increased for better responses
            messages=[{"role": "user", "content": user_message}]
        )
        answer = response.content[0].text

    print(f"[OK] Answer generated\n")
    print("="*80)
    print("ANSWER")
    print("="*80)
    print(answer)
    print()
    print("="*80)
    print("SOURCES")
    print("="*80)
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['type'].upper()}] {r['source']}")
    print("="*80)

    return answer

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_kb_query_fast.py \"your question here\"")
        sys.exit(1)

    query = sys.argv[1]

    try:
        fast_query(query)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
