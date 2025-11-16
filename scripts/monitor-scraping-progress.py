"""
BroBro - Scraping Progress Monitor
Real-time monitoring of YouTube channel scraping progress
"""

import time
import os
from pathlib import Path
from datetime import datetime
import json

def monitor_progress():
    """Monitor scraping progress in real-time"""

    output_dir = Path('data/youtube-tutorials')

    print("\n" + "="*70)
    print("BroBro - Scraping Progress Monitor")
    print("="*70)
    print("\nMonitoring: data/youtube-tutorials/")
    print("Press Ctrl+C to stop monitoring\n")

    last_count = 0
    start_time = time.time()

    try:
        while True:
            # Count JSON files (scraped videos)
            if output_dir.exists():
                json_files = list(output_dir.glob('youtube_*.json'))
                current_count = len(json_files)

                # Calculate stats
                elapsed = time.time() - start_time
                elapsed_mins = elapsed / 60

                if current_count > last_count:
                    new_videos = current_count - last_count
                    last_count = current_count

                    # Estimate remaining time
                    if elapsed > 0 and current_count > 0:
                        rate = current_count / elapsed_mins  # videos per minute

                        # Estimate total (assume 1700)
                        estimated_total = 1700
                        remaining = estimated_total - current_count
                        eta_mins = remaining / rate if rate > 0 else 0
                    else:
                        rate = 0
                        eta_mins = 0

                # Display progress
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Videos Scraped: {current_count:>4} | "
                      f"Rate: {rate:.1f}/min | "
                      f"Elapsed: {elapsed_mins:.1f}m | "
                      f"ETA: {eta_mins:.0f}m")

                # Show latest video
                if json_files:
                    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            title = data.get('title', 'Unknown')[:60]
                            print(f"           Latest: {title}...")
                    except:
                        pass

            time.sleep(10)  # Update every 10 seconds

    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("Monitoring stopped")
        print(f"{'='*70}")
        print(f"\nFinal count: {last_count} videos scraped")
        print(f"Total time: {elapsed_mins:.1f} minutes")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    monitor_progress()
