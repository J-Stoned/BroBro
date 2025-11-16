import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host='localhost',
    port=8001,
    settings=Settings(anonymized_telemetry=False)
)

# Get the ghl-business collection
coll = client.get_collection('ghl-business')
print(f"\nghl-business collection: {coll.count()} items\n")

# Peek at some items to see what's in there
results = coll.peek(limit=5)
print("Sample items:")
for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
    print(f"\n{i+1}. {doc[:200]}...")
    print(f"   Metadata: {meta}")
