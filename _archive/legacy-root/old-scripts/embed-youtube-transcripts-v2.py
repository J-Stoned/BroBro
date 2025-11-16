"""
YouTube Transcript Scraper and Embedder for BroBro (v2)
Supports both native transcripts AND Whisper AI transcription fallback
"""

import os
import sys
import json
import re
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
import yt_dlp
import whisper
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
COLLECTION_NAME = "ghl-youtube"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
USE_WHISPER_FALLBACK = True  # Set to True to use Whisper for videos without transcripts
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large

# YouTube channels to scrape
CHANNELS = {
    "highlevelwizard": "https://www.youtube.com/@highlevelwizard"
}

class YouTubeTranscriptScraper:
    def __init__(self, use_whisper=True):
        """Initialize the scraper with ChromaDB and embedding model"""
        print("=" * 60)
        print(">> Initializing YouTube Transcript Scraper v2")
        print("=" * 60)

        self.use_whisper = use_whisper

        # Initialize ChromaDB client
        self.chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(allow_reset=True)
        )

        # Initialize embedding model
        print(f">> Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Initialize Whisper if enabled
        if self.use_whisper:
            print(f">> Loading Whisper model: {WHISPER_MODEL}")
            print("   (This may take a minute on first run...)")
            self.whisper_model = whisper.load_model(WHISPER_MODEL)
            print("   >> Whisper loaded successfully!")
        else:
            self.whisper_model = None

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

        # Create temp directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        print(f">> Temp directory: {self.temp_dir}")

    def extract_video_id(self, video_data: Dict) -> Optional[str]:
        """Extract video ID from scrapetube video data"""
        try:
            return video_data.get('videoId')
        except Exception:
            return None

    def get_channel_videos(self, channel_handle: str, limit: int = 100) -> List[Dict]:
        """Get videos from a YouTube channel"""
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

            print(f"   >> Found {len(videos)} videos")
            return videos

        except Exception as e:
            print(f"   >> Error fetching channel videos: {e}")
            return []

    def get_native_transcript(self, video_id: str) -> Optional[str]:
        """Try to get native YouTube transcript"""
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            full_transcript = " ".join([entry['text'] for entry in transcript_list])
            full_transcript = re.sub(r'\s+', ' ', full_transcript).strip()
            return full_transcript
        except:
            return None

    def download_audio(self, video_url: str, video_id: str) -> Optional[str]:
        """Download audio from YouTube video"""
        try:
            output_path = os.path.join(self.temp_dir, f"{video_id}.mp3")

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.temp_dir, f"{video_id}.%(ext)s"),
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            if os.path.exists(output_path):
                return output_path
            return None

        except Exception as e:
            print(f"   >> Error downloading audio: {e}")
            return None

    def transcribe_with_whisper(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file using Whisper"""
        try:
            result = self.whisper_model.transcribe(audio_path)
            transcript = result.get('text', '').strip()
            return transcript if transcript else None
        except Exception as e:
            print(f"   >> Error transcribing: {e}")
            return None
        finally:
            # Clean up audio file
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

    def get_transcript(self, video_id: str, video_url: str, use_whisper_fallback: bool = True) -> tuple[Optional[str], str]:
        """
        Get transcript using native method first, then Whisper fallback

        Returns:
            tuple: (transcript_text, method_used)
        """
        # Try native transcript first
        transcript = self.get_native_transcript(video_id)
        if transcript:
            return transcript, "native"

        # Fallback to Whisper if enabled
        if use_whisper_fallback and self.use_whisper and self.whisper_model:
            print(f"   >> No native transcript - using Whisper AI...")

            # Download audio
            audio_path = self.download_audio(video_url, video_id)
            if not audio_path:
                return None, "failed_download"

            # Transcribe
            transcript = self.transcribe_with_whisper(audio_path)
            if transcript:
                return transcript, "whisper"

        return None, "unavailable"

    def chunk_transcript(self, transcript: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split transcript into chunks with overlap"""
        if len(transcript) <= chunk_size:
            return [transcript]

        chunks = []
        start = 0

        while start < len(transcript):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(transcript):
                for punct in ['. ', '? ', '! ']:
                    last_punct = transcript[start:end].rfind(punct)
                    if last_punct > chunk_size * 0.7:
                        end = start + last_punct + 1
                        break

            chunk = transcript[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def embed_video(self, video: Dict, use_whisper: bool = True) -> Dict[str, int]:
        """Fetch transcript for a video and embed it into ChromaDB"""
        video_id = video['video_id']
        title = video['title']

        print(f"\n>> Processing: {title[:60]}...")

        # Get transcript
        transcript, method = self.get_transcript(video_id, video['url'], use_whisper)

        if not transcript:
            print(f"   >> Skipped - No transcript available")
            return {'skipped': 1, 'added': 0, 'chunks': 0, 'native': 0, 'whisper': 0}

        print(f"   >> Transcript obtained via {method.upper()} ({len(transcript)} chars)")

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
                    "transcription_method": method,
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
                print(f"   >> Error embedding chunk {idx}: {e}")

        print(f"   >> Added {added_count}/{len(chunks)} chunks to database")

        result = {
            'skipped': 0,
            'added': 1,
            'chunks': added_count,
            'native': 1 if method == 'native' else 0,
            'whisper': 1 if method == 'whisper' else 0
        }

        return result

    def scrape_and_embed_channel(self, channel_handle: str, max_videos: int = 100, use_whisper: bool = True):
        """Scrape all videos from a channel and embed their transcripts"""
        print(f"\n{'='*60}")
        print(f">> SCRAPING CHANNEL: @{channel_handle}")
        print(f"{'='*60}")

        # Get videos
        videos = self.get_channel_videos(channel_handle, limit=max_videos)

        if not videos:
            print(">> No videos found or error fetching channel")
            return

        # Process each video
        stats = {
            'total': len(videos),
            'added': 0,
            'skipped': 0,
            'chunks': 0,
            'native_transcripts': 0,
            'whisper_transcripts': 0
        }

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{stats['total']}]", end=" ")
            result = self.embed_video(video, use_whisper=use_whisper)

            stats['added'] += result['added']
            stats['skipped'] += result['skipped']
            stats['chunks'] += result['chunks']
            stats['native_transcripts'] += result['native']
            stats['whisper_transcripts'] += result['whisper']

        # Print summary
        print(f"\n{'='*60}")
        print(f">> SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Total videos processed: {stats['total']}")
        print(f"Videos embedded: {stats['added']}")
        print(f"  - Native transcripts: {stats['native_transcripts']}")
        print(f"  - Whisper transcripts: {stats['whisper_transcripts']}")
        print(f"Videos skipped: {stats['skipped']}")
        print(f"Total chunks added: {stats['chunks']}")
        print(f"\nFinal collection size: {self.collection.count()} documents")

def main():
    """Main execution function"""
    print("="*60)
    print("BroBro YouTube Transcript Embedder v2")
    print("Supports native transcripts + Whisper AI fallback")
    print("="*60)

    try:
        scraper = YouTubeTranscriptScraper(use_whisper=USE_WHISPER_FALLBACK)

        # Scrape highlevelwizard channel (will use Whisper since no native transcripts)
        scraper.scrape_and_embed_channel(
            "highlevelwizard",
            max_videos=5,  # Start with just 5 videos to test
            use_whisper=USE_WHISPER_FALLBACK
        )

        print("\n>> All done! YouTube transcripts are now searchable in BroBro.")

    except Exception as e:
        print(f"\n>> Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
