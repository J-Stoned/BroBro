#!/usr/bin/env python3
"""
Simple YouTube Transcript Adder
Paste your transcript, add metadata, and it gets embedded automatically!
"""

import re
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

def chunk_transcript(transcript, chunk_size=1000, overlap=200):
    """Split transcript into chunks with overlap"""
    words = transcript.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)

        if end >= len(words):
            break
        start = end - overlap

    return chunks

def embed_transcript(video_id, title, transcript):
    """Embed transcript into ChromaDB"""

    print("\n" + "=" * 80)
    print("Embedding Transcript to GHL WHIZ Knowledge Base")
    print("=" * 80)

    # Connect to ChromaDB
    print("\n>> Connecting to ChromaDB...")
    client = chromadb.HttpClient(host='localhost', port=8001)

    try:
        collection = client.get_collection(name="ghl-youtube")
        print(f">> Connected to ghl-youtube collection ({collection.count()} existing items)")
    except:
        collection = client.create_collection(name="ghl-youtube")
        print(">> Created ghl-youtube collection")

    # Load model
    print(">> Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Clean transcript
    print(f"\n>> Processing transcript...")
    transcript = re.sub(r'\s+', ' ', transcript).strip()
    print(f"   Transcript length: {len(transcript)} characters")

    # Chunk transcript
    chunks = chunk_transcript(transcript)
    print(f"   Split into {len(chunks)} chunks")

    # Embed each chunk
    print(f"\n>> Embedding chunks...")
    added_count = 0
    for idx, chunk in enumerate(chunks):
        try:
            # Generate embedding
            embedding = model.encode(chunk).tolist()

            # Create unique document ID
            doc_id = f"youtube_{video_id}_chunk_{idx}"

            # Add to collection
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    'source': 'youtube',
                    'video_id': video_id,
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'type': 'video_transcript',
                    'added_date': datetime.now().isoformat()
                }]
            )

            added_count += 1
            print(f"   Chunk {idx + 1}/{len(chunks)} embedded...")

        except Exception as e:
            print(f"   ERROR on chunk {idx}: {e}")

    # Final stats
    final_count = collection.count()
    print(f"\n>> SUCCESS!")
    print(f"   Added {added_count}/{len(chunks)} chunks")
    print(f"   Collection now has {final_count} total items")
    print("=" * 80)

    return added_count

def main():
    """Interactive transcript addition"""

    print("=" * 80)
    print("GHL WHIZ - Add YouTube Transcript to Knowledge Base")
    print("=" * 80)
    print()
    print("This tool helps you add YouTube transcripts to your knowledge base.")
    print("You'll need:")
    print("  1. Video ID (from YouTube URL)")
    print("  2. Video title")
    print("  3. Full transcript text (copy-pasted)")
    print()
    print("=" * 80)
    print()

    # Get video ID
    print("Step 1: Video ID")
    print("-" * 80)
    print("Example URL: https://www.youtube.com/watch?v=ABC123xyz")
    print("Video ID would be: ABC123xyz")
    print()
    video_id = input("Enter Video ID: ").strip()

    if not video_id:
        print("\nERROR: Video ID is required!")
        return

    # Get title
    print("\nStep 2: Video Title")
    print("-" * 80)
    title = input("Enter video title: ").strip()

    if not title:
        print("\nERROR: Title is required!")
        return

    # Get transcript
    print("\nStep 3: Transcript")
    print("-" * 80)
    print("Paste the full transcript below.")
    print("When done, press Enter, then Ctrl+Z (Windows) or Ctrl+D (Mac/Linux), then Enter again.")
    print()

    transcript_lines = []
    try:
        while True:
            line = input()
            transcript_lines.append(line)
    except EOFError:
        pass

    transcript = '\n'.join(transcript_lines).strip()

    if not transcript:
        print("\nERROR: Transcript is required!")
        return

    # Confirm
    print("\n" + "=" * 80)
    print("Ready to embed:")
    print("=" * 80)
    print(f"Video ID: {video_id}")
    print(f"Title: {title}")
    print(f"Transcript length: {len(transcript)} characters")
    print()

    confirm = input("Proceed? (y/n): ").strip().lower()

    if confirm != 'y':
        print("\nCancelled.")
        return

    # Embed
    embed_transcript(video_id, title, transcript)

    print("\nDone! Transcript is now searchable in your knowledge base.")

if __name__ == '__main__':
    main()
