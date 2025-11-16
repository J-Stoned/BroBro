# 7. Deployment Architecture

### 7.1 Local Deployment (MVP)

**Target Environment:** Windows Desktop (Windows 10/11)

**Prerequisites:**
- Node.js 20+ LTS
- Docker Desktop
- Git
- Text editor (VS Code recommended for Claude Code)

**Deployment Steps:**

```bash
# 1. Clone repository
git clone <repo-url>
cd "C:\Users\justi\BroBro"

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env
# Edit .env with GHL OAuth credentials, Firecrawl API key

# 4. Start Chroma Vector DB
docker run -d -p 8000:8000 -v ./chroma_db:/chroma/chroma chromadb/chroma

# 5. Configure MCP servers in Claude Code
# Claude Code reads .claude/settings.local.json automatically

# 6. Build GHL API MCP server
cd mcp-servers/ghl-api-server
npm install
npm run build

# 7. Run knowledge base pipeline (first time only)
node scripts/build-knowledge-base.js

# 8. Open project in Claude Code
# MCP servers auto-start when Claude Code loads project
```

**Runtime Architecture:**

```
┌─────────────────────────────────────────────┐
│         Windows Desktop (localhost)         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Claude Code │  │  MCP Servers         │ │
│  │             │  │  ├─ ghl-api (stdio) │ │
│  │  Slash      │──┼──├─ chroma (HTTP)    │ │
│  │  Commands   │  │  ├─ memory (HTTP)    │ │
│  │             │  │  ├─ youtube (npx)    │ │
│  │             │  │  └─ firecrawl (npx)  │ │
│  └─────────────┘  └──────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Docker Desktop                      │   │
│  │  └─ Chroma Container (port 8000)   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ File System                         │   │
│  │  ├─ kb/ (knowledge base content)   │   │
│  │  ├─ chroma_db/ (vector storage)    │   │
│  │  └─ .env (OAuth tokens, API keys)  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 7.2 MCP Server Configuration

**File:** `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(npx @anthropic-ai/mcp-doctor list-servers)",
      "Bash(dir:*)",
      "Bash(where:*)",
      "Bash(claude mcp list:*)"
    ]
  },
  "mcp": {
    "servers": {
      "ghl-api": {
        "command": "node",
        "args": ["./mcp-servers/ghl-api-server/dist/index.js"],
        "env": {
          "GHL_CLIENT_ID": "${GHL_CLIENT_ID}",
          "GHL_CLIENT_SECRET": "${GHL_CLIENT_SECRET}",
          "NODE_ENV": "production"
        }
      },
      "chroma-db": {
        "transport": "http",
        "url": "http://localhost:8000"
      },
      "memory-service": {
        "transport": "http",
        "url": "http://localhost:8001"
      },
      "youtube-transcript-pro": {
        "command": "npx",
        "args": ["@thisis-romar/mcp-youtube-transcript-pro"]
      },
      "youtube-intelligence": {
        "command": "npx",
        "args": ["@of3y/mcp-youtube-transcript"]
      },
      "firecrawl": {
        "command": "npx",
        "args": ["@firecrawl/mcp-server"],
        "env": {
          "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
        }
      }
    }
  }
}
```

### 7.3 Cloud Migration Path (Future)

**Phase 1: Hybrid (Local + Cloud Vector DB)**

```
User Machine:
  - Claude Code
  - MCP servers (stdio)

Cloud (Azure/AWS/GCP):
  - Chroma on VM (HTTP transport)
  - Benefits: Multi-device access, persistent storage
```

**Phase 2: Fully Cloud-Deployed**

```
User Machine:
  - Claude Code only

Cloud:
  - MCP servers as HTTP endpoints (Azure Functions, AWS Lambda)
  - Chroma managed service
  - Object storage for KB content

Benefits:
  - No local setup
  - Auto-scaling
  - Team access
  - Centralized updates
```

**Migration Checklist:**
1. ✅ Test Chroma HTTP transport locally
2. Deploy Chroma to cloud VM
3. Update `.claude/settings.local.json` with cloud URL
4. Containerize GHL API MCP server (Docker)
5. Deploy to cloud functions
6. Migrate to HTTP transport
7. Update slash commands to use HTTP MCP servers

---
