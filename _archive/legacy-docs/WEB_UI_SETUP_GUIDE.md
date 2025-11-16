# BroBro Web UI - Setup & Usage Guide

## Overview

BroBro has been upgraded with a modern web-based chat interface powered by two AI backends:
- **Claude** + ChromaDB (default) - Superior reasoning with multi-collection search
- **Gemini** + File Search (new) - Fast responses with Google's vector store

Both backends maintain full conversation history and support citations from your knowledge base.

---

## System Requirements

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **4GB RAM minimum** (8GB recommended)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

---

## Installation

### 1. Backend Dependencies

```bash
cd web/backend
pip install -r requirements.txt
```

Required packages:
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- google-genai>=1.0.0
- anthropic>=0.19.0
- chromadb==0.4.22
- sentence-transformers==2.3.1

### 2. Frontend Dependencies

```bash
cd web/frontend
npm install
```

### 3. Environment Setup

Create/update `.env` file in project root:

```env
# Google APIs
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ChromaDB
CHROMA_URL=http://localhost:8001

# Optional: Google File Search Store ID
GOOGLE_FILE_SEARCH_STORE_ID=fileSearchStores/ghlwizcompletekb-9dultbq96h00
```

---

## Running the Servers

### Option 1: Automated Startup (Recommended)

**Windows:**
```bash
start-servers.bat
```

**Linux/Mac:**
```bash
chmod +x start-servers.sh
./start-servers.sh
```

This will:
1. Start FastAPI backend on http://localhost:8000
2. Start Vite frontend on http://localhost:5173
3. Open both in separate console windows (Windows) or terminal tabs

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd web/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd web/frontend
npm run dev
```

### Option 3: Production Build

```bash
# Build frontend
cd web/frontend
npm run build

# Run backend with production settings
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Web UI Navigation

### Main Tabs

1. **Chat** - Conversation with AI (with backend switcher)
2. **Commands** - Browse GHL commands and operations
3. **Workflows** - Visual workflow builder
4. **Analytics** - Performance metrics and insights
5. **Search** - Multi-collection semantic search
6. **Setup Management** - Configuration and system info

### Chat Interface

#### Backend Switcher
Click the "Chat" tab to reveal a dropdown:
- **Claude** - Default, uses ChromaDB with multi-collection search
- **Gemini** - Google-powered, uses File Search with faster responses

#### Features
- **Conversation History** - Automatically saved to localStorage
- **Citations** - Click "Sources" to see referenced documents
- **Export** - Save conversations as JSON or Markdown
- **Settings** - Adjust temperature (creativity) and max tokens
- **Message Actions** - Copy, clear history, or start fresh

#### Keyboard Shortcuts
- `Enter` - Send message
- `Shift+Enter` - New line in message
- `Ctrl+/` - Focus search/command input (varies by tab)

---

## Configuration Options

### Claude Backend (Default)

**Advantages:**
- Superior reasoning and analysis
- Multi-collection search (docs, YouTube, books, business)
- Better at complex questions
- Integrates ChromaDB for fine-grained control

**Settings:**
- Model: Claude 3.5 Haiku (fast) or Sonnet (detailed)
- Temperature: 0.7 (creative) to 1.0 (very creative)
- Max tokens: 1000-4096

### Gemini Backend (New)

**Advantages:**
- Extremely fast responses
- Google's advanced retrieval
- File Search with grounding metadata
- Optimized for factual knowledge base queries

**Settings:**
- Model: Gemini 2.5 Flash
- Temperature: 0.0 (factual) to 1.0 (creative)  ← Default: 0.2 for accuracy
- Max tokens: 500-4000  ← Default: 2000

---

## Knowledge Base Content

### Indexed Collections

| Collection | Content | Source |
|-----------|---------|--------|
| ghl-docs | Official GoHighLevel documentation | GHL knowledge base |
| ghl-youtube | YouTube tutorial transcripts | Extracted from videos |
| ghl-business | Business strategy books | Hormozi, Brunson, etc. |
| ghl-knowledge-base | General knowledge articles | Various sources |

### Recently Added

✨ **Hormozi Business Playbooks** (Extracted & Optimized)
- 100M Offers (8,569 words)
- 100M Leads (14,728 words)
- 100M Money Models (45,200 words)
- 100M Ads (19,025 words)
- Lead Nurture Playbook (13,926 words)

**Total:** 101,448 words, 817 chunks, optimized for retrieval

---

## Testing the System

### Quick Test Queries

**For Claude Backend:**
```
"How do I set up a workflow in GoHighLevel?"
"What are the key strategies from the 100M Offers book?"
"Explain tissue culture micropropagation"
```

**For Gemini Backend:**
```
"Summarize the lead nurturing playbook"
"What are the best practices for GHL automation?"
"Tell me about offer strategy from Hormozi"
```

### Multi-Turn Conversation Test

1. Ask: "What is the 100M Offers framework?"
2. Follow up: "Can you explain the core principles more?"
3. Ask: "How does this relate to GoHighLevel?"

**Expect:** The AI should reference previous answers and build context.

---

## Troubleshooting

### Backend Connection Issues

**Problem:** "Backend offline" message

**Solutions:**
1. Check if backend is running: `http://localhost:8000/health`
2. Verify `.env` has correct API keys
3. Restart backend server
4. Check for port conflicts on 8000

### Slow Responses

**Problem:** Messages taking >10 seconds

**Solutions:**
1. For Gemini: Reduce max_tokens in settings (default 2000)
2. For Claude: Reduce conversation history (fewer previous messages)
3. Check network connection
4. Ensure backend has access to AI APIs

### Missing Knowledge Base Content

**Problem:** "I don't have information on that topic"

**Solutions:**
1. Verify files were uploaded to Google File Search
2. Wait 30-60 minutes after upload for indexing
3. Try searching with different keywords
4. Check collection status in Setup Management tab

### LocalStorage Full

**Problem:** "Conversation too large for localStorage"

**Solutions:**
1. Export conversation (JSON/Markdown)
2. Clear conversation history
3. Restart browser
4. Check browser storage limits (usually 5-10MB)

---

## API Documentation

### Backend Endpoints

#### Chat Endpoints

**Claude Chat**
```
POST /api/chat
{
  "query": "Your question",
  "n_results": 5,
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Gemini Chat**
```
POST /api/gemini/chat
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "temperature": 0.2,
  "max_tokens": 2000
}
```

#### System Endpoints

```
GET /health                          # Health check
GET /api/system/info                 # System status
GET /api/collections                 # List collections
GET /api/gemini/status               # Gemini configuration
```

### Full API Documentation

Interactive API docs available at: **http://localhost:8000/docs**

---

## Performance Tips

1. **Use Gemini for quick facts** - Faster response time, great for factual queries
2. **Use Claude for analysis** - Better reasoning, good for "why" questions
3. **Limit history** - Keep conversations under 10 exchanges for faster responses
4. **Pre-filter** - Use specific keywords instead of broad questions
5. **Batch questions** - Ask multiple related questions together

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` to git (it contains API keys)
- API keys should have minimal permissions
- Conversations are stored in browser localStorage (not encrypted)
- Use HTTPS in production environments
- Implement authentication if deploying online

---

## Advanced Features

### Custom System Prompts

Edit `ghl_kb_chat_v6_FIXED.py` system prompt (lines 441-463) and restart backend to affect Gemini responses.

### Model Selection

Change Claude model in `web/backend/routes/main.py` (line 431):
```python
model_id = "claude-3-5-haiku-20241022"  # Fast
model_id = "claude-3-5-sonnet-20241022"  # Detailed
```

### Collection Management

Add new ChromaDB collections in `web/backend/routes/main.py` for custom knowledge bases.

---

## Support & Documentation

### Helpful Resources

- **Frontend Code:** `web/frontend/src/components/`
- **Backend Code:** `web/backend/routes/` and `web/backend/gemini/`
- **Chat Logic:**
  - Claude: `web/backend/routes/main.py` (lines 419-673)
  - Gemini: `web/backend/routes/gemini_routes.py`

### Common Questions

**Q: Can I use both backends simultaneously?**
A: Yes! Switch between them using the backend selector in the Chat tab.

**Q: How often is the knowledge base updated?**
A: Manually - run `google_file_search_upload.py` or `embed_document.py` to add new content.

**Q: Can I deploy this online?**
A: Yes! Use platforms like Vercel (frontend) + Railway/Render (backend).

**Q: How do I add more documents?**
A: Place `.txt/.pdf/.md` files in `kb/` directories and run upload/embed scripts.

---

## Next Steps

1. ✅ Test both backends (Claude vs Gemini)
2. ✅ Try multi-turn conversations
3. ✅ Export a conversation as reference
4. ✅ Customize system prompts if desired
5. ✅ Add more knowledge base content as needed

---

**Version:** 1.0
**Last Updated:** 2025-11-15
**Status:** ✅ Production Ready
