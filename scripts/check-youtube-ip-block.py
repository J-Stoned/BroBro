"""
BroBro - YouTube IP Block Checker
Checks if YouTube has lifted the IP rate limit block
"""

import time
from datetime import datetime

# Test with a simple video
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video

def check_youtube_access():
    """
    Test if YouTube API access is working
    Returns: (is_working, method, message)
    """

    # Method 1: Try youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        transcript_list = api.list("jNQXAC9IVRw")

        if transcript_list:
            return (True, "youtube-transcript-api", "Access working!")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Too Many Requests" in error_msg:
            return (False, "youtube-transcript-api", "Still blocked (429)")
        elif "blocking requests from your IP" in error_msg:
            return (False, "youtube-transcript-api", "Still blocked (IP ban)")
        else:
            return (False, "youtube-transcript-api", f"Error: {error_msg[:50]}...")

    # Method 2: Try yt-dlp
    try:
        import yt_dlp

        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(TEST_VIDEO_URL, download=False)

            if info:
                return (True, "yt-dlp", "Access working!")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Too Many Requests" in error_msg:
            return (False, "yt-dlp", "Still blocked (429)")
        else:
            return (False, "yt-dlp", f"Error: {error_msg[:50]}...")

    return (False, "both", "Both methods failed")


def monitor_youtube_access(check_interval_seconds: int = 60, max_checks: int = 60):
    """
    Monitor YouTube access and notify when it's back
    """
    print("="*70)
    print("BroBro - YouTube IP Block Checker")
    print("="*70)
    print(f"\nTest video: {TEST_VIDEO_URL}")
    print(f"Check interval: {check_interval_seconds} seconds")
    print(f"Max checks: {max_checks}")
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\nPress Ctrl+C to stop monitoring\n")

    check_count = 0

    try:
        while check_count < max_checks:
            check_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')

            print(f"[{timestamp}] Check #{check_count}/{max_checks}...", end=" ")

            is_working, method, message = check_youtube_access()

            if is_working:
                print(f"\n\n{'='*70}")
                print("[OK] YOUTUBE ACCESS RESTORED!")
                print("="*70)
                print(f"Method: {method}")
                print(f"Message: {message}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                print("\nYou can now resume scraping!")
                print("\nRun this command:")
                print("  python scripts/scrape-youtube-channel-slow.py https://www.youtube.com/@gohighlevel/videos")
                print("="*70)
                return True
            else:
                print(f"[X] {method}: {message}")

            # Wait before next check
            if check_count < max_checks:
                time.sleep(check_interval_seconds)

    except KeyboardInterrupt:
        print("\n\n[INFO] Monitoring stopped by user")
        print(f"Total checks performed: {check_count}")
        return False

    print("\n\n[INFO] Reached maximum number of checks")
    print("YouTube access still blocked. Try again later.")
    return False


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("\nYouTube IP Block Checker")
        print("="*70)
        print("\nUsage:")
        print("  python check-youtube-ip-block.py [check_interval] [max_checks]")
        print("\nExamples:")
        print("  python check-youtube-ip-block.py              # Check every 60 seconds, up to 60 times")
        print("  python check-youtube-ip-block.py 120          # Check every 2 minutes")
        print("  python check-youtube-ip-block.py 300 30       # Check every 5 minutes, up to 30 times")
        print("\nParameters:")
        print("  check_interval : Seconds between checks (default: 60)")
        print("  max_checks     : Maximum number of checks (default: 60)")
        print("\nThis script tests YouTube API access to detect when the IP block is lifted.")
        sys.exit(0)

    check_interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    max_checks = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    monitor_youtube_access(check_interval, max_checks)


if __name__ == "__main__":
    main()
