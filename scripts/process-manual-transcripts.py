"""
BroBro - Manual YouTube Transcript Processor
Processes transcripts copied manually from YouTube
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ManualTranscriptProcessor:
    """Process manually copied YouTube transcripts"""

    def __init__(self):
        self.output_dir = Path('data/youtube-tutorials')
        self.manual_dir = Path('data/manual-transcripts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manual_dir.mkdir(parents=True, exist_ok=True)

    def extract_video_id_from_url(self, url: str) -> Optional[str]:
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

    def parse_transcript_with_timestamps(self, transcript_text: str) -> List[Dict]:
        """
        Parse transcript text that includes timestamps
        Format examples:
        - 0:00 Some text here
        - 1:23 More text
        - 12:34 Even more text
        """
        entries = []
        lines = transcript_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to match timestamp at start of line
            # Formats: 0:00, 1:23, 12:34, 1:23:45
            timestamp_match = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?\s+(.+)', line)

            if timestamp_match:
                minutes = int(timestamp_match.group(1))
                seconds = int(timestamp_match.group(2))
                hours = int(timestamp_match.group(3)) if timestamp_match.group(3) else 0
                text = timestamp_match.group(4).strip()

                # Convert to total seconds
                start_seconds = hours * 3600 + minutes * 60 + seconds

                entries.append({
                    'text': text,
                    'start': start_seconds,
                    'duration': 0
                })
            else:
                # If no timestamp, append to previous entry or create new one
                if entries:
                    entries[-1]['text'] += ' ' + line
                else:
                    entries.append({
                        'text': line,
                        'start': 0,
                        'duration': 0
                    })

        return entries

    def parse_transcript_plain(self, transcript_text: str) -> List[Dict]:
        """
        Parse plain transcript text without timestamps
        Creates a single entry
        """
        text = transcript_text.strip()
        if not text:
            return []

        return [{
            'text': text,
            'start': 0,
            'duration': 0
        }]

    def process_transcript_file(self, filepath: Path) -> Optional[Dict]:
        """
        Process a manually saved transcript file
        Expected format: Plain text file with transcript
        Filename should be: VIDEO_ID.txt or VIDEO_URL.txt
        """
        print(f"\n{'='*70}")
        print(f"Processing: {filepath.name}")
        print(f"{'='*70}")

        # Read transcript text
        with open(filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read()

        if not transcript_text.strip():
            print("  [ERROR] Empty transcript file")
            return None

        # Try to extract video ID from filename
        video_id = None
        filename_no_ext = filepath.stem

        # Check if filename is a URL
        if 'youtube.com' in filename_no_ext or 'youtu.be' in filename_no_ext:
            video_id = self.extract_video_id_from_url(filename_no_ext)
        elif len(filename_no_ext) == 11:
            # Filename is just the video ID
            video_id = filename_no_ext
        else:
            # Try to extract from any URL in the filename
            video_id = self.extract_video_id_from_url(filename_no_ext)

        if not video_id:
            print(f"  [ERROR] Could not extract video ID from filename: {filepath.name}")
            print("  Filename should be: VIDEO_ID.txt or include the full YouTube URL")
            return None

        print(f"  Video ID: {video_id}")

        # Parse transcript (try with timestamps first, then plain)
        if re.search(r'\d{1,2}:\d{2}', transcript_text):
            print("  Format: Transcript with timestamps")
            entries = self.parse_transcript_with_timestamps(transcript_text)
        else:
            print("  Format: Plain transcript (no timestamps)")
            entries = self.parse_transcript_plain(transcript_text)

        if not entries:
            print("  [ERROR] Could not parse transcript")
            return None

        # Combine all text
        full_text = " ".join(entry['text'] for entry in entries)

        # Create result
        result = {
            'video_id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'title': 'Manual Import',  # Will be updated if metadata available
            'channel': 'HighLevel',
            'transcript': full_text,
            'transcript_entries': entries,
            'word_count': len(full_text.split()),
            'language': 'en',
            'is_generated': True,
            'method': 'manual-import',
            'scraped_date': datetime.now().isoformat()
        }

        print(f"\n[SUCCESS] Transcript processed!")
        print(f"  Word count: {result['word_count']}")
        print(f"  Entries: {len(entries)}")

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

    def process_directory(self) -> List[Dict]:
        """Process all transcript files in the manual directory"""
        files = list(self.manual_dir.glob('*.txt'))

        if not files:
            print(f"\n[INFO] No transcript files found in: {self.manual_dir}")
            print("\nPlace your transcript .txt files in this directory and run again.")
            return []

        print(f"\n{'='*70}")
        print(f"Found {len(files)} transcript file(s)")
        print(f"{'='*70}")

        results = []
        for i, filepath in enumerate(files):
            print(f"\n[{i+1}/{len(files)}]")

            result = self.process_transcript_file(filepath)
            if result:
                saved_path = self.save_transcript(result)
                results.append(result)

                # Move processed file to avoid reprocessing
                processed_dir = self.manual_dir / 'processed'
                processed_dir.mkdir(exist_ok=True)
                processed_path = processed_dir / filepath.name

                try:
                    filepath.rename(processed_path)
                    print(f"  Moved to: {processed_path}")
                except Exception as e:
                    print(f"  [WARN] Could not move file: {e}")

        return results


def main():
    processor = ManualTranscriptProcessor()

    print("\n" + "="*70)
    print("BroBro - Manual YouTube Transcript Processor")
    print("="*70)
    print(f"\nInput directory: {processor.manual_dir}")
    print(f"Output directory: {processor.output_dir}")
    print("="*70)

    # Check if specific file provided
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"\n[ERROR] File not found: {filepath}")
            sys.exit(1)

        result = processor.process_transcript_file(filepath)
        if result:
            processor.save_transcript(result)
            print("\n[SUCCESS] Transcript processed!")
        else:
            print("\n[FAILED] Could not process transcript")
            sys.exit(1)
    else:
        # Process entire directory
        results = processor.process_directory()

        print(f"\n{'='*70}")
        print(f"[COMPLETE] Processed {len(results)} transcript(s)")
        print(f"{'='*70}")

        if results:
            total_words = sum(r['word_count'] for r in results)
            print(f"\nTotal words: {total_words:,}")
            print(f"Output directory: {processor.output_dir}")
            print(f"\nNext step: python scripts/embed-youtube-tutorials.py data/youtube-tutorials/")
        else:
            print("\nNo transcripts were processed.")
            print(f"\nTo use this tool:")
            print(f"1. Copy transcript from YouTube")
            print(f"2. Save as .txt file in: {processor.manual_dir}")
            print(f"3. Name file: VIDEO_ID.txt (e.g., Po2i0GTX_LU.txt)")
            print(f"   OR include the full YouTube URL in the filename")
            print(f"4. Run: python scripts/process-manual-transcripts.py")


if __name__ == "__main__":
    main()
