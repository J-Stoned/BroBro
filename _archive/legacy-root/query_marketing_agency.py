import chromadb
from chromadb.config import Settings

# Connect to the local ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Get the collection (assuming it's named 'knowledge_base' or similar)
collections = client.list_collections()
print(f"\nAvailable collections: {[c.name for c in collections]}\n")

# Try to get the main collection
collection = None
for coll in collections:
    print(f"Trying collection: {coll.name}")
    collection = client.get_collection(coll.name)
    break

if collection:
    # Query for marketing agency growth strategies
    query_text = "how to grow and scale a marketing agency business from zero to profitable with client acquisition strategies"
    
    print(f"\nQuerying: '{query_text}'\n")
    print("="*80)
    
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
            print(f"\n--- Result {i} (Relevance: {1 - distance:.3f}) ---")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            if 'book' in metadata:
                print(f"Book: {metadata['book']}")
            print(f"\nContent:\n{doc[:500]}...")
            print()
    else:
        print("No results found!")
else:
    print("No collections found!")
