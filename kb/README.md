# GHL Wiz Knowledge Base

This directory contains all knowledge base content for the GHL Wiz assistant, including scraped documentation, YouTube tutorials, best practices, and reference materials.

## Directory Structure

```
kb/
├── youtube-sources.json          # Configuration for YouTube content extraction
├── ghl-docs/                     # GoHighLevel official documentation
│   ├── raw/                      # Original scraped content
│   └── processed/                # Chunked and cleaned content
├── youtube-transcripts/          # YouTube tutorial transcripts
│   ├── by-creator/               # Organized by creator name
│   ├── by-topic/                 # Organized by topic
│   ├── index.json                # Complete metadata index
│   └── failed.log                # Failed extractions log
├── best-practices/               # Curated best practices and guides
├── snapshots-reference/          # Snapshot marketplace information
└── html-templates/               # HTML template resources
```

---

## GoHighLevel Documentation Scraping

### Status: Story 2.1 Complete ✅

**Date:** 2025-10-26
**Method:** Firecrawl API (parallel scraping with 5 concurrent requests)
**Pages Scraped:** 27 pages successfully (28 attempted)
**Performance:** 173 seconds using Ryzen 5 multi-core processing

#### Successfully Scraped Documentation

**Help Site (8 pages from help.gohighlevel.com):**
- Triggers & Workflows overview
- Workflow automation fundamentals
- Contact management and import
- Funnel building guides and templates
- Calendar configuration
- Form builder documentation

**API Documentation (2 pages from marketplace.gohighlevel.com):**
- Getting Started guide
- OAuth authentication

#### Scraping Scripts

1. **`scripts/scrape-parallel.js`** - Parallel scraper with multi-core support (recommended) ⭐
2. **`scripts/scrape-specific-pages.js`** - Single-threaded priority page scraper
3. **`scripts/scrape-ghl-with-api.js`** - Full crawl (requires paid plan)
4. **`scripts/test-firecrawl-mcp.js`** - Configuration validator
5. **`scripts/discover-ghl-urls.js`** - URL discovery tool

#### Usage

```bash
# Parallel scraping (recommended) - uses multi-core CPU
node scripts/scrape-parallel.js --concurrency 5 --batch-size 10

# Adjust concurrency for your CPU (Ryzen 5 = 6 cores, use 5-8 concurrent requests)
node scripts/scrape-parallel.js --concurrency 8 --batch-size 15

# Single-threaded scraping
node scripts/scrape-specific-pages.js

# Test Firecrawl configuration
node scripts/test-firecrawl-mcp.js

# Discover valid URLs
node scripts/discover-ghl-urls.js

# View scraping results
cat kb/ghl-docs/scraping-report.json
```

#### Firecrawl API Limitations

- **Rate Limit:** 10 requests/minute (free tier)
- **Credits:** Limited monthly credits
- **Recommendation:** Use targeted scraping vs. full site crawls

#### Next Steps for Documentation

- Retry failed pages after rate limit reset
- Add more priority URLs to `scripts/scrape-specific-pages.js`
- Consider paid Firecrawl plan for full site crawls (500+ pages)

---

## YouTube Sources Configuration

### Overview

The `youtube-sources.json` file controls which YouTube content is extracted and indexed into the knowledge base. It supports three types of sources:

1. **Creators (Channels)** - Extract videos from specific YouTube creators
2. **Specific Videos** - Individual must-have videos
3. **Playlists** - Complete YouTube playlists

### Adding a Creator

To add a new GoHighLevel expert creator:

1. Open `kb/youtube-sources.json`
2. Add a new object to the `creators` array:

```json
{
  "name": "Creator Name",
  "channelId": "@CreatorChannelHandle",
  "channelUrl": "https://www.youtube.com/@CreatorChannelHandle",
  "description": "Brief description of expertise",
  "maxVideos": 25,
  "topics": ["workflows", "funnels", "api"],
  "priority": "high",
  "enabled": true,
  "notes": "Any special focus areas"
}
```

3. Set `enabled: true` to include in next extraction
4. Run extraction script (see below)

### Adding Specific Videos

For must-have individual videos:

1. Find the video on YouTube
2. Copy the full URL (e.g., `https://www.youtube.com/watch?v=ABC123`)
3. Add to the `specificVideos` array:

```json
{
  "url": "https://www.youtube.com/watch?v=ABC123",
  "title": "Video Title",
  "creator": "Creator Name",
  "category": "must-have",
  "topics": ["workflows", "automation"],
  "priority": "high",
  "enabled": true,
  "notes": "Why this video is important"
}
```

### Adding Playlists

For complete tutorial series:

1. Copy the playlist URL (e.g., `https://www.youtube.com/playlist?list=PLxxx`)
2. Add to the `playlists` array:

```json
{
  "url": "https://www.youtube.com/playlist?list=PLxxx",
  "name": "Playlist Name",
  "creator": "Creator Name",
  "description": "What this series covers",
  "topics": ["saas-mode", "configuration"],
  "priority": "high",
  "enabled": true,
  "maxVideosFromPlaylist": 20,
  "notes": "Special instructions"
}
```

---

## Running YouTube Extraction

Once you've configured your sources:

### Extract All Enabled Sources

```bash
node scripts/extract-yt-transcripts.js
```

This will:
- Read `kb/youtube-sources.json`
- Process all enabled creators, videos, and playlists
- Extract transcripts using YouTube MCP servers
- Save to `kb/youtube-transcripts/`
- Create metadata index

### Extract Specific Creator

```bash
node scripts/extract-yt-transcripts.js --creator "Robb Bailey"
```

### Extract Specific Video

```bash
node scripts/extract-yt-transcripts.js --video "https://youtube.com/watch?v=ABC123"
```

### Dry Run (Preview Only)

```bash
node scripts/extract-yt-transcripts.js --dry-run
```

Shows what would be extracted without actually downloading.

---

## Topic Categories

Use these standardized topics for consistency:

| Topic | Description |
|-------|-------------|
| `workflows` | Workflow automation and triggers |
| `automation` | Marketing automation and sequences |
| `funnels` | Funnel building and optimization |
| `forms` | Form creation and conversion optimization |
| `saas-mode` | SaaS mode configuration and white-labeling |
| `api` | API integration and development |
| `best-practices` | Proven strategies and optimization techniques |
| `product-updates` | New features and platform updates |
| `integrations` | Third-party integrations (Stripe, Twilio, etc.) |
| `calendars` | Calendar and appointment management |
| `snapshots` | Snapshot marketplace and usage |
| `strategy` | Business strategy and use cases |

---

## Priority Levels

- **high**: Process first, most valuable content
- **medium**: Process after high priority
- **low**: Process last, nice-to-have content

---

## Extraction Settings

The `extractionSettings` section in `youtube-sources.json` controls:

- **Language**: Preferred transcript language (default: English)
- **Timestamps**: Include timestamp data (default: true)
- **Auto-generated**: Accept auto-generated transcripts (default: true)
- **Duration**: Min/max video length in seconds
- **Date Filter**: Only extract videos after a certain date
- **Skip Shorts**: Exclude YouTube Shorts (default: true)

---

## Viewing Results

After extraction:

1. **Check the index**: `kb/youtube-transcripts/index.json`
   - Complete metadata for all extracted videos
   - Search by creator, topic, date

2. **Browse by creator**: `kb/youtube-transcripts/by-creator/[creator-name]/`
   - All videos from specific creator

3. **Browse by topic**: `kb/youtube-transcripts/by-topic/[topic-name]/`
   - All videos tagged with specific topic

4. **Check for failures**: `kb/youtube-transcripts/failed.log`
   - Videos that couldn't be extracted
   - Reasons for failure

---

## Recommended YouTube Creators

### Confirmed Experts (Pre-configured)

1. **Robb Bailey** - GHL Platform Master, official trainer
2. **Shaun Clark** - GHL CEO, strategic insights
3. **GoHighLevel Official** - Official product channel

### To Research & Add

When you discover valuable GHL creators, add them to `youtube-sources.json`:

- Search YouTube for "GoHighLevel tutorials"
- Check video quality, recency, and view counts
- Verify creator expertise (check their credentials)
- Add to config and run extraction

---

## Knowledge Base Stats

Track your knowledge base growth:

```bash
# Count total videos extracted
find kb/youtube-transcripts/by-creator -type f -name "*.md" | wc -l

# View latest index stats
cat kb/youtube-transcripts/index.json | jq '.stats'

# Check extraction date
cat kb/youtube-sources.json | jq '.stats'
```

---

## Best Practices

### Curation Guidelines

1. **Quality over Quantity**: 50 high-quality tutorials > 200 mediocre ones
2. **Recency Matters**: Prioritize 2024-2025 content (latest GHL features)
3. **Diverse Topics**: Cover all major GHL features (workflows, funnels, API, etc.)
4. **Verified Experts**: Stick to known GHL experts and official sources
5. **Avoid Duplicates**: Check existing content before adding similar videos

### Maintenance

- **Quarterly Review**: Every 3 months, review and update sources
- **Remove Outdated**: Disable videos covering deprecated features
- **Add New Experts**: Keep an eye on emerging GHL content creators
- **Update Metadata**: Fix incorrect topics/categories as you discover them

---

## Troubleshooting

### "Transcript not available"

Some videos don't have transcripts. The script will:
1. Try YouTube Transcript Pro MCP
2. Fallback to YouTube Intelligence Suite
3. Log to `failed.log` if both fail

**Solution**: Manually request creator to enable transcripts, or skip the video.

### "Channel not found"

**Cause**: Incorrect `channelId` or `channelUrl`

**Solution**:
1. Visit the channel on YouTube
2. Copy the `@ChannelHandle` from the URL
3. Update `channelId` in config

### "Rate limit exceeded"

**Cause**: Too many API requests

**Solution**:
1. Reduce `maxVideos` per creator
2. Add delays between requests (script handles this)
3. Wait and retry later

---

## Next Steps

1. ✅ Review `youtube-sources.json` and enable desired sources
2. 📝 Add any additional creators you follow
3. ▶️ Run extraction script
4. 📊 Review `index.json` for results
5. 🔍 Check `failed.log` for any issues
6. 🔄 Re-run periodically to get new videos from creators

---

For more information, see:
- [Project PRD](../docs/prd.md)
- [Setup Guide](../README.md)
- [Scripts Documentation](../scripts/README.md)
