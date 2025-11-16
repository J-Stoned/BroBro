"""Quick progress checker for YouTube scraping"""
import os
from pathlib import Path
from datetime import datetime

output_dir = Path('data/youtube-tutorials')
files = list(output_dir.glob('youtube_*.json'))

print(f"\n{'='*70}")
print(f"YouTube Scraping Progress - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")
print(f"Total videos scraped: {len(files)}")

if files:
    # Get latest file
    latest_file = max(files, key=os.path.getmtime)
    latest_time = datetime.fromtimestamp(os.path.getmtime(latest_file))

    print(f"Latest file: {latest_file.name}")
    print(f"Last scraped: {latest_time.strftime('%H:%M:%S')}")

    # Calculate rate
    first_file = min(files, key=os.path.getmtime)
    first_time = datetime.fromtimestamp(os.path.getmtime(first_file))
    elapsed_minutes = (latest_time - first_time).total_seconds() / 60

    if elapsed_minutes > 0:
        rate = len(files) / elapsed_minutes
        print(f"Scraping rate: {rate:.2f} videos/minute")

        remaining = 1700 - len(files)
        eta_minutes = remaining / rate if rate > 0 else 0
        print(f"Estimated remaining: {remaining} videos")
        print(f"ETA: {eta_minutes:.0f} minutes ({eta_minutes/60:.1f} hours)")

print(f"{'='*70}\n")
