# Manual YouTube Transcript Workflow

This guide shows you how to manually copy transcripts from YouTube and process them into your BroBro knowledge base.

---

## Why Manual?

YouTube has persistent IP rate limiting that blocks automated scraping. The manual approach:
- ✓ Bypasses all API/IP blocks
- ✓ Works reliably every time
- ✓ You control the pace
- ✓ Can be done while browsing

---

## Quick Start Guide

### Step 1: Copy Transcript from YouTube

1. Open a YouTube video (e.g., https://www.youtube.com/watch?v=Po2i0GTX_LU)
2. Below the video, click the **"More"** button (three dots ...)
3. Click **"Show transcript"**
4. A transcript panel appears on the right side
5. Click anywhere in the transcript panel
6. Press **Ctrl+A** (select all)
7. Press **Ctrl+C** (copy)

### Step 2: Save the Transcript

1. Open Notepad or any text editor
2. Press **Ctrl+V** (paste)
3. Save the file to: `c:\Users\justi\BroBro\data\manual-transcripts\`
4. **Important:** Name the file with the video ID
   - Find the video ID in the URL: `watch?v=VIDEO_ID`
   - Example: For `watch?v=Po2i0GTX_LU`, save as `Po2i0GTX_LU.txt`
   - Or just include the full URL in the filename

### Step 3: Process the Transcripts

Run this command:
```bash
python scripts/process-manual-transcripts.py
```

The script will:
- Find all `.txt` files in `data/manual-transcripts/`
- Parse each transcript
- Extract video ID from filename
- Save to `data/youtube-tutorials/` in JSON format
- Move processed files to `data/manual-transcripts/processed/`

### Step 4: Embed into Knowledge Base

After processing transcripts, embed them:
```bash
python scripts/embed-youtube-tutorials.py data/youtube-tutorials/
```

---

## Detailed Instructions

### Finding the Video ID

The video ID is the 11-character code in the YouTube URL:

**Examples:**
- `https://www.youtube.com/watch?v=Po2i0GTX_LU` → Video ID: `Po2i0GTX_LU`
- `https://youtu.be/3AwIuOz4tX0` → Video ID: `3AwIuOz4tX0`

### Filename Options

Any of these filename formats work:

1. **Just the Video ID:**
   - `Po2i0GTX_LU.txt`
   - `3AwIuOz4tX0.txt`

2. **Full YouTube URL:**
   - `https___www.youtube.com_watch_v=Po2i0GTX_LU.txt`
   - `youtube-Po2i0GTX_LU.txt`

3. **With Description:**
   - `Po2i0GTX_LU-countdown-timers.txt`

The script extracts the video ID from any of these formats.

### Transcript Formats Supported

**Format 1: With Timestamps** (Preferred)
```
0:00 HighLevel WhatsApp Coexistence Now Live for Everyone!
0:05 Today we're announcing a major update
0:12 You can now use multiple WhatsApp numbers
1:23 This is perfect for agencies
```

**Format 2: Plain Text**
```
HighLevel WhatsApp Coexistence Now Live for Everyone! Today we're announcing a major update. You can now use multiple WhatsApp numbers. This is perfect for agencies.
```

Both formats work - the script auto-detects which one you're using.

---

## Batch Processing

To process multiple videos at once:

1. Copy transcripts from 10-20 YouTube videos
2. Save each as `VIDEO_ID.txt` in `data/manual-transcripts/`
3. Run the processor once: `python scripts/process-manual-transcripts.py`
4. All transcripts are processed in one go

**Example batch:**
```
data/manual-transcripts/
  Po2i0GTX_LU.txt
  3AwIuOz4tX0.txt
  ltclLkjmAiQ.txt
  Z5jEDwabSR0.txt
  SmN6H-EUyww.txt
```

Run processor:
```bash
python scripts/process-manual-transcripts.py
```

Output:
```
Found 5 transcript file(s)
[1/5] Po2i0GTX_LU.txt → Processed ✓
[2/5] 3AwIuOz4tX0.txt → Processed ✓
[3/5] ltclLkjmAiQ.txt → Processed ✓
[4/5] Z5jEDwabSR0.txt → Processed ✓
[5/5] SmN6H-EUyww.txt → Processed ✓

Total: 5 transcripts, 3,456 words
```

---

## Tips & Tricks

### Tip 1: Use Multiple Tabs
Open 10-20 GHL videos in tabs, copy transcripts quickly:
1. Open video → Show transcript → Ctrl+A → Ctrl+C
2. Alt+Tab to Notepad → Ctrl+V → Save as VIDEO_ID.txt
3. Repeat for next tab

You can process 20 videos in 10-15 minutes this way.

### Tip 2: Create a Template Folder
Organize by topic:
```
manual-transcripts/
  automations/
    VIDEO_ID1.txt
    VIDEO_ID2.txt
  workflows/
    VIDEO_ID3.txt
  funnels/
    VIDEO_ID4.txt
```

Move all to root folder when ready to process.

### Tip 3: Use Browser Extensions
Search for "YouTube Transcript Downloader" extensions:
- Download entire transcript with one click
- Auto-saves with video ID
- Supports batch downloads

### Tip 4: Track Progress
Keep a spreadsheet of videos:
- Column A: Video URL
- Column B: Video Title
- Column C: Copied? (Yes/No)
- Column D: Processed? (Yes/No)

---

## Troubleshooting

### Q: Script says "Could not extract video ID"
**A:** Check your filename includes the 11-character video ID. Examples:
- ✓ Good: `Po2i0GTX_LU.txt`
- ✗ Bad: `countdown-timers.txt`

### Q: Empty transcript file?
**A:** Make sure you:
1. Clicked in the transcript panel
2. Pressed Ctrl+A to select all
3. Pressed Ctrl+C to copy
4. Pasted into text file (Ctrl+V)

### Q: Can I process a single file?
**A:** Yes! Run:
```bash
python scripts/process-manual-transcripts.py path/to/VIDEO_ID.txt
```

### Q: What happens to processed files?
**A:** They're moved to `data/manual-transcripts/processed/` to avoid reprocessing.

### Q: Can I reprocess if needed?
**A:** Yes, move the file back from `processed/` to `manual-transcripts/` and run again.

---

## Full Workflow Example

Let's scrape 5 videos:

**1. Identify Videos**
Go to: https://www.youtube.com/@gohighlevel/videos

Pick 5 recent videos:
- https://www.youtube.com/watch?v=Po2i0GTX_LU
- https://www.youtube.com/watch?v=3AwIuOz4tX0
- https://www.youtube.com/watch?v=SmN6H-EUyww
- https://www.youtube.com/watch?v=ltclLkjmAiQ
- https://www.youtube.com/watch?v=Z5jEDwabSR0

**2. Copy Transcripts (5 minutes)**
For each video:
- Open video
- Click "..." → "Show transcript"
- Ctrl+A → Ctrl+C
- Save as `VIDEO_ID.txt`

**3. Process (5 seconds)**
```bash
python scripts/process-manual-transcripts.py
```

Output:
```
Found 5 transcript file(s)
[COMPLETE] Processed 5 transcript(s)
Total words: 2,893
```

**4. Embed (30 seconds)**
```bash
python scripts/embed-youtube-tutorials.py data/youtube-tutorials/
```

Output:
```
Successfully embedded 5 tutorials!
Collection now has: 16 total documents
```

**Done!** Those 5 videos are now searchable in your knowledge base.

---

## Scaling Up

### Goal: 100 Videos
**Time estimate:** 2-3 hours over a few days

**Strategy:**
- Day 1: Copy 30 videos (30 minutes)
- Day 2: Copy 30 videos (30 minutes)
- Day 3: Copy 40 videos (40 minutes)
- Process & embed: 5 minutes

### Goal: 1,700 Videos (Full Channel)
**Time estimate:** 25-30 hours spread over 2-4 weeks

**Strategy:**
- Daily: Copy 50-100 videos (1 hour/day)
- Weekly: Process & embed batches (10 minutes/week)
- 2-4 weeks: Complete

**OR:**

Hire someone on Fiverr/Upwork:
- Task: "Copy transcripts from 1,700 YouTube videos"
- Provide: List of video URLs
- Receive: Folder of .txt files named with video IDs
- Cost: ~$50-100 for the entire channel

---

## Current Status

**Videos in KB:** 11 (from automated scraping before IP block)
**Method:** Manual workflow (this guide)
**Next:** Copy & process more videos at your pace

**Directories:**
- Input: `c:\Users\justi\BroBro\data\manual-transcripts\`
- Output: `c:\Users\justi\BroBro\data\youtube-tutorials\`
- Processed: `c:\Users\justi\BroBro\data\manual-transcripts\processed\`

---

## Need Help?

Run the processor with no arguments to see usage:
```bash
python scripts/process-manual-transcripts.py
```

Check your progress:
```bash
python scripts/quick-progress-check.py
```

Verify KB status:
```bash
python -c "import chromadb; client = chromadb.HttpClient(host='localhost', port=8001); print(f'Videos in KB: {client.get_collection(\"ghl-tutorials\").count()}')"
```

---

**Last Updated:** 2025-11-01
**Status:** Ready to use
