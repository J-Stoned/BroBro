import chromadb
import sys
from chromadb.config import Settings

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Connect to the local ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
collections = client.list_collections()
print(f"\nAvailable collections:")
for c in collections:
    coll = client.get_collection(c.name)
    count = coll.count()
    print(f"  - {c.name}: {count} documents")

# Try the knowledge base collection
print("\n\nQuerying ghl-knowledge-base collection...")
print("="*80)

collection = client.get_collection("ghl-knowledge-base")

# Query for marketing agency growth strategies  
query_text = "how to grow and scale a marketing agency business strategies for client acquisition"

print(f"\nQuery: '{query_text}'\n")

results = collection.query(
    query_texts=[query_text],
    n_results=10
)

# Display results
if results and results['documents']:
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"\n--- Result {i} (Similarity: {1 - distance:.3f}) ---")
        if 'book' in metadata:
            print(f"Book: {metadata.get('book', 'Unknown')}")
        if 'source' in metadata:
            print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"\nContent Preview:\n{doc[:400]}")
        print()
else:
    print("No results found!")
