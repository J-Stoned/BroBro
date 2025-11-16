import chromadb

c = chromadb.HttpClient(host='localhost', port=8001)

print("="*60)
print("DEBUGGING: WHERE ARE THE BOOKS?")
print("="*60)

# Check ALL collections for book content
collections = c.list_collections()

for col in collections:
    print(f"\n--- {col.name} ({col.count()} items) ---")
    
    # Search for book-related terms
    results = col.query(
        query_texts=["hormozi offer value"],
        n_results=3
    )
    
    if results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            source = meta.get('source', 'unknown')
            title = meta.get('title', meta.get('name', 'no title'))
            doc_type = meta.get('type', 'unknown')
            distance = results['distances'][0][i]
            
            print(f"  Result {i+1}:")
            print(f"    Source: {source}")
            print(f"    Type: {doc_type}")
            print(f"    Title: {title}")
            print(f"    Distance: {distance:.4f}")
            print(f"    Preview: {doc[:100]}...")
            print()

print("\n" + "="*60)
print("LOOKING FOR SPECIFIC BOOK METADATA...")
print("="*60)

# Check what types/sources exist in ghl-knowledge-base
kb = c.get_collection('ghl-knowledge-base')
sample = kb.peek(100)

sources = set()
types = set()
for m in sample['metadatas']:
    sources.add(m.get('source', 'unknown'))
    types.add(m.get('type', 'unknown'))

print(f"\nUnique sources in ghl-knowledge-base: {sources}")
print(f"Unique types in ghl-knowledge-base: {types}")
