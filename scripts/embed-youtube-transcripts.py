"""
YouTube Transcript Scraper and Embedder for BroBro
Scrapes video transcripts from YouTube channels and embeds them into ChromaDB
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
COLLECTION_NAME = "ghl-youtube"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# YouTube channels to scrape
CHANNELS = {
    "jasperhighlevel": "https://www.youtube.com/@jasperhighlevel",
    "highlevelwizard": "https://www.youtube.com/@highlevelwizard"
}

class YouTubeTranscriptScraper:
    def __init__(self):
        """Initialize the scraper with ChromaDB and embedding model"""
        print(">> Initializing YouTube Transcript Scraper...")

        # Initialize ChromaDB client
        self.chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(allow_reset=True)
        )

        # Initialize embedding model
        print(f">> Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
            print(f">> Connected to existing collection: {COLLECTION_NAME}")
            print(f"   Current document count: {self.collection.count()}")
        except Exception:
            print(f">> Creating new collection: {COLLECTION_NAME}")
            self.collection = self.chroma_client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "YouTube video transcripts from GHL experts"}
            )

    def extract_video_id(self, video_data: Dict) -> Optional[str]:
        """Extract video ID from scrapetube video data"""
        try:
            return video_data.get('videoId')
        except Exception:
            return None

    def get_channel_videos(self, channel_handle: str, limit: int = 100) -> List[Dict]:
        """
        Get videos from a YouTube channel

        Args:
            channel_handle: Channel handle (e.g., 'highlevelwizard')
            limit: Maximum number of videos to retrieve

        Returns:
            List of video data dictionaries
        """
        print(f"\n>> Fetching videos from @{channel_handle}...")

        try:
            videos = []
            count = 0

            for video in scrapetube.get_channel(channel_username=channel_handle):
                if count >= limit:
                    break

                video_id = self.extract_video_id(video)
                if video_id:
                    video_info = {
                        'video_id': video_id,
                        'title': video.get('title', {}).get('runs', [{}])[0].get('text', 'Untitled'),
                        'thumbnail': video.get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'channel': channel_handle
                    }
                    videos.append(video_info)
                    count += 1

            print(f"[OK] Found {len(videos)} videos")
            return videos

        except Exception as e:
            print(f"[ERROR] Error fetching channel videos: {e}")
            return []

    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get transcript for a YouTube video

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript text or None if unavailable
        """
        try:
            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['en'])

            # Combine all transcript segments
            full_transcript = " ".join([entry['text'] for entry in transcript_list])

            # Clean up transcript
            full_transcript = re.sub(r'\s+', ' ', full_transcript).strip()

            return full_transcript

        except TranscriptsDisabled:
            return None
        except NoTranscriptFound:
            return None
        except VideoUnavailable:
            return None
        except Exception as e:
            # Try without language specification
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.fetch(video_id)
                full_transcript = " ".join([entry['text'] for entry in transcript_list])
                full_transcript = re.sub(r'\s+', ' ', full_transcript).strip()
                return full_transcript
            except:
                return None

    def chunk_transcript(self, transcript: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split transcript into chunks with overlap for better context

        Args:
            transcript: Full transcript text
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of transcript chunks
        """
        if len(transcript) <= chunk_size:
            return [transcript]

        chunks = []
        start = 0

        while start < len(transcript):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(transcript):
                # Look for period, question mark, or exclamation point
                for punct in ['. ', '? ', '! ']:
                    last_punct = transcript[start:end].rfind(punct)
                    if last_punct > chunk_size * 0.7:  # At least 70% through chunk
                        end = start + last_punct + 1
                        break

            chunk = transcript[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def embed_video(self, video: Dict) -> Dict[str, int]:
        """
        Fetch transcript for a video and embed it into ChromaDB

        Args:
            video: Video information dictionary

        Returns:
            Dictionary with success/failure counts
        """
        video_id = video['video_id']
        title = video['title']

        # Sanitize title for Windows console (remove non-ASCII chars)
        safe_title = title.encode('ascii', 'ignore').decode('ascii')

        print(f"\n>> Processing: {safe_title[:60]}...")

        # Get transcript
        transcript = self.get_transcript(video_id)

        if not transcript:
            print(f"   [SKIP] No transcript available")
            return {'skipped': 1, 'added': 0, 'chunks': 0}

        print(f"   [OK] Transcript fetched ({len(transcript)} chars)")

        # Chunk transcript
        chunks = self.chunk_transcript(transcript)
        print(f"   >> Split into {len(chunks)} chunks")

        # Embed each chunk
        added_count = 0
        for idx, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist()

                # Create unique ID
                doc_id = f"yt_{video_id}_chunk_{idx}"

                # Metadata
                metadata = {
                    "source": "youtube",
                    "video_id": video_id,
                    "title": title,
                    "url": video['url'],
                    "channel": video['channel'],
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "thumbnail": video.get('thumbnail', ''),
                    "scraped_at": datetime.now().isoformat()
                }

                # Add to ChromaDB
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata]
                )

                added_count += 1

            except Exception as e:
                print(f"   [ERROR] Error embedding chunk {idx}: {e}")

        print(f"   [OK] Added {added_count}/{len(chunks)} chunks to database")

        return {'skipped': 0, 'added': 1, 'chunks': added_count}

    def scrape_and_embed_channel(self, channel_handle: str, max_videos: int = 100):
        """
        Scrape all videos from a channel and embed their transcripts

        Args:
            channel_handle: YouTube channel handle
            max_videos: Maximum number of videos to process
        """
        print(f"\n{'='*60}")
        print(f">> SCRAPING CHANNEL: @{channel_handle}")
        print(f"{'='*60}")

        # Get videos
        videos = self.get_channel_videos(channel_handle, limit=max_videos)

        if not videos:
            print("[ERROR] No videos found or error fetching channel")
            return

        # Process each video
        stats = {
            'total': len(videos),
            'added': 0,
            'skipped': 0,
            'chunks': 0
        }

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{stats['total']}]", end=" ")
            result = self.embed_video(video)

            stats['added'] += result['added']
            stats['skipped'] += result['skipped']
            stats['chunks'] += result['chunks']

        # Print summary
        print(f"\n{'='*60}")
        print(f"[OK] SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Total videos processed: {stats['total']}")
        print(f"Videos embedded: {stats['added']}")
        print(f"Videos skipped (no transcript): {stats['skipped']}")
        print(f"Total chunks added: {stats['chunks']}")
        print(f"\nFinal collection size: {self.collection.count()} documents")

def main():
    """Main execution function"""
    print("="*60)
    print("BroBro YouTube Transcript Embedder")
    print("="*60)

    try:
        scraper = YouTubeTranscriptScraper()

        # Scrape highlevelwizard channel
        scraper.scrape_and_embed_channel("highlevelwizard", max_videos=50)

        print("\n[OK] All done! YouTube transcripts are now searchable in BroBro.")

    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
