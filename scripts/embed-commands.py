#!/usr/bin/env python3
"""
BroBro - Commands Embedding Script
Converts commands-specification.CSV to embeddings in ghl-knowledge-base collection
Built with BMAD-METHOD for Epic US: Populate Commands Collection
"""

import csv
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from datetime import datetime

def embed_commands():
    print("\n" + "="*80)
    print("BroBro - Commands Embedding Process")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Load CSV
    csv_path = Path("data/commands-specification.csv")
    if not csv_path.exists():
        print(f"[ERROR] Commands file not found at {csv_path}")
        return False

    print(f"[OK] Found commands CSV: {csv_path}")

    commands = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            commands.append(row)

    print(f"[OK] Loaded {len(commands)} commands from CSV\n")

    # 2. Initialize ChromaDB
    print("Connecting to ChromaDB...")
    try:
        chroma_client = chromadb.HttpClient(
            host="localhost",
            port=8001
        )
        # Test connection
        chroma_client.heartbeat()
        print("[OK] Connected to ChromaDB at http://localhost:8001\n")
    except Exception as e:
        print(f"[ERROR] Cannot connect to ChromaDB: {e}")
        print("   Make sure ChromaDB is running: chroma run --host 0.0.0.0 --port 8001 --path ./chroma_db")
        return False

    # 3. Create embedding function
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    print("[OK] Embedding model loaded\n")

    # 4. Get or create collection
    collection_name = "ghl-knowledge-base"
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        existing = collection.count()
        print(f"[OK] Found existing collection: {collection_name}")
        if existing > 0:
            print(f"[WARN] Collection has {existing} items, clearing...")
            collection.delete(where={})
            print(f"[OK] Cleared collection\n")
    except Exception:
        print(f"Creating new collection: {collection_name}")
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"description": "GHL Slash Commands and Automation Templates"}
        )
        print(f"[OK] Created collection: {collection_name}\n")

    # 5. Prepare data for embedding
    print("Preparing commands for embedding...")
    ids = []
    documents = []
    metadatas = []

    for cmd in commands:
        command_id = cmd['command_id']
        category = cmd['category']
        purpose = cmd['purpose']
        example = cmd['real_world_example']
        kb_queries = cmd['kb_search_queries']
        similar = cmd['similar_commands']
        status = cmd['status']

        # Build searchable document text
        doc_text = f"""Command: /{command_id}
Category: {category}
Purpose: {purpose}
Example: {example}
Search Keywords: {kb_queries}
Similar Commands: {similar}"""

        # Create metadata
        metadata = {
            'command_id': command_id,
            'title': f"/{command_id}",
            'category': category,
            'purpose': purpose,
            'example': example,
            'type': 'command',
            'kb_search_queries': kb_queries,
            'similar_commands': similar,
            'status': status,
            'has_examples': bool(example),
            'indexed_date': datetime.now().isoformat()
        }

        ids.append(command_id)
        documents.append(doc_text.strip())
        metadatas.append(metadata)

    print(f"[OK] Prepared {len(documents)} commands\n")

    # 6. Deduplicate IDs (CSV has duplicates)
    print("Deduplicating commands...")
    seen_ids = set()
    unique_ids = []
    unique_docs = []
    unique_meta = []

    for i, cmd_id in enumerate(ids):
        if cmd_id not in seen_ids:
            seen_ids.add(cmd_id)
            unique_ids.append(cmd_id)
            unique_docs.append(documents[i])
            unique_meta.append(metadatas[i])
        else:
            print(f"  [WARN] Skipping duplicate: {cmd_id}")

    print(f"[OK] Kept {len(unique_ids)} unique commands (removed {len(ids) - len(unique_ids)} duplicates)\n")

    # Update arrays
    ids = unique_ids
    documents = unique_docs
    metadatas = unique_meta

    # 7. Add to collection in batches
    print("Embedding commands into ChromaDB...")
    batch_size = 50
    total = len(ids)
    batches = (total - 1) // batch_size + 1

    for i in range(0, total, batch_size):
        batch_num = i // batch_size + 1
        end = min(i + batch_size, total)
        batch_ids = ids[i:end]
        batch_docs = documents[i:end]
        batch_meta = metadatas[i:end]

        try:
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta
            )
            print(f"[OK] Embedded batch {batch_num}/{batches} ({len(batch_ids)} commands)")
        except Exception as e:
            print(f"[ERROR] Error in batch {batch_num}: {e}")
            return False

    # 7. Verify
    final_count = collection.count()
    print(f"\n[SUCCESS] Embedded {final_count} commands into {collection_name}\n")

    # 8. Test search
    print("="*80)
    print("Testing Search Functionality")
    print("="*80)

    test_queries = [
        "send sms",
        "workflow automation",
        "landing page",
        "email sequence",
        "appointment booking"
    ]

    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            num_results = len(results['ids'][0])
            print(f"\nQuery: '{query}'")
            print(f"  Found: {num_results} results")

            if num_results > 0:
                top_result = results['metadatas'][0][0]
                print(f"  Top: /{top_result['command_id']} - {top_result['purpose'][:60]}...")
        except Exception as e:
            print(f"  [ERROR] {e}")

    # 9. Summary
    print("\n" + "="*80)
    print("EMBEDDING COMPLETE")
    print("="*80)
    print(f"Collection: {collection_name}")
    print(f"Commands Embedded: {final_count}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n[SUCCESS] Commands are now available in unified search!")
    print("   Unified search will automatically include these commands")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    try:
        success = embed_commands()
        if success:
            print("[READY] READY FOR TESTING")
            print("\nNext steps:")
            print("1. Restart backend if needed")
            print("2. Test: curl \"http://localhost:8000/api/search/unified?query=send%20sms\"")
            print("3. Open frontend and search for commands")
            exit(0)
        else:
            print("\n[FAILED] EMBEDDING FAILED - Check errors above")
            exit(1)
    except Exception as e:
        print(f"\n[FATAL] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
