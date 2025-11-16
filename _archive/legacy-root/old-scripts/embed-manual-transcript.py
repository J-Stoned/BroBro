"""
BroBro - Manual YouTube Transcript Embedder

This script lets you paste YouTube video transcripts manually and embed them into the knowledge base.
"""

import sys
import os
import re
from typing import List
import chromadb
from sentence_transformers import SentenceTransformer

class ManualTranscriptEmbedder:
    """Embeds manually pasted YouTube transcripts into ChromaDB"""

    def __init__(self):
        """Initialize the embedder"""
        print(">> Initializing Manual Transcript Embedder...")

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

        Args:
            transcript: Full transcript text
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
        words = transcript.split()
        chunks = []

        start = 0
        while start < len(words):
            # Calculate end position
            end = start + chunk_size

            # Get chunk
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)

            # Move start position with overlap
            if end >= len(words):
                break
            start = end - overlap

        return chunks

    def embed_transcript(self, video_url: str, title: str, transcript: str):
        """
        Embed a manually pasted transcript into ChromaDB

        Args:
            video_url: Full YouTube URL
            title: Video title
            transcript: Full transcript text
        """
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
        if not video_id_match:
            print(f"[ERROR] Could not extract video ID from URL: {video_url}")
            return

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


def main():
    """Main execution function"""
    print("="*60)
    print("BroBro Manual YouTube Transcript Embedder")
    print("="*60)
    print()
    print("This tool lets you paste YouTube transcripts manually.")
    print()

    try:
        embedder = ManualTranscriptEmbedder()

        print("\n" + "="*60)
        print("Ready to accept transcripts!")
        print("="*60)
        print()
        print("For each video, provide:")
        print("1. YouTube URL (e.g., https://www.youtube.com/watch?v=abc123)")
        print("2. Video title")
        print("3. Full transcript text")
        print()
        print("Type 'done' when finished, or 'quit' to exit.")
        print("="*60)

        video_count = 0

        while True:
            print(f"\n\n--- VIDEO #{video_count + 1} ---")

            # Get URL
            url = input("\nYouTube URL (or 'done'/'quit'): ").strip()
            if url.lower() in ['done', 'quit', 'exit']:
                break

            if not url:
                print("[ERROR] URL cannot be empty")
                continue

            # Get title
            title = input("Video Title: ").strip()
            if not title:
                print("[ERROR] Title cannot be empty")
                continue

            # Get transcript
            print("\nPaste transcript (press Enter, then Ctrl+Z and Enter on Windows to finish):")
            transcript_lines = []
            try:
                while True:
                    line = input()
                    transcript_lines.append(line)
            except EOFError:
                pass

            transcript = '\n'.join(transcript_lines).strip()

            if not transcript:
                print("[ERROR] Transcript cannot be empty")
                continue

            # Embed the transcript
            embedder.embed_transcript(url, title, transcript)
            video_count += 1

        print("\n" + "="*60)
        print(f"[OK] Processing complete!")
        print(f"Added {video_count} video(s) to knowledge base")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
