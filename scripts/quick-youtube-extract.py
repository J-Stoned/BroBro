#!/usr/bin/env python3
"""
Quick YouTube Transcript Extractor
Simple, direct YouTube transcript extraction and embedding
"""

import os
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import chromadb
from sentence_transformers import SentenceTransformer
import re

# Video IDs to extract (from your configured sources)
VIDEO_URLS = [
    # Robb Bailey - GoHighLevel tutorials
    "https://www.youtube.com/watch?v=YgaZb_vtCuA",  # Smart Websites
    "https://www.youtube.com/watch?v=E3l9YvX8l7w",  # Workflows
    "https://www.youtube.com/watch?v=K5M3xQ3oZ-M",  # Automation

    # GoHighLevel Official
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Example video

    # You can add more URLs here...
]

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript for a video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([entry['text'] for entry in transcript_list])
        return full_transcript
    except TranscriptsDisabled:
        print(f"  [SKIP] Transcripts disabled for {video_id}")
        return None
    except NoTranscriptFound:
        print(f"  [SKIP] No transcript found for {video_id}")
        return None
    except Exception as e:
        print(f"  [ERROR] {video_id}: {e}")
        return None

def chunk_transcript(transcript, chunk_size=1000, overlap=200):
    """Split transcript into chunks"""
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

def embed_transcript(video_id, title, transcript, collection, model):
    """Embed transcript chunks into ChromaDB"""
    # Clean transcript
    transcript = re.sub(r'\s+', ' ', transcript).strip()

    # Chunk transcript
    chunks = chunk_transcript(transcript)
    print(f"  Chunked into {len(chunks)} pieces")

    # Embed each chunk
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
                    'type': 'video_transcript'
                }]
            )

            added_count += 1
        except Exception as e:
            print(f"  [ERROR] Chunk {idx}: {e}")

    print(f"  Successfully embedded {added_count}/{len(chunks)} chunks")
    return added_count

def main():
    print("=" * 80)
    print("Quick YouTube Transcript Extractor")
    print("=" * 80)
    print()

    # Initialize ChromaDB
    print(">> Connecting to ChromaDB...")
    client = chromadb.HttpClient(host='localhost', port=8001)

    try:
        collection = client.get_collection(name="ghl-youtube")
        print(f">> Connected to ghl-youtube collection ({collection.count()} existing items)")
    except:
        collection = client.create_collection(name="ghl-youtube")
        print(">> Created ghl-youtube collection")

    # Load embedding model
    print(">> Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print()
    print("=" * 80)
    print(f"Extracting {len(VIDEO_URLS)} videos...")
    print("=" * 80)
    print()

    total_extracted = 0
    total_skipped = 0
    total_chunks = 0

    for idx, url in enumerate(VIDEO_URLS, 1):
        video_id = extract_video_id(url)
        if not video_id:
            print(f"[{idx}/{len(VIDEO_URLS)}] INVALID URL: {url}")
            total_skipped += 1
            continue

        print(f"[{idx}/{len(VIDEO_URLS)}] Processing: {video_id}")

        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            total_skipped += 1
            continue

        print(f"  Transcript length: {len(transcript)} characters")

        # Use video ID as title for now (you can update with real titles)
        title = f"YouTube Video {video_id}"

        # Embed transcript
        chunks_added = embed_transcript(video_id, title, transcript, collection, model)
        total_chunks += chunks_added
        total_extracted += 1

        print()

    # Final stats
    final_count = collection.count()
    print("=" * 80)
    print("EXTRACTION COMPLETE!")
    print("=" * 80)
    print(f"Videos extracted: {total_extracted}")
    print(f"Videos skipped: {total_skipped}")
    print(f"Total chunks added: {total_chunks}")
    print(f"Collection total: {final_count} items")
    print("=" * 80)

if __name__ == '__main__':
    main()
