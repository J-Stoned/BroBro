# Story 2.4 - Semantic Chunking Pipeline Execution

## Overview
Activate the semantic chunking pipeline on all knowledge base content:
- ✅ 25+ GHL documentation pages (from Puppeteer scraper)
- ✅ 38 best practices guides (from curation)
- ✅ 31 snapshot profiles (from curation)
- YouTube transcripts (when available)

## Chunking Strategy
- **Chunk Size:** 512 tokens (optimal for embeddings + context)
- **Overlap:** 10% (improves retrieval continuity)
- **Semantic Chunking:** Content-aware splitting (sentences, paragraphs)
- **Output:** JSON files with chunks + metadata

## Available Commands

### Chunk All Content (Recommended for First Run)
```bash
npm run chunk:all
# or
node scripts/chunk-documents.js --source all
```
Chunks all sources sequentially into processed directories.

### Chunk by Source
```bash
# Only GHL documentation
npm run chunk:ghl

# Only best practices (38 files)
npm run chunk:best-practices

# Only snapshots (31 files)
npm run chunk:snapshots

# Best practices + snapshots (69 curated files)
npm run chunk:curated
```

### Custom Chunking
```bash
# Custom chunk size (256 tokens)
node scripts/chunk-documents.js --chunk-size 256

# Custom overlap (20%)
node scripts/chunk-documents.js --overlap 0.20

# Specific directory
node scripts/chunk-documents.js --input kb/best-practices --output kb/best-practices/processed
```

## Execution Plan (Recommended)

### Phase 1: Chunk Curated Content First (Faster)
```bash
npm run chunk:curated
# Time estimate: ~2-3 minutes (69 files, ~2,000-3,000 chunks)
```

**Why first?** Curated content is well-structured, smaller, and will validate the pipeline works correctly.

### Phase 2: Chunk GHL Documentation (Slower)
```bash
npm run chunk:ghl
# Time estimate: ~5-10 minutes (25+ pages, ~1,000-2,000 chunks)
```

**Why second?** Scraped content is larger and may take longer.

### Phase 3: Complete Full Pipeline (If Available)
```bash
npm run chunk:youtube
# Time estimate: Depends on transcript count
```

## Expected Output Structure

After chunking, you'll have processed directories:
```
kb/
├── best-practices/
│   └── processed/
│       ├── automated-lead-scoring-workflow_chunks.json
│       ├── email-drip-nurture-sequence_chunks.json
│       └── ... (38 files total)
├── snapshots-reference/
│   └── processed/
│       ├── small-business-snapshot_chunks.json
│       ├── epic-real-estate-agent-snapshot_chunks.json
│       └── ... (31 files total)
└── ghl-docs/
    └── processed/
        ├── dashboard-setup_chunks.json
        ├── workflow-automation_chunks.json
        └── ... (25+ files)
```

## Chunk Output Format

Each `*_chunks.json` file contains:
```json
{
  "sourceFile": "path/to/original.md",
  "chunkCount": 42,
  "chunks": [
    {
      "id": "chunk_1",
      "text": "Content from 400-600 tokens...",
      "tokens": 523,
      "metadata": {
        "title": "Original document title",
        "source": "best-practices",
        "category": "lead-nurturing"
      }
    }
    // ... more chunks
  ],
  "stats": {
    "totalTokens": 21966,
    "avgTokensPerChunk": 523,
    "minTokens": 412,
    "maxTokens": 645
  },
  "chunkedAt": "2025-10-26T15:30:00Z"
}
```

## Summary Report

After chunking completes, a `kb/chunk-summary.json` file will be generated:
```json
{
  "processedAt": "2025-10-26T15:30:00Z",
  "config": {
    "chunkSize": 512,
    "overlap": 0.10,
    "source": "all"
  },
  "totals": {
    "documents": 94,
    "chunks": 5847,
    "tokens": 2892341,
    "avgChunksPerDoc": 62,
    "avgTokensPerChunk": 495
  },
  "results": [...]
}
```

## Logs

Real-time logs saved to:
- `kb/chunk.log` - Detailed processing log
- `kb/chunk-summary.json` - Final statistics

## Next Steps (Story 2.5)

After chunking completes successfully, proceed to:
- **Story 2.5:** Embedding Generation & Indexing
  - Generate embeddings for all chunks
  - Index chunks to Chroma vector database
  - Command: `npm run embed-content`

## Troubleshooting

### Script Hangs
- Check available disk space
- Verify all input directories exist
- Check `kb/chunk.log` for errors

### Missing Output Files
- Verify input directories have readable markdown files
- Check file permissions
- Review error logs in `kb/chunk.log`

### Memory Issues
- Process runs in Node.js (moderate memory usage)
- If memory exceeds 2GB, increase Node heap: `NODE_OPTIONS=--max-old-space-size=4096 npm run chunk:all`

## Ready to Execute?

✅ Script updated to support: ghl-docs, youtube-transcripts, best-practices, snapshots
✅ npm scripts added for convenient execution
✅ 69 curated files (38 best practices + 31 snapshots) ready
✅ 25+ GHL documentation pages ready
✅ Chunking strategy: 512 tokens, 10% overlap

**Recommendation:** Run `npm run chunk:curated` first to validate the pipeline, then `npm run chunk:ghl` for documentation.
