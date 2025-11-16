import chromadb

client = chromadb.HttpClient(host='localhost', port=8001)

try:
    coll = client.get_collection('data-kb-books')
    print(f'data-kb-books collection EXISTS with {coll.count()} items')
except Exception as e:
    print(f'data-kb-books collection does NOT exist: {e}')
