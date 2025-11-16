# Knowledge Base Setup - GHL WHIZ

## Current Status

**Backend:** ✅ Running at http://localhost:8000
**ChromaDB:** ✅ Running at http://localhost:8001
**Frontend:** ✅ Running at http://localhost:3000
**Embedding:** ✅ Complete (424 articles → 960 chunks)

## Problem

The knowledge base collections were empty:
- `ghl-knowledge-base` - Did not exist
- `ghl-docs` - Did not exist

This caused searches to return no results.

## Solution

Running the embedding script to populate ChromaDB:
```bash
python scripts/embed-ghl-docs.py
```

This script:
1. Loads the embedding model (`sentence-transformers/all-MiniLM-L6-v2`)
2. Reads 424 articles from `kb/ghl-docs`
3. Chunks each article
4. Generates embeddings
5. Stores in ChromaDB collection `ghl-docs`

## Expected Result

After embedding completes:
- Collection `ghl-docs` will have ~424 documents
- Search queries will return relevant results
- Commands tab will show available commands
- Chat will work with knowledge base

## Testing the Knowledge Base

Once embedding is complete, test at:
- **Commands Tab:** http://localhost:3000 (click Commands)
- **Chat Tab:** Ask "How do I create a lead nurture workflow?"
- **Search Tab:** Search for "appointment reminders"

All should return relevant results from the knowledge base.

## Health Check

Check backend status:
```bash
curl http://localhost:8000/health
```

Should show:
```json
{
  "status": "healthy",
  "chroma_connected": true,
  "collections": {
    "ghl-docs": 424
  },
  "model_loaded": true
}
```

## Time Estimate

Embedding 424 articles takes approximately:
- ~10-15 minutes total
- ~2-3 seconds per article
- Progress shown in real-time

✅ Embedding complete!
Backend connected to ghl-docs collection: 960 chunks ready for search
