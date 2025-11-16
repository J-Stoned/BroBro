import chromadb

c = chromadb.HttpClient(host='localhost', port=8001)

# Search for book content specifically
print("SEARCHING FOR BOOK CONTENT...")
print("="*60)

# Check ghl-knowledge-base (4076 items - books should be here)
kb = c.get_collection('ghl-knowledge-base')

# Search for Hormozi
print("\n1. SEARCHING FOR 'HORMOZI':")
results = kb.query(query_texts=["hormozi value offer"], n_results=3)
for i, doc in enumerate(results['documents'][0]):
    meta = results['metadatas'][0][i]
    print(f"  - Source: {meta.get('source', 'unknown')}")
    print(f"    Title: {meta.get('title', meta.get('name', 'no title'))}")
    print(f"    Preview: {doc[:150]}...")
    print()

# Search for Russell Brunson
print("\n2. SEARCHING FOR 'BRUNSON FUNNEL':")
results = kb.query(query_texts=["russell brunson funnel secrets"], n_results=3)
for i, doc in enumerate(results['documents'][0]):
    meta = results['metadatas'][0][i]
    print(f"  - Source: {meta.get('source', 'unknown')}")
    print(f"    Title: {meta.get('title', meta.get('name', 'no title'))}")
    print(f"    Preview: {doc[:150]}...")
    print()

# Search for value creation
print("\n3. SEARCHING FOR 'VALUE LADDER':")
results = kb.query(query_texts=["value ladder ascension customer"], n_results=3)
for i, doc in enumerate(results['documents'][0]):
    meta = results['metadatas'][0][i]
    print(f"  - Source: {meta.get('source', 'unknown')}")
    print(f"    Title: {meta.get('title', meta.get('name', 'no title'))}")
    print(f"    Preview: {doc[:150]}...")
    print()

print("\n" + "="*60)
print("If these show GHL docs instead of BOOKS, the books aren't indexed!")
