"""
BroBro - YouTube Transcript Scraper using Playwright
Bypasses API rate limits by scraping transcripts directly from YouTube UI
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import re

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("[ERROR] Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class PlaywrightYouTubeScraper:
    """Scrapes YouTube transcripts using browser automation"""

    def __init__(self, headless: bool = True):
        self.output_dir = Path('data/youtube-tutorials')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11:
                    return video_id
        return None

    def scrape_video(self, url: str) -> Optional[Dict]:
        """
        Scrape a YouTube video transcript using Playwright
        """
        print(f"\n{'='*70}")
        print(f"Scraping: {url}")
        print(f"{'='*70}")

        video_id = self.extract_video_id(url)
        if not video_id:
            print("[ERROR] Could not extract video ID")
            return None

        print(f"  Video ID: {video_id}")

        try:
            with sync_playwright() as p:
                # Launch browser
                print("  >> Launching browser...")
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Navigate to video
                print(f"  >> Loading video page...")
                page.goto(url, wait_until='domcontentloaded', timeout=30000)

                # Wait for page to load
                time.sleep(3)

                # Get video title
                title = "Unknown Title"
                try:
                    title_element = page.query_selector('h1.ytd-video-primary-info-renderer')
                    if not title_element:
                        title_element = page.query_selector('h1 yt-formatted-string')
                    if title_element:
                        title = title_element.inner_text().strip()
                except:
                    pass

                print(f"  Title: {title}")

                # Get channel name
                channel = "Unknown Channel"
                try:
                    channel_element = page.query_selector('ytd-channel-name a')
                    if channel_element:
                        channel = channel_element.inner_text().strip()
                except:
                    pass

                print(f"  Channel: {channel}")

                # First, expand the description to reveal transcript button
                print("  >> Expanding description...")
                try:
                    # Click "Show more" button in description
                    show_more_selectors = [
                        'tp-yt-paper-button#expand',
                        'ytd-text-inline-expander button',
                        '#description-inline-expander button'
                    ]

                    for selector in show_more_selectors:
                        try:
                            show_more_button = page.query_selector(selector)
                            if show_more_button and show_more_button.is_visible():
                                show_more_button.click()
                                time.sleep(2)
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"  [WARN] Could not expand description: {e}")

                # Click on "Show transcript" button
                print("  >> Looking for transcript button...")

                # Try clicking the three-dot menu first to access transcript
                try:
                    # Find and click the "more actions" menu button
                    more_actions = page.query_selector('#top-level-buttons-computed ytd-menu-renderer button[aria-label*="More"]')
                    if more_actions and more_actions.is_visible():
                        print("  >> Opening more actions menu...")
                        more_actions.click()
                        time.sleep(1)

                        # Click "Show transcript" option in menu
                        transcript_menu_item = page.query_selector('ytd-menu-service-item-renderer:has-text("Show transcript")')
                        if transcript_menu_item:
                            print("  >> Clicking 'Show transcript' from menu...")
                            transcript_menu_item.click()
                            time.sleep(2)
                        else:
                            print("  [WARN] Could not find transcript option in menu")
                            browser.close()
                            return None
                    else:
                        print("  [ERROR] Could not find more actions button")
                        browser.close()
                        return None
                except Exception as e:
                    print(f"  [ERROR] Failed to access transcript: {e}")
                    browser.close()
                    return None

                # Wait for transcript panel to load
                print("  >> Waiting for transcript to load...")
                try:
                    page.wait_for_selector('ytd-transcript-segment-renderer', timeout=10000)
                except PlaywrightTimeoutError:
                    print("  [ERROR] Transcript did not load")
                    browser.close()
                    return None

                # Extract transcript segments
                print("  >> Extracting transcript...")
                segments = page.query_selector_all('ytd-transcript-segment-renderer')

                if not segments:
                    print("  [ERROR] No transcript segments found")
                    browser.close()
                    return None

                transcript_entries = []
                full_text_parts = []

                for segment in segments:
                    try:
                        # Get timestamp
                        timestamp_element = segment.query_selector('.segment-timestamp')
                        timestamp_text = timestamp_element.inner_text().strip() if timestamp_element else "0:00"

                        # Convert timestamp to seconds
                        time_parts = timestamp_text.split(':')
                        if len(time_parts) == 2:  # MM:SS
                            start_seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                        elif len(time_parts) == 3:  # HH:MM:SS
                            start_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        else:
                            start_seconds = 0

                        # Get text
                        text_element = segment.query_selector('.segment-text')
                        text = text_element.inner_text().strip() if text_element else ""

                        if text:
                            entry = {
                                'text': text,
                                'start': start_seconds,
                                'duration': 0  # Duration not available from UI
                            }
                            transcript_entries.append(entry)
                            full_text_parts.append(text)

                    except Exception as e:
                        print(f"  [WARN] Error parsing segment: {e}")
                        continue

                browser.close()

                if not transcript_entries:
                    print("  [ERROR] No transcript text extracted")
                    return None

                full_text = " ".join(full_text_parts)

                result = {
                    'video_id': video_id,
                    'url': url,
                    'title': title,
                    'channel': channel,
                    'transcript': full_text,
                    'transcript_entries': transcript_entries,
                    'word_count': len(full_text.split()),
                    'language': 'en',
                    'is_generated': True,  # Assume auto-generated
                    'method': 'playwright-ui-scraping',
                    'scraped_date': datetime.now().isoformat()
                }

                print(f"\n[SUCCESS] Transcript extracted!")
                print(f"  Method: Playwright (UI scraping)")
                print(f"  Word count: {result['word_count']}")
                print(f"  Segments: {len(transcript_entries)}")

                return result

        except Exception as e:
            print(f"\n[ERROR] Failed to scrape: {e}")
            return None

    def save_transcript(self, data: Dict) -> Path:
        """Save transcript data to JSON file"""
        video_id = data['video_id']
        filename = f"youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] {filepath}")
        return filepath

    def scrape_multiple(self, urls: List[str], delay_seconds: int = 5) -> List[Dict]:
        """Scrape multiple videos"""
        results = []

        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}] Processing: {url}")

            result = self.scrape_video(url)
            if result:
                filepath = self.save_transcript(result)
                results.append(result)
            else:
                print(f"  [FAILED] Could not scrape transcript")

            # Rate limiting
            if i < len(urls) - 1:
                print(f"  Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)

        return results


def main():
    if len(sys.argv) < 2:
        print("\nPlaywright YouTube Transcript Scraper")
        print("="*70)
        print("Bypasses API rate limits by scraping transcripts from YouTube UI")
        print("\nUsage:")
        print("  python scrape-youtube-playwright.py <youtube_url> [youtube_url2] ...")
        print("\nExamples:")
        print("  python scrape-youtube-playwright.py https://www.youtube.com/watch?v=VIDEO_ID")
        print("  python scrape-youtube-playwright.py https://www.youtube.com/watch?v=ID1 https://www.youtube.com/watch?v=ID2")
        print("\nOptions:")
        print("  --visible    Show browser window (default: headless)")
        sys.exit(1)

    # Parse arguments
    urls = []
    headless = True

    for arg in sys.argv[1:]:
        if arg == '--visible':
            headless = False
        else:
            urls.append(arg)

    if not urls:
        print("[ERROR] No URLs provided")
        sys.exit(1)

    scraper = PlaywrightYouTubeScraper(headless=headless)

    print("\n" + "="*70)
    print("BroBro - Playwright YouTube Transcript Scraper")
    print("="*70)
    print(f"Mode: {'Headless' if headless else 'Visible browser'}")
    print(f"Processing {len(urls)} video(s)...")

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
