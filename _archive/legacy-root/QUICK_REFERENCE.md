# BroBro - Quick Reference Card

## Manual YouTube Transcript Workflow

### Step 1: Copy Transcript (2 min per video)
1. Open video: `https://www.youtube.com/watch?v=VIDEO_ID`
2. Click **... (More)** → **Show transcript**
3. **Ctrl+A** (select all) → **Ctrl+C** (copy)

### Step 2: Save Transcript
1. Open Notepad
2. **Ctrl+V** (paste)
3. Save to: `c:\Users\justi\BroBro\data\manual-transcripts\`
4. Filename: `VIDEO_ID.txt` (e.g., `Po2i0GTX_LU.txt`)

### Step 3: Process Transcripts
```bash
python scripts/process-manual-transcripts.py
```

### Step 4: Embed into KB
```bash
python scripts/embed-youtube-tutorials.py data/youtube-tutorials/
```

---

## Finding Video IDs

From URL `https://www.youtube.com/watch?v=Po2i0GTX_LU`:
- Video ID = `Po2i0GTX_LU` (the 11 characters after `v=`)

---

## Check Progress

```bash
# Count videos processed
python scripts/quick-progress-check.py

# Check KB status
ls data/youtube-tutorials/youtube_*.json | wc -l
```

---

## Current Status

**Videos in KB:** 11
**Method:** Manual copying from YouTube
**Goal:** 100-1,700 videos (as many as you want!)

---

## Tips

- **Batch process:** Copy 10-20 transcripts, then process all at once
- **Name correctly:** Use just the video ID: `Po2i0GTX_LU.txt`
- **Daily goal:** 20-50 videos = 30-60 minutes
- **Hire help:** Fiverr/Upwork can copy all 1,700 for ~$50-100

---

## Files & Directories

| Path | Purpose |
|------|---------|
| `data/manual-transcripts/` | Place transcript .txt files here |
| `data/manual-transcripts/processed/` | Processed files moved here |
| `data/youtube-tutorials/` | JSON output files |
| `scripts/process-manual-transcripts.py` | Processor script |
| `MANUAL_YOUTUBE_WORKFLOW.md` | Full detailed guide |

---

## Troubleshooting

**"Could not extract video ID"**
→ Check filename has 11-char video ID

**"Empty transcript file"**
→ Make sure you copied the transcript (Ctrl+A, Ctrl+C, Ctrl+V)

**Script not found**
→ Run from: `c:\Users\justi\BroBro\`

---

**Full Guide:** See `MANUAL_YOUTUBE_WORKFLOW.md` for complete instructions
