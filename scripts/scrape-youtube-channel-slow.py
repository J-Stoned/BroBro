"""
BroBro - YouTube Channel Scraper (SLOW RATE)
Extracts all video URLs from a YouTube channel and scrapes their transcripts
USES 10-15 SECOND DELAYS TO AVOID IP RATE LIMITING
"""

import sys
import json
import time
import yt_dlp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess

class YouTubeChannelScraperSlow:
    """Scrapes all videos from a YouTube channel with slow rate limiting"""

    def __init__(self, delay_seconds: int = 10):
        self.output_dir = Path('data/youtube-tutorials')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay_seconds = delay_seconds

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
        Scrape a single video using the robust scraper v2 script
        """
        try:
            # Call the robust scraper v2 script (with yt-dlp fallback)
            result = subprocess.run(
                ['python', 'scripts/scrape-youtube-robust-v2.py', video_url],
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

    def get_existing_video_ids(self) -> set:
        """Get list of already scraped video IDs"""
        existing_ids = set()
        for file in self.output_dir.glob('youtube_*.json'):
            # Extract video ID from filename: youtube_VIDEO_ID_timestamp.json
            parts = file.stem.split('_')
            if len(parts) >= 2:
                video_id = parts[1]
                existing_ids.add(video_id)
        return existing_ids

    def scrape_channel(self, channel_url: str, max_videos: Optional[int] = None,
                       skip_existing: bool = True) -> Dict:
        """
        Scrape all videos from a channel with slow rate limiting
        """
        print("\n" + "="*70)
        print("BroBro - YouTube Channel Scraper (SLOW RATE)")
        print("="*70)
        print(f"Rate Limiting: {self.delay_seconds} seconds between requests")
        print("="*70)

        # Get all video URLs
        video_urls = self.get_channel_videos(channel_url, max_videos)

        if not video_urls:
            print("\n[ERROR] No videos to scrape")
            return {'success': 0, 'failed': 0, 'skipped': 0, 'total': 0}

        # Check for existing videos
        skipped_count = 0
        if skip_existing:
            existing_ids = self.get_existing_video_ids()
            print(f"\n>> Found {len(existing_ids)} already scraped videos")

            # Filter out existing videos
            filtered_urls = []
            for url in video_urls:
                # Extract video ID from URL
                if 'watch?v=' in url:
                    video_id = url.split('watch?v=')[1].split('&')[0]
                    if video_id not in existing_ids:
                        filtered_urls.append(url)
                    else:
                        skipped_count += 1
                else:
                    filtered_urls.append(url)

            video_urls = filtered_urls
            print(f">> Skipping {skipped_count} already scraped videos")
            print(f">> {len(video_urls)} videos remaining to scrape")

        if not video_urls:
            print("\n[INFO] All videos already scraped!")
            return {'success': 0, 'failed': 0, 'skipped': skipped_count, 'total': skipped_count}

        # Scrape each video
        print(f"\n{'='*70}")
        print(f"Scraping {len(video_urls)} videos...")
        print(f"{'='*70}")

        # Calculate ETA
        total_time_seconds = len(video_urls) * self.delay_seconds
        eta_minutes = total_time_seconds / 60
        print(f"\nEstimated time: {eta_minutes:.1f} minutes ({eta_minutes/60:.1f} hours)")
        print(f"{'='*70}\n")

        success_count = 0
        failed_count = 0
        start_time = time.time()

        for i, video_url in enumerate(video_urls):
            elapsed = time.time() - start_time
            elapsed_mins = elapsed / 60

            # Calculate progress
            progress_pct = (i / len(video_urls)) * 100

            print(f"\n[{i+1}/{len(video_urls)}] ({progress_pct:.1f}%) | Elapsed: {elapsed_mins:.1f}m")
            print(f"{video_url}")

            if self.scrape_video(video_url):
                success_count += 1
                print(f"   [OK] Successfully scraped")
            else:
                failed_count += 1
                print(f"   [FAILED] Could not scrape transcript")

            # Rate limiting (slow!)
            if i < len(video_urls) - 1:
                print(f"   [RATE LIMIT] Waiting {self.delay_seconds} seconds...")
                time.sleep(self.delay_seconds)

        return {
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'total': len(video_urls) + skipped_count
        }


def main():
    if len(sys.argv) < 2:
        print("\nYouTube Channel Scraper (SLOW RATE)")
        print("="*70)
        print("Uses 10-15 second delays to avoid YouTube IP rate limiting")
        print("\nUsage:")
        print("  python scrape-youtube-channel-slow.py <channel_url> [max_videos] [delay_seconds]")
        print("\nExamples:")
        print("  python scrape-youtube-channel-slow.py https://www.youtube.com/@gohighlevel/videos")
        print("  python scrape-youtube-channel-slow.py https://www.youtube.com/@gohighlevel/videos 50")
        print("  python scrape-youtube-channel-slow.py https://www.youtube.com/@gohighlevel/videos 1000 15")
        print("\nParameters:")
        print("  channel_url    : YouTube channel URL (must end with /videos)")
        print("  max_videos     : Maximum number of videos to scrape (optional, default: all)")
        print("  delay_seconds  : Seconds to wait between requests (optional, default: 10)")
        print("\nSupported formats:")
        print("  - https://www.youtube.com/@username/videos")
        print("  - https://www.youtube.com/c/channelname/videos")
        print("  - https://www.youtube.com/channel/CHANNEL_ID/videos")
        print("\nNOTE: Always add /videos to the end of the channel URL!")
        sys.exit(1)

    channel_url = sys.argv[1]
    max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else None
    delay_seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    scraper = YouTubeChannelScraperSlow(delay_seconds=delay_seconds)
    results = scraper.scrape_channel(channel_url, max_videos)

    print(f"\n{'='*70}")
    print("SCRAPING COMPLETE")
    print(f"{'='*70}")
    print(f"  Successfully scraped: {results['success']}/{results['total']} videos")
    print(f"  Failed: {results['failed']}/{results['total']} videos")
    print(f"  Skipped (already scraped): {results['skipped']}/{results['total']} videos")
    print(f"{'='*70}")
    print(f"\nOutput directory: {scraper.output_dir}")
    print(f"\nNext step: python scripts/embed-youtube-tutorials.py data/youtube-tutorials/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
