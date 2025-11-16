#!/usr/bin/env python3
"""
BroBro - Multi-Collection Search Integration Tests
Tests search across both ghl-knowledge-base and ghl-docs collections
"""

import time
from search_api import MultiCollectionSearch


def test_query(search, query, expected_sources=None):
    """Test a single query and validate results"""
    print("="*80)
    print(f"QUERY: \"{query}\"")
    print("="*80)

    start = time.time()
    results = search.search(query, n_results=5)
    elapsed = (time.time() - start) * 1000

    print(f"\nResults: {len(results)}")
    print(f"Time: {elapsed:.0f}ms")
    print(f"Commands: {sum(1 for r in results if r.source == 'command')}")
    print(f"Documentation: {sum(1 for r in results if r.source == 'documentation')}")

    # Show top 3 results
    print("\nTop 3 Results:")
    for idx, result in enumerate(results[:3], 1):
        source_tag = "[CMD]" if result.source == 'command' else "[DOC]"
        title = result.metadata.get('title', 'No title')[:60]
        print(f"  {idx}. {source_tag} {title} ({result.relevance_score:.1%})")

    # Validation
    success = True
    if elapsed > 500:
        print(f"  WARNING: Query took {elapsed:.0f}ms (target <500ms)")
        success = False

    if len(results) == 0:
        print("  ERROR: No results returned")
        success = False

    if expected_sources:
        actual_sources = set(r.source for r in results)
        if expected_sources and not actual_sources.intersection(expected_sources):
            print(f"  WARNING: Expected sources {expected_sources}, got {actual_sources}")

    status = "PASS" if success else "FAIL"
    print(f"\nStatus: {status}")
    print()

    return success


def main():
    """Run all integration tests"""

    print("\n" + "="*80)
    print("BroBro - MULTI-COLLECTION SEARCH TESTS")
    print("="*80)
    print()

    # Initialize search
    search = MultiCollectionSearch()

    # Test queries from requirements
    test_queries = [
        ("How do I create a lead nurture workflow?", {'documentation'}),
        ("Show me appointment reminders", {'command', 'documentation'}),
        ("What's the best way to setup SMS automation?", {'documentation'}),
        ("Create a contact in GoHighLevel", {'command', 'documentation'}),
        ("Email automation best practices", {'documentation'}),
        ("Set up Facebook lead ads", {'documentation'}),
        ("Workflow triggers and actions", {'documentation'}),
        ("Calendar booking settings", {'documentation'}),
        ("Custom fields for contacts", {'documentation'}),
        ("Integration with Stripe", {'documentation'}),
        ("Voice AI agents", {'documentation'}),
        ("Reputation management setup", {'documentation'}),
        ("WhatsApp configuration", {'documentation'}),
        ("Pipeline management", {'documentation'}),
        ("Membership sites and courses", {'documentation'}),
        ("Payment processing", {'documentation'}),
        ("Form builder", {'documentation'}),
        ("Snapshot creation", {'documentation'}),
        ("Agency dashboard", {'documentation'}),
        ("API authentication", {'documentation'}),
    ]

    passed = 0
    failed = 0

    for query, expected_sources in test_queries:
        if test_query(search, query, expected_sources):
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    print()

    if failed == 0:
        print("SUCCESS: All tests passed!")
    else:
        print(f"FAILURE: {failed} test(s) failed")

    return failed == 0


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
