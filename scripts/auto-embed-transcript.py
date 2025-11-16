"""
BroBro - Auto-Embed YouTube Transcript

Simply paste the transcript - the system will automatically:
1. Detect video ID and URL from timestamps
2. Extract the video title from content
3. Clean and structure the transcript
4. Chunk it properly
5. Embed it into ChromaDB

Usage: Just run the script and paste your transcript!
"""

import sys
import os
import re
from typing import List, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

class AutoTranscriptEmbedder:
    """Auto-detects and embeds YouTube transcripts"""

    def __init__(self):
        """Initialize the embedder"""
        print(">> Initializing Auto-Transcript Embedder...")

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

    def extract_video_id(self, text: str) -> Optional[str]:
        """
        Try to extract video ID from various formats in the transcript
        """
        # Look for YouTube URLs
        url_patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in url_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def extract_title(self, text: str) -> str:
        """
        Try to extract video title from content
        Looks for common title patterns in transcripts
        """
        # Clean text for analysis
        lines = text.split('\n')

        # Look for first substantial line that might be a title
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Skip timestamp lines
            if re.match(r'^\d+:\d+', line):
                continue
            # Skip very short lines
            if len(line) < 20:
                continue
            # If we find a good line, use it
            if len(line) < 200:  # Titles usually aren't too long
                return line

        # Fallback: use first 100 chars
        clean_text = re.sub(r'\d+:\d+\s*', '', text)  # Remove timestamps
        clean_text = clean_text.strip()
        return clean_text[:100] + "..."

    def clean_transcript(self, text: str) -> str:
        """
        Clean the transcript:
        - Remove timestamp markers (0:06, 1:23, etc)
        - Normalize whitespace
        - Keep the actual content
        """
        # Remove timestamps like "0:06" or "12:34"
        cleaned = re.sub(r'\n\d+:\d+\s*\n', ' ', text)
        cleaned = re.sub(r'^\d+:\d+\s*', '', cleaned, flags=re.MULTILINE)

        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

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

    def auto_embed(self, raw_transcript: str, manual_url: Optional[str] = None, manual_title: Optional[str] = None) -> bool:
        """
        Automatically detect, clean, chunk, and embed a transcript
        """
        print("\n" + "="*60)
        print("AUTO-PROCESSING TRANSCRIPT")
        print("="*60)

        # Step 1: Extract or use provided URL
        video_id = None
        if manual_url:
            video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', manual_url)
            if video_id_match:
                video_id = video_id_match.group(1)

        if not video_id:
            video_id = self.extract_video_id(raw_transcript)

        if not video_id:
            # Generate a random ID if we can't find one
            import hashlib
            video_id = hashlib.md5(raw_transcript[:100].encode()).hexdigest()[:11]
            print(f"[WARN] No video ID found - using generated ID: {video_id}")
        else:
            print(f"[OK] Detected video ID: {video_id}")

        # Step 2: Extract or use provided title
        if manual_title:
            title = manual_title
        else:
            title = self.extract_title(raw_transcript)

        # Sanitize title for console
        safe_title = title.encode('ascii', 'ignore').decode('ascii')
        print(f"[OK] Title: {safe_title[:60]}...")

        # Step 3: Clean transcript
        cleaned_transcript = self.clean_transcript(raw_transcript)
        print(f"[OK] Cleaned transcript: {len(cleaned_transcript)} characters")

        # Step 4: Chunk transcript
        chunks = self.chunk_transcript(cleaned_transcript)
        print(f"[OK] Split into {len(chunks)} chunks")

        # Step 5: Embed each chunk
        video_url = f"https://www.youtube.com/watch?v={video_id}"
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
                        'url': video_url,
                        'chunk_index': idx,
                        'total_chunks': len(chunks),
                        'type': 'video_transcript'
                    }]
                )

                added_count += 1

            except Exception as e:
                print(f"[ERROR] Error embedding chunk {idx}: {e}")

        print(f"[OK] Added {added_count}/{len(chunks)} chunks to database")

        # Show updated count
        final_count = self.collection.count()
        print(f"[OK] Collection now has {final_count} total documents")
        print("="*60)

        return True


def main():
    """Main execution function"""
    print("="*60)
    print("BroBro Auto-Transcript Embedder")
    print("="*60)
    print()
    print("This tool automatically processes and embeds transcripts.")
    print("Just paste the transcript and it handles the rest!")
    print()
    print("Optional: You can provide a URL or title first, or just paste")
    print("          the transcript and it will auto-detect everything.")
    print()
    print("="*60)

    try:
        embedder = AutoTranscriptEmbedder()

        print("\n")

        # Ask if they want to provide URL/title or just paste transcript
        print("Options:")
        print("  1. Just paste transcript (auto-detect everything)")
        print("  2. Provide URL and title first")
        print()

        choice = input("Choose option (1 or 2, default=1): ").strip()

        manual_url = None
        manual_title = None

        if choice == "2":
            manual_url = input("\nYouTube URL: ").strip()
            manual_title = input("Video Title: ").strip()

        print("\nPaste transcript below, then press Enter and Ctrl+Z (Windows) or Ctrl+D (Mac/Linux):")
        print("-" * 60)

        # Read multiline input
        transcript_lines = []
        try:
            while True:
                line = input()
                transcript_lines.append(line)
        except EOFError:
            pass

        raw_transcript = '\n'.join(transcript_lines).strip()

        if not raw_transcript:
            print("\n[ERROR] No transcript provided")
            sys.exit(1)

        # Process and embed
        success = embedder.auto_embed(raw_transcript, manual_url, manual_title)

        if success:
            print("\n[OK] Transcript successfully embedded and ready to search!")
        else:
            print("\n[ERROR] Failed to embed transcript")
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
