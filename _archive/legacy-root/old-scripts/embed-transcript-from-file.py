"""
BroBro - Embed YouTube Transcript from File

Usage: python embed-transcript-from-file.py <video_url> <title> <transcript_file.txt>
"""

import sys
import os
import re
from typing import List
import chromadb
from sentence_transformers import SentenceTransformer

class TranscriptEmbedder:
    """Embeds YouTube transcripts from text files into ChromaDB"""

    def __init__(self):
        """Initialize the embedder"""
        print(">> Initializing Transcript Embedder...")

        # Initialize embedding model
        print(">> Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Connect to ChromaDB
        chroma_client = chromadb.HttpClient(host='localhost', port=8001)

        # Get or create YouTube collection
        try:
            self.collection = chroma_client.get_collection(name="ghl-youtube")
            doc_count = self.collection.count()
            print(f">> Connected to existing collection: ghl-youtube")
            print(f"   Current document count: {doc_count}")
        except:
            self.collection = chroma_client.create_collection(
                name="ghl-youtube",
                metadata={"description": "YouTube video transcripts about GoHighLevel"}
            )
            print(">> Created new collection: ghl-youtube")

    def chunk_transcript(self, transcript: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split transcript into chunks with overlap for better context
        """
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

    def embed_transcript(self, video_url: str, title: str, transcript: str):
        """
        Embed a transcript into ChromaDB
        """
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
        if not video_id_match:
            print(f"[ERROR] Could not extract video ID from URL: {video_url}")
            return False

        video_id = video_id_match.group(1)

        # Sanitize title for console
        safe_title = title.encode('ascii', 'ignore').decode('ascii')

        print(f"\n>> Processing: {safe_title[:60]}...")
        print(f"   Video ID: {video_id}")
        print(f"   Transcript length: {len(transcript)} characters")

        # Clean transcript
        transcript = re.sub(r'\s+', ' ', transcript).strip()

        # Chunk transcript
        chunks = self.chunk_transcript(transcript)
        print(f"   >> Split into {len(chunks)} chunks")

        # Embed each chunk
        added_count = 0
        for idx, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = self.model.encode(chunk).tolist()

                # Create unique document ID
                doc_id = f"youtube_{video_id}_chunk_{idx}"

                # Add to collection
                self.collection.add(
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
                print(f"   [ERROR] Error embedding chunk {idx}: {e}")

        print(f"   [OK] Added {added_count}/{len(chunks)} chunks to database")

        # Show updated count
        final_count = self.collection.count()
        print(f"\n   Collection now has {final_count} total documents")

        return True


def main():
    """Main execution function"""
    print("="*60)
    print("BroBro YouTube Transcript Embedder (File-based)")
    print("="*60)

    if len(sys.argv) != 4:
        print("\nUsage: python embed-transcript-from-file.py <video_url> <title> <transcript_file.txt>")
        print("\nExample:")
        print('  python embed-transcript-from-file.py "https://www.youtube.com/watch?v=abc123" "Video Title" transcript.txt')
        sys.exit(1)

    video_url = sys.argv[1]
    title = sys.argv[2]
    transcript_file = sys.argv[3]

    # Check if file exists
    if not os.path.exists(transcript_file):
        print(f"\n[ERROR] Transcript file not found: {transcript_file}")
        sys.exit(1)

    # Read transcript from file
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
    except Exception as e:
        print(f"\n[ERROR] Could not read transcript file: {e}")
        sys.exit(1)

    if not transcript.strip():
        print(f"\n[ERROR] Transcript file is empty")
        sys.exit(1)

    try:
        embedder = TranscriptEmbedder()
        success = embedder.embed_transcript(video_url, title, transcript)

        if success:
            print("\n" + "="*60)
            print("[OK] Transcript successfully embedded!")
            print("="*60)
        else:
            print("\n[ERROR] Failed to embed transcript")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
