# YouTube Scraping Guide - Resuming After IP Block

## Current Status

**Date:** November 1, 2025
**Videos Scraped:** 11 out of ~1,700
**Issue:** YouTube IP rate limit (429 Too Many Requests)
**KB Status:** 11 videos successfully embedded into `ghl-tutorials` collection

---

## What Happened

YouTube detected too many rapid requests from your IP address and temporarily blocked access to both:
- `youtube-transcript-api` - "YouTube is blocking requests from your IP"
- `yt-dlp` subtitle extraction - "HTTP Error 429: Too Many Requests"

This is a **temporary block** that typically clears in 30 minutes to 4 hours.

---

## Step-by-Step Resume Process

### Step 1: Check if YouTube Block Has Cleared

Run the IP block checker to monitor when YouTube unblocks your IP:

```bash
python scripts/check-youtube-ip-block.py
```

**Options:**
```bash
# Check every 2 minutes instead of every minute
python scripts/check-youtube-ip-block.py 120

# Check every 5 minutes, up to 30 times (2.5 hours total)
python scripts/check-youtube-ip-block.py 300 30
```

The script will automatically notify you when YouTube access is restored.

---

### Step 2: Resume Scraping with Slow Rate Limiting

Once the block clears, use the **slow-rate scraper** to avoid getting blocked again:

```bash
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos"
```

**Features of the slow scraper:**
- ✓ Uses 10-second delays between requests (vs. 2 seconds before)
- ✓ Automatically skips already-scraped videos (the 11 we have)
- ✓ Shows progress with ETA
- ✓ Uses yt-dlp fallback method to bypass API blocks
- ✓ Resumes where you left off

**Custom delay (even slower for extra safety):**
```bash
# 15-second delays (safer but slower)
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos" "" 15

# 20-second delays (safest)
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos" "" 20
```

**Estimated Time:**
- With 10-second delays: ~5 hours for 1,700 videos
- With 15-second delays: ~7 hours for 1,700 videos
- With 20-second delays: ~9.5 hours for 1,700 videos

---

### Step 3: Run in Background (Recommended)

To scrape overnight or while doing other work:

```bash
# Start scraping in background
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos" > scraping.log 2>&1 &
```

**Monitor progress:**
```bash
# Check how many videos scraped
ls data/youtube-tutorials/youtube_*.json | wc -l

# View latest log entries
tail -f scraping.log
```

---

### Step 4: Embed Newly Scraped Videos

After scraping completes (or periodically during scraping):

```bash
python scripts/embed-youtube-tutorials.py data/youtube-tutorials/
```

This will:
- Chunk long transcripts (800 words with 100-word overlap)
- Embed new videos into the `ghl-tutorials` collection
- Skip already-embedded videos

---

## Scripts Reference

### 1. `check-youtube-ip-block.py`
**Purpose:** Monitor when YouTube unblocks your IP
**Usage:** `python scripts/check-youtube-ip-block.py [interval_seconds] [max_checks]`
**Example:** Check every 2 minutes: `python scripts/check-youtube-ip-block.py 120`

### 2. `scrape-youtube-channel-slow.py`
**Purpose:** Scrape channel with slow rate limiting to avoid blocks
**Usage:** `python scripts/scrape-youtube-channel-slow.py <channel_url> [max_videos] [delay_seconds]`
**Example:** `python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos" "" 15`

**Key Features:**
- Automatically skips already-scraped videos
- Uses 10-second delays by default (customizable)
- Shows ETA and progress
- Uses yt-dlp fallback method

### 3. `scrape-youtube-robust-v2.py`
**Purpose:** Scrape single videos with IP block workaround
**Usage:** `python scripts/scrape-youtube-robust-v2.py <video_url>`
**Example:** `python scripts/scrape-youtube-robust-v2.py "https://www.youtube.com/watch?v=VIDEO_ID"`

**Key Features:**
- Try youtube-transcript-api first (fast)
- Falls back to yt-dlp subtitle extraction
- Bypasses some IP blocks

### 4. `embed-youtube-tutorials.py`
**Purpose:** Embed scraped videos into ChromaDB knowledge base
**Usage:** `python scripts/embed-youtube-tutorials.py data/youtube-tutorials/`

---

## Troubleshooting

### Q: How long until YouTube unblocks my IP?
**A:** Typically 30-60 minutes, but can be up to 2-4 hours for severe blocks. Use the checker script to monitor.

### Q: What if I get blocked again during scraping?
**A:** The slow-rate scraper automatically skips already-scraped videos, so you can restart where you left off:
```bash
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos"
```

### Q: Can I scrape faster once the block clears?
**A:** Not recommended. Stick with 10-15 second delays to avoid another block. Better to scrape slowly than get blocked repeatedly.

### Q: What if both youtube-transcript-api AND yt-dlp are blocked?
**A:** Wait for the block to clear. When it does, yt-dlp typically unblocks first (it's more resilient than the transcript API).

### Q: How do I check my current progress?
**A:** Count the JSON files:
```bash
ls data/youtube-tutorials/youtube_*.json | wc -l
```

Or check the KB:
```bash
python -c "import chromadb; client = chromadb.HttpClient(host='localhost', port=8001); print(client.get_collection('ghl-tutorials').count())"
```

---

## Current Files in System

**Scrapers:**
- `scripts/scrape-youtube-robust-v2.py` - Single video scraper with IP block workaround
- `scripts/scrape-youtube-channel-slow.py` - Channel scraper with slow rate limiting
- `scripts/scrape-youtube-channel.py` - Original fast scraper (causes blocks, don't use)

**Monitoring:**
- `scripts/check-youtube-ip-block.py` - Monitor when YouTube unblocks IP

**Embedding:**
- `scripts/embed-youtube-tutorials.py` - Embed videos into ChromaDB

**Data:**
- `data/youtube-tutorials/` - Scraped video JSON files (11 currently)

---

## Quick Start (When Block Clears)

**All-in-one command:**
```bash
# 1. Check if block cleared
python scripts/check-youtube-ip-block.py

# 2. Once cleared, start slow scraping
python scripts/scrape-youtube-channel-slow.py "https://www.youtube.com/@gohighlevel/videos"

# 3. Embed results (run periodically or after completion)
python scripts/embed-youtube-tutorials.py data/youtube-tutorials/
```

---

## Notes

- Always use the `/videos` suffix on channel URLs
- The slow scraper will take 5-9 hours for 1,700 videos (depending on delay setting)
- You can stop and resume at any time - already-scraped videos are automatically skipped
- Embedded videos are never re-embedded, so you can run the embedder multiple times safely

---

**Last Updated:** 2025-11-01
**Status:** Waiting for YouTube IP block to clear (check with `check-youtube-ip-block.py`)
