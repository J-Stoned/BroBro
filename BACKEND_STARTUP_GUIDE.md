# GHL WHIZ Backend Startup Guide

## Quick Start (TL;DR)

```bash
# Terminal 1: Start ChromaDB
cd "c:\Users\justi\BroBro"
.\start-chroma.bat

# Terminal 2: Start Backend
cd "c:\Users\justi\BroBro\web\backend"
python main.py

# Terminal 3: Start Frontend
cd "c:\Users\justi\BroBro\web\frontend"
npm run dev
```

Then open: http://localhost:3000

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **Node.js 16+**
   - Check: `node --version`
   - Download: https://nodejs.org/

3. **ChromaDB**
   - Already configured in project
   - No separate installation needed

### Python Dependencies

All Python dependencies are listed in `requirements.txt`:

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
chromadb==0.5.23
sentence-transformers==3.3.1
python-dotenv==1.0.1
pydantic==2.10.4
pydantic-settings==2.6.1
```

Install with:
```bash
cd "c:\Users\justi\BroBro\web\backend"
pip install -r requirements.txt
```

---

## Step-by-Step Startup

### Step 1: Start ChromaDB

ChromaDB is the vector database that stores embedded documentation.

**Option A: Using the batch script (Recommended)**
```bash
cd "c:\Users\justi\BroBro"
.\start-chroma.bat
```

**Option B: Manual start**
```bash
cd "c:\Users\justi\BroBro"
chroma run --host 0.0.0.0 --port 8001 --path ./chroma_db
```

**Expected Output:**
```
Running Chroma at http://0.0.0.0:8001
```

**Troubleshooting:**
- If ChromaDB fails to start, ensure port 8001 is not in use
- Check: `netstat -ano | findstr :8001`
- If port is busy, kill the process or use a different port (update .env accordingly)

### Step 2: Start Backend Server

The FastAPI backend provides the API endpoints.

**Start the server:**
```bash
cd "c:\Users\justi\BroBro\web\backend"
python main.py
```

**Expected Output:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Health Check:**
Open http://localhost:8000/health in your browser. You should see:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "chroma_connected": true,
  "collections": {
    "ghl-knowledge-base": 586,
    "ghl-docs": 649
  },
  "model_loaded": true,
  "timestamp": "2025-10-29T19:30:00.000000"
}
```

**Troubleshooting:**
- **Port 8000 already in use:** Kill the process or change port in `main.py`
- **ChromaDB connection failed:** Ensure ChromaDB is running on port 8001
- **Collections empty:** Run the embedding scripts (see Data Setup section)
- **Module not found:** Install dependencies with `pip install -r requirements.txt`

### Step 3: Start Frontend

The React frontend provides the user interface.

**Install dependencies (first time only):**
```bash
cd "c:\Users\justi\BroBro\web\frontend"
npm install
```

**Start the development server:**
```bash
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in 806 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Access the application:**
Open http://localhost:3000 in your browser

**Troubleshooting:**
- **Port 3000 already in use:** Frontend will auto-select port 3001
- **Backend offline error:** Ensure backend is running on port 8000
- **Cannot connect to ChromaDB:** Check that ChromaDB is running

---

## Verify Everything is Working

### 1. Check Connection Status

In the GHL WHIZ UI (top-right corner), you should see:
- **Green "Online" badge** with document count
- Example: "Online • 1,235 docs"

### 2. Test Commands Tab

1. Navigate to **Commands** tab
2. You should see the command library with 500+ commands
3. If you see "Backend Server Offline", the backend is not running

### 3. Test Chat Tab

1. Navigate to **Chat** tab
2. Try asking: "How do I create a lead nurture workflow?"
3. You should get a response with relevant documentation

### 4. Test Search Tab

1. Navigate to **Search** tab
2. Search for: "appointment reminders"
3. You should see search results with relevance scores

---

## Common Issues and Solutions

### Issue: "Backend Server Offline" message

**Symptoms:**
- Red "Offline" badge in header
- "Backend Server Offline" messages on all tabs
- Cannot load commands, chat, or search

**Solution:**
1. Check if backend is running: http://localhost:8000/health
2. If not running, start backend: `python main.py` in `web/backend` directory
3. Click "Check Connection" button to retry

### Issue: "ChromaDB disconnected" in footer

**Symptoms:**
- Backend shows "degraded" status
- Collections show 0 documents
- Search returns no results

**Solution:**
1. Start ChromaDB: `.\start-chroma.bat`
2. Wait for "Running Chroma" message
3. Restart backend to reconnect
4. Refresh frontend

### Issue: Collections are empty (0 documents)

**Symptoms:**
- Health check shows `"collections": {}`
- Search returns no results
- Commands tab is empty

**Solution:**
Run the embedding scripts to populate ChromaDB:

```bash
cd "c:\Users\justi\BroBro"

# Embed commands (from .claude/commands folder)
python scripts/embed-content.py

# Embed documentation (from knowledge_base/scraper_output)
python scripts/embed-docs.py
```

Expected: 586 documents in ghl-knowledge-base + 649 in ghl-docs = 1,235 total

### Issue: ModuleNotFoundError

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd "c:\Users\justi\BroBro\web\backend"
pip install -r requirements.txt
```

### Issue: Port already in use

**For ChromaDB (port 8001):**
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Or change port in .env:
CHROMA_PORT=8002
```

**For Backend (port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in main.py:
uvicorn.run(app, host="0.0.0.0", port=8002)
```

**For Frontend (port 3000):**
Vite will automatically use the next available port (3001, 3002, etc.)

---

## Data Setup (First Time Only)

### Embedding Scripts

GHL WHIZ uses two embedding scripts to populate ChromaDB:

#### 1. Embed Commands (`scripts/embed-content.py`)

Embeds all slash command files from `.claude/commands/`:

```bash
cd "c:\Users\justi\BroBro"
python scripts/embed-content.py
```

**Expected Output:**
```
Processing 586 command files...
✓ Embedded: ghl-landing-page.md
✓ Embedded: ghl-funnel.md
...
✓ Successfully embedded 586 commands
Collection: ghl-knowledge-base
```

#### 2. Embed Documentation (`scripts/embed-docs.py`)

Embeds scraped documentation from `knowledge_base/scraper_output/`:

```bash
cd "c:\Users\justi\BroBro"
python scripts/embed-docs.py
```

**Expected Output:**
```
Processing 649 documentation files...
✓ Embedded: getting-started.json
✓ Embedded: workflows.json
...
✓ Successfully embedded 649 docs
Collection: ghl-docs
```

### Verify Embeddings

Check that embeddings were created:

```bash
# Start backend if not running
python web/backend/main.py

# Check health endpoint
curl http://localhost:8000/health
```

Should show:
```json
{
  "collections": {
    "ghl-knowledge-base": 586,
    "ghl-docs": 649
  }
}
```

---

## Environment Variables

### Backend (.env)

Located at: `c:\Users\justi\BroBro\.env`

```env
# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_PATH=./chroma_db

# Collections
CHROMA_COLLECTION_COMMANDS=ghl-knowledge-base
CHROMA_COLLECTION_DOCS=ghl-docs

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Note:** These are the defaults. Only create a `.env` file if you need to override them.

---

## API Endpoints Reference

### Health & System

- `GET /health` - System health check
- `GET /api/health` - Same as /health (frontend-friendly)
- `GET /api/system/info` - System information
- `GET /api/collections` - List collections and counts

### Search

- `POST /api/search` - Semantic search
  ```json
  {
    "query": "how to create workflows",
    "n_results": 10,
    "collection_filter": "both",
    "include_metadata": true
  }
  ```

### Chat

- `POST /api/chat` - Chat completion (uses search internally)
  ```json
  {
    "message": "How do I set up appointment reminders?",
    "history": []
  }
  ```

### Analytics (Epic 13)

- `POST /api/analytics/executions/start` - Start workflow execution tracking
- `POST /api/analytics/executions/complete` - Complete execution
- `GET /api/analytics/metrics` - Get metrics summary
- `GET /api/analytics/performance/bottlenecks/{workflow_id}` - Detect bottlenecks

---

## Testing the Setup

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response includes:
- `"status": "healthy"`
- `"chroma_connected": true`
- `"collections": { ... }`

### 2. Search API Test

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "appointment reminders",
    "n_results": 5,
    "collection_filter": "both"
  }'
```

Expected: JSON response with 5 search results

### 3. Frontend Connection Test

1. Open http://localhost:3000
2. Check connection status indicator (top-right)
3. Should show "Online" with green badge
4. Footer should show "1,235 documents indexed"

---

## Shutdown Procedure

To safely shut down GHL WHIZ:

1. **Stop Frontend** (Terminal 3)
   - Press `Ctrl+C` in the terminal running `npm run dev`

2. **Stop Backend** (Terminal 2)
   - Press `Ctrl+C` in the terminal running `python main.py`

3. **Stop ChromaDB** (Terminal 1)
   - Press `Ctrl+C` in the terminal running ChromaDB

**Note:** Data persists in `./chroma_db` directory. No data loss on shutdown.

---

## Development Tips

### Hot Reload

- **Frontend:** Changes to React components reload automatically
- **Backend:** Restart required (or use `uvicorn --reload`)
- **ChromaDB:** No restart needed for queries, restart for schema changes

### Debugging

**Backend Logs:**
All API requests are logged to console where `python main.py` is running.

**Frontend Logs:**
Open browser DevTools (F12) → Console tab

**ChromaDB Logs:**
Console where ChromaDB is running shows all vector operations

### Browser DevTools

Useful for debugging API errors:
1. Open DevTools (F12)
2. Network tab → Filter: "Fetch/XHR"
3. Click any failed request to see details
4. Response tab shows error message

---

## Production Deployment Notes

This guide focuses on local development. For production:

1. **Use environment-specific configs**
   - Production `.env` with secure settings
   - HTTPS endpoints
   - CORS whitelist

2. **Use production servers**
   - gunicorn instead of uvicorn for backend
   - nginx for serving frontend
   - Managed ChromaDB instance

3. **Enable monitoring**
   - Application logging
   - Health check alerts
   - Analytics dashboards

See `DEPLOYMENT.md` for production setup (to be created).

---

## Additional Resources

- **Project Documentation:** `START_HERE.md`
- **Epic Progress:** `EPIC_*_PROGRESS.md` files
- **Architecture:** `web/README.md`
- **API Docs:** http://localhost:8000/docs (when backend running)

---

## Support

If you encounter issues not covered in this guide:

1. Check the error message in browser console (F12)
2. Check backend logs in terminal
3. Verify all services are running (ChromaDB → Backend → Frontend)
4. Review `TROUBLESHOOTING.md` (if available)

**Common Error Patterns:**

- **ECONNREFUSED:** Backend not running
- **ChromaDB disconnected:** ChromaDB not running or wrong port
- **Collections empty:** Run embedding scripts
- **Module not found:** Install Python dependencies
- **npm ERR!:** Delete `node_modules` and run `npm install`

---

**Last Updated:** October 29, 2025
**GHL WHIZ Version:** 1.0 (Epics 1-13 Complete)
