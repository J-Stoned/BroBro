#!/usr/bin/env python3
"""
Query GHL WHIZ KB about service package and pricing strategy for Josh Wash
"""

import sys
import time
from search_api import MultiCollectionSearch

def query_kb(question, n_results=5):
    """Query the knowledge base and print results"""
    search = MultiCollectionSearch()
    
    print("\n" + "="*80)
    print(f"QUERY: {question}")
    print("="*80 + "\n")
    
    start = time.time()
    results = search.search(question, n_results=n_results)
    elapsed = (time.time() - start) * 1000
    
    print(f"Found {len(results)} results in {elapsed:.0f}ms\n")
    
    for idx, result in enumerate(results, 1):
        source_tag = "[CMD]" if result.source == 'command' else "[DOC]"
        title = result.metadata.get('title', 'No title')
        
        print(f"\n--- Result {idx} ({source_tag}) ---")
        print(f"Title: {title}")
        print(f"Relevance: {result.relevance_score:.1%}")
        print(f"\nContent:\n{result.content[:500]}...")
        print("-" * 80)

if __name__ == '__main__':
    # Query about service package pricing strategy
    questions = [
        "What is the best pricing strategy for service packages and bundles?",
        "How should I price tiered service packages to maximize profit margins?",
        "How much discount should I offer for bundle packages vs individual services?",
        "Service package pricing strategy for home services business",
    ]
    
    for question in questions:
        query_kb(question, n_results=3)
        print("\n\n")
