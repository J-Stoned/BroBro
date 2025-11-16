"""
Index ALL business books from JSON files into ChromaDB
This is what was MISSING!
"""
import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
import hashlib

print("="*60)
print("BroBro - BOOK INDEXER")
print("="*60)

# Connect to ChromaDB
client = chromadb.HttpClient(host='localhost', port=8001)
print("[OK] Connected to ChromaDB")

# Load embedding model
print("[LOADING] Sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("[OK] Model loaded")

# Get or create collection
try:
    collection = client.get_collection("ghl-knowledge-base")
    print(f"[OK] Using collection: ghl-knowledge-base ({collection.count()} items)")
except:
    collection = client.create_collection("ghl-knowledge-base")
    print("[OK] Created new collection: ghl-knowledge-base")

# Path to books
books_path = Path("C:/Users/justi/BroBro/data/books")
book_files = list(books_path.glob("*.json"))

print(f"\n[FOUND] {len(book_files)} book files to process\n")

total_chunks = 0

for book_file in book_files:
    print(f"\nProcessing: {book_file.name}")
    
    try:
        with open(book_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get('title', book_file.stem)
        author = data.get('author', 'Unknown')
        entries = data.get('entries', [])
        
        if not entries:
            # Maybe the whole thing is text?
            if 'content' in data:
                entries = [{'content': data['content']}]
            elif 'text' in data:
                entries = [{'content': data['text']}]
            else:
                print(f"  [SKIP] No entries found in {book_file.name}")
                continue
        
        print(f"  Title: {title}")
        print(f"  Author: {author}")
        print(f"  Entries: {len(entries)}")
        
        # Process each entry
        chunks_added = 0
        for i, entry in enumerate(entries):
            # Get text content
            if isinstance(entry, dict):
                text = entry.get('content', entry.get('text', str(entry)))
            else:
                text = str(entry)
            
            if len(text) < 50:  # Skip tiny chunks
                continue
            
            # Create unique ID
            chunk_id = hashlib.md5(f"{title}_{i}_{text[:100]}".encode()).hexdigest()
            
            # Generate embedding
            embedding = model.encode(text).tolist()
            
            # Add to collection
            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[text[:8000]],  # Limit size
                metadatas=[{
                    "source": "business_book",
                    "title": title,
                    "author": author,
                    "type": "book",
                    "chunk_index": i,
                    "file": book_file.name
                }]
            )
            chunks_added += 1
            
            if chunks_added % 10 == 0:
                print(f"    Added {chunks_added} chunks...")
        
        print(f"  [DONE] Added {chunks_added} chunks from {title}")
        total_chunks += chunks_added
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        continue

print(f"\n" + "="*60)
print(f"COMPLETE! Indexed {total_chunks} chunks from {len(book_files)} books")
print(f"Collection now has: {collection.count()} total items")
print("="*60)
