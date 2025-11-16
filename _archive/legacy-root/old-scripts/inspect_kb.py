import sys
sys.stdout.reconfigure(encoding='utf-8')
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("ghl-knowledge-base")

# Get a sample of documents
results = collection.get(limit=5, include=['documents', 'metadatas'])

print(f"\nCollection: ghl-knowledge-base")
print(f"Total documents: {collection.count()}\n")
print("="*80)
print("SAMPLE DOCUMENTS:")
print("="*80)

for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
    print(f"\n### Document {i}")
    print(f"Metadata: {meta}")
    text = doc.replace('\u2192', '->').replace('\u2013', '-')
    print(f"Content preview: {text[:300]}...")
    print()
