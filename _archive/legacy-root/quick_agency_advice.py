import sys
sys.stdout.reconfigure(encoding='utf-8')

import chromadb

# Connect directly to the persistent database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("ghl-knowledge-base")

# Query for marketing agency growth
results = collection.query(
    query_texts=["how to grow marketing agency business strategies client acquisition scaling profitable"],
    n_results=15
)

print("\n" + "="*80)
print("MARKETING AGENCY GROWTH STRATEGIES FROM YOUR 21 BUSINESS BOOKS")
print("="*80 + "\n")

for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
    book = meta.get('book', 'Unknown')
    print(f"\n### INSIGHT {i} - From: {book}")
    print("-" * 80)
    # Clean and print the text
    text = doc.replace('\u2192', '->').replace('\u2013', '-').replace('\u2019', "'")
    print(text[:600] + "..." if len(text) > 600 else text)
    print()
