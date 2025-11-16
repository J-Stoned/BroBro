"""
BroBro - YouTube Channel Scraper
Extracts all video URLs from a YouTube channel and scrapes their transcripts
"""

import sys
import json
import time
import yt_dlp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess

class YouTubeChannelScraper:
    """Scrapes all videos from a YouTube channel"""

    def __init__(self):
        self.output_dir = Path('data/youtube-tutorials')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_channel_videos(self, channel_url: str, max_videos: Optional[int] = None) -> List[str]:
        """
        Get all video URLs from a YouTube channel
        """
        print(f"\n{'='*70}")
        print(f"Extracting videos from channel: {channel_url}")
        print(f"{'='*70}")

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get info
                'skip_download': True,
            }

            if max_videos:
                ydl_opts['playlistend'] = max_videos
                print(f">> Limiting to first {max_videos} videos")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(">> Fetching channel video list...")

                # Extract channel info
                info = ydl.extract_info(channel_url, download=False)

                if not info:
                    print("[ERROR] Could not fetch channel information")
                    return []

                # Get channel name
                channel_name = info.get('channel', info.get('uploader', 'Unknown Channel'))
                print(f"   Channel: {channel_name}")

                # Get video entries
                entries = info.get('entries', [])

                if not entries:
                    print("[ERROR] No videos found in channel")
                    return []

                print(f"   Found {len(entries)} videos")

                # Extract video URLs
                video_urls = []
                for entry in entries:
                    # Try multiple ways to get the URL/ID
                    video_url = entry.get('url')
                    video_id = entry.get('id')

                    if video_url and 'youtube.com' in video_url:
                        video_urls.append(video_url)
                    elif video_id and len(video_id) == 11:  # Valid YouTube video ID
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        video_urls.append(video_url)
                    elif video_url:
                        # Might be a relative URL
                        if video_url.startswith('/watch'):
                            video_url = f"https://www.youtube.com{video_url}"
                            video_urls.append(video_url)

                print(f"[OK] Extracted {len(video_urls)} video URLs")
                return video_urls

        except Exception as e:
            print(f"[ERROR] Failed to extract channel videos: {e}")
            return []

    def scrape_video(self, video_url: str) -> bool:
        """
        Scrape a single video using the robust scraper script
        """
        try:
            # Call the robust scraper script
            result = subprocess.run(
                ['python', 'scripts/scrape-youtube-robust.py', video_url],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Check if successful
            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                return True
            else:
                return False

        except Exception as e:
            print(f"   [ERROR] Failed to scrape: {e}")
            return False

    def scrape_channel(self, channel_url: str, max_videos: Optional[int] = None,
                       delay_seconds: int = 2) -> Dict:
        """
        Scrape all videos from a channel
        """
        print("\n" + "="*70)
        print("BroBro - YouTube Channel Scraper")
        print("="*70)

        # Get all video URLs
        video_urls = self.get_channel_videos(channel_url, max_videos)

        if not video_urls:
            print("\n[ERROR] No videos to scrape")
            return {'success': 0, 'failed': 0, 'total': 0}

        # Scrape each video
        print(f"\n{'='*70}")
        print(f"Scraping {len(video_urls)} videos...")
        print(f"{'='*70}")

        success_count = 0
        failed_count = 0

        for i, video_url in enumerate(video_urls):
            print(f"\n[{i+1}/{len(video_urls)}] {video_url}")

            if self.scrape_video(video_url):
                success_count += 1
                print(f"   [OK] Successfully scraped")
            else:
                failed_count += 1
                print(f"   [FAILED] Could not scrape transcript")

            # Rate limiting
            if i < len(video_urls) - 1:
                print(f"   Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)

        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(video_urls)
        }


def main():
    if len(sys.argv) < 2:
        print("\nYouTube Channel Scraper")
        print("="*70)
        print("\nUsage:")
        print("  python scrape-youtube-channel.py <channel_url> [max_videos]")
        print("\nExamples:")
        print("  python scrape-youtube-channel.py https://www.youtube.com/@gohighlevel")
        print("  python scrape-youtube-channel.py https://www.youtube.com/@gohighlevel 50")
        print("\nSupported formats:")
        print("  - https://www.youtube.com/@username")
        print("  - https://www.youtube.com/c/channelname")
        print("  - https://www.youtube.com/channel/CHANNEL_ID")
        sys.exit(1)

    channel_url = sys.argv[1]
    max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else None

    scraper = YouTubeChannelScraper()
    results = scraper.scrape_channel(channel_url, max_videos)

    print(f"\n{'='*70}")
    print("SCRAPING COMPLETE")
    print(f"{'='*70}")
    print(f"  Successfully scraped: {results['success']}/{results['total']} videos")
    print(f"  Failed: {results['failed']}/{results['total']} videos")
    print(f"{'='*70}")
    print(f"\nOutput directory: {scraper.output_dir}")
    print(f"\nNext step: python scripts/embed-youtube-tutorials.py data/youtube-tutorials/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
