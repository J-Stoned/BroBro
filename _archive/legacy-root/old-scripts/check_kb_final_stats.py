#!/usr/bin/env python3
"""Quick script to check final KB statistics"""

import chromadb

# Connect to ChromaDB
client = chromadb.HttpClient(host="localhost", port=8001)

# Get all collections
collections = client.list_collections()

print("="*80)
print("FINAL BroBro KNOWLEDGE BASE STATISTICS")
print("="*80)
print()

total_docs = 0

for collection in collections:
    coll = client.get_collection(name=collection.name)
    count = coll.count()
    total_docs += count
    print(f"{collection.name}: {count:,} documents")

print()
print("-"*80)
print(f"TOTAL DOCUMENTS ACROSS ALL COLLECTIONS: {total_docs:,}")
print("="*80)
