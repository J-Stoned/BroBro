import chromadb
c = chromadb.HttpClient(host='localhost', port=8001)
col = c.get_collection('ghl-knowledge-base')
results = col.peek(10)
print('KNOWLEDGE BASE SAMPLE (first 10 items):')
print('='*50)
for m in results['metadatas']:
    source = m.get('source', 'unknown')
    title = m.get('title', m.get('name', 'no title'))
    print(f"- {source}: {title}")
