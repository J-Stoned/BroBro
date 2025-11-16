"""
BroBro - Single YouTube Transcript Embedder
Embeds a single YouTube transcript into the knowledge base (non-interactive)
"""

import sys
import os
import re
from typing import List
import chromadb
from sentence_transformers import SentenceTransformer

class SingleTranscriptEmbedder:
    """Embeds a single YouTube transcript into ChromaDB"""

    def __init__(self):
        """Initialize the embedder"""
        print(">> Initializing Single Transcript Embedder...")

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
            video_url: Full YouTube URL or placeholder
            title: Video title
            transcript: Full transcript text
        """
        # Extract video ID from URL or generate placeholder
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
        if video_id_match:
            video_id = video_id_match.group(1)
        else:
            # Generate a placeholder video ID from title
            import hashlib
            video_id = hashlib.md5(title.encode()).hexdigest()[:11]
            print(f"[INFO] Generated placeholder video ID: {video_id}")

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

        print(f"   SUCCESS: Added {added_count}/{len(chunks)} chunks to database")

        # Show updated count
        final_count = self.collection.count()
        print(f"\n   Collection now has {final_count} total documents")

        return True


def main():
    """Main execution function"""
    print("="*80)
    print("BroBro Single YouTube Transcript Embedder")
    print("="*80)
    print()

    if len(sys.argv) != 4:
        print("Usage: python embed-single-transcript.py <youtube_url> <title> <transcript_file>")
        print()
        print("Arguments:")
        print("  youtube_url      : YouTube video URL")
        print("  title            : Video title")
        print("  transcript_file  : Path to text file containing transcript")
        print()
        sys.exit(1)

    video_url = sys.argv[1]
    title = sys.argv[2]
    transcript_file = sys.argv[3]

    # Read transcript from file
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
    except Exception as e:
        print(f"[ERROR] Could not read transcript file: {e}")
        sys.exit(1)

    # Initialize embedder
    try:
        embedder = SingleTranscriptEmbedder()

        # Embed the transcript
        success = embedder.embed_transcript(video_url, title, transcript)

        if success:
            print("\n" + "="*80)
            print("SUCCESS: Transcript embedded into knowledge base!")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("FAILED: Could not embed transcript")
            print("="*80)
            sys.exit(1)

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
