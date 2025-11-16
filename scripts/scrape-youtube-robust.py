"""
BroBro - Robust YouTube Transcript Scraper
Extracts transcripts from ANY YouTube URL with multiple fallback methods
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import time

# Method 1: youtube-transcript-api
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    HAS_TRANSCRIPT_API = True
except ImportError:
    HAS_TRANSCRIPT_API = False
    print("[WARN] youtube-transcript-api not available")

# Method 2: yt-dlp
try:
    import yt_dlp
    HAS_YT_DLP = True
except ImportError:
    HAS_YT_DLP = False
    print("[WARN] yt-dlp not available")


class RobustYouTubeScraper:
    """
    Multi-method YouTube transcript scraper with fallbacks
    """

    def __init__(self):
        self.output_dir = Path('data/youtube-tutorials')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'([a-zA-Z0-9_-]{11})'  # Fallback: just the ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11:  # YouTube IDs are always 11 chars
                    return video_id

        return None

    def get_transcript_method1(self, video_id: str) -> Optional[Dict]:
        """
        Method 1: Use youtube-transcript-api
        """
        if not HAS_TRANSCRIPT_API:
            return None

        try:
            print(f"  [Method 1] Trying youtube-transcript-api...")

            # Create API instance
            api = YouTubeTranscriptApi()

            # Try to list and fetch transcripts
            transcript_list = api.list(video_id)

            if not transcript_list:
                print(f"  [Method 1] No transcripts available")
                return None

            # Try to find English transcript first
            transcript = None
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                try:
                    # Try to get first available transcript
                    transcript = transcript_list._manually_created_transcripts[0] if transcript_list._manually_created_transcripts else None
                    if not transcript and transcript_list._generated_transcripts:
                        transcript = transcript_list._generated_transcripts[0]
                except:
                    pass

            if not transcript:
                print(f"  [Method 1] Could not select a transcript")
                return None

            # Fetch the transcript data
            transcript_data = transcript.fetch()

            # Extract properties
            language = transcript.language_code
            is_generated = transcript.is_generated

            # Convert snippet objects to dicts and combine text
            entries = []
            full_text_parts = []

            for snippet in transcript_data:
                entry = {
                    'text': snippet.text,
                    'start': snippet.start,
                    'duration': snippet.duration
                }
                entries.append(entry)
                full_text_parts.append(snippet.text)

            full_text = " ".join(full_text_parts)

            # Calculate duration
            duration = 0
            if entries:
                last_entry = entries[-1]
                duration = last_entry['start'] + last_entry['duration']

            return {
                'transcript': full_text,
                'transcript_entries': entries,
                'duration_seconds': duration,
                'language': language,
                'is_generated': is_generated,
                'method': 'youtube-transcript-api'
            }

        except TranscriptsDisabled:
            print(f"  [Method 1] Transcripts are disabled for this video")
        except NoTranscriptFound:
            print(f"  [Method 1] No transcript found")
        except Exception as e:
            print(f"  [Method 1] Failed: {e}")

        return None

    def get_transcript_method2(self, video_id: str) -> Optional[Dict]:
        """
        Method 2: Use yt-dlp to extract subtitles
        """
        if not HAS_YT_DLP:
            return None

        try:
            print(f"  [Method 2] Trying yt-dlp...")

            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'quiet': True,
                'no_warnings': True
            }

            url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Check for subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})

                # Try English subtitles first
                subtitle_data = subtitles.get('en') or automatic_captions.get('en')

                if subtitle_data:
                    # yt-dlp returns subtitle formats, we need to download one
                    # For now, we'll use the JSON format if available
                    for fmt in subtitle_data:
                        if fmt.get('ext') == 'json3':
                            # This would require additional processing
                            # For now, we'll fall back to the next method
                            pass

                print(f"  [Method 2] Subtitles found but extraction not fully implemented")
                return None

        except Exception as e:
            print(f"  [Method 2] Failed: {e}")

        return None

    def get_metadata(self, video_id: str) -> Dict:
        """
        Get video metadata using yt-dlp
        """
        try:
            if not HAS_YT_DLP:
                return {}

            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'no_warnings': True
            }

            url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                return {
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('uploader', 'Unknown Channel'),
                    'channel_id': info.get('channel_id', ''),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', [])
                }
        except Exception as e:
            print(f"  [WARN] Could not fetch metadata: {e}")
            return {}

    def scrape_video(self, url: str) -> Optional[Dict]:
        """
        Scrape a YouTube video using multiple fallback methods
        """
        print(f"\n{'='*70}")
        print(f"Scraping: {url}")
        print(f"{'='*70}")

        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            print(f"[ERROR] Could not extract video ID from URL")
            return None

        print(f"  Video ID: {video_id}")

        # Get metadata first
        print(f"\n>> Fetching video metadata...")
        metadata = self.get_metadata(video_id)

        if metadata:
            print(f"  Title: {metadata.get('title', 'Unknown')}")
            print(f"  Channel: {metadata.get('channel', 'Unknown')}")
            print(f"  Duration: {metadata.get('duration', 0)} seconds")

        # Try multiple methods to get transcript
        transcript_data = None

        # Method 1: youtube-transcript-api (most reliable)
        transcript_data = self.get_transcript_method1(video_id)

        # Method 2: yt-dlp (fallback)
        if not transcript_data:
            transcript_data = self.get_transcript_method2(video_id)

        if not transcript_data:
            print(f"\n[ERROR] Could not extract transcript using any method")
            print(f"  This video may not have captions/transcripts available")
            return None

        # Combine metadata and transcript
        result = {
            'video_id': video_id,
            'url': url,
            **metadata,
            **transcript_data,
            'scraped_date': datetime.now().isoformat(),
            'word_count': len(transcript_data['transcript'].split())
        }

        print(f"\n[SUCCESS] Transcript extracted!")
        print(f"  Method: {transcript_data['method']}")
        print(f"  Word count: {result['word_count']}")
        print(f"  Language: {transcript_data.get('language', 'unknown')}")

        return result

    def save_transcript(self, data: Dict) -> Path:
        """Save transcript data to JSON file"""
        video_id = data['video_id']
        filename = f"youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] {filepath}")
        return filepath

    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple videos"""
        results = []

        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}] Processing: {url}")

            result = self.scrape_video(url)
            if result:
                filepath = self.save_transcript(result)
                results.append(result)

            # Be respectful with rate limiting
            if i < len(urls) - 1:
                time.sleep(2)

        return results


def main():
    if len(sys.argv) < 2:
        print("\nRobust YouTube Transcript Scraper")
        print("="*70)
        print("\nUsage:")
        print("  python scrape-youtube-robust.py <youtube_url>")
        print("  python scrape-youtube-robust.py <url1> <url2> <url3> ...")
        print("\nExamples:")
        print("  python scrape-youtube-robust.py https://www.youtube.com/watch?v=VIDEO_ID")
        print("  python scrape-youtube-robust.py https://youtu.be/VIDEO_ID")
        print("\nSupported URL formats:")
        print("  - https://www.youtube.com/watch?v=VIDEO_ID")
        print("  - https://youtu.be/VIDEO_ID")
        print("  - https://www.youtube.com/embed/VIDEO_ID")
        print("  - VIDEO_ID (just the 11-character ID)")
        sys.exit(1)

    urls = sys.argv[1:]

    scraper = RobustYouTubeScraper()

    print("\n" + "="*70)
    print("BroBro - Robust YouTube Transcript Scraper")
    print("="*70)
    print(f"\nProcessing {len(urls)} video(s)...")

    results = scraper.scrape_multiple(urls)

    print(f"\n{'='*70}")
    print(f"[COMPLETE] Successfully scraped {len(results)}/{len(urls)} videos")
    print(f"{'='*70}")

    if results:
        total_words = sum(r['word_count'] for r in results)
        print(f"\nTotal words extracted: {total_words:,}")
        print(f"Output directory: {scraper.output_dir}")
        print(f"\nNext step: python scripts/embed-youtube-tutorials.py")


if __name__ == "__main__":
    main()
