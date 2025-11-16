# Source Tree

Complete directory structure for the GHL Wiz project.

## Project Root Structure

```
ghl-wiz/
├── .bmad-core/                 # BMAD-METHOD framework
│   ├── agents/                 # Agent definitions
│   ├── tasks/                  # Reusable task workflows
│   ├── templates/              # Document templates
│   └── core-config.yaml        # BMAD configuration
│
├── .claude/                    # Claude Code configuration
│   ├── commands/               # Slash commands
│   │   └── BMad/              # BMAD agent commands
│   └── settings.local.json    # MCP server config
│
├── docs/                       # Project documentation
│   ├── prd/                   # Sharded PRD sections
│   ├── architecture/          # Sharded architecture sections
│   ├── stories/               # User stories (to be created)
│   ├── epics/                 # Epic documents (to be created)
│   ├── project-brief.md       # Initial project vision
│   ├── prd.md                 # Complete PRD (source)
│   └── architecture.md        # Complete architecture (source)
│
├── kb/                        # Knowledge base content
│   ├── ghl-docs/             # GoHighLevel documentation
│   │   ├── raw/              # Original scraped content
│   │   └── processed/        # Chunked and cleaned
│   ├── youtube-transcripts/  # YouTube tutorial transcripts
│   │   ├── by-creator/       # Organized by creator
│   │   ├── by-topic/         # Organized by topic
│   │   ├── index.json        # Metadata index
│   │   └── failed.log        # Failed extractions
│   ├── best-practices/       # Curated guides
│   ├── snapshots-reference/  # Snapshot marketplace info
│   ├── html-templates/       # HTML template resources
│   ├── youtube-sources.json  # YouTube extraction config
│   └── README.md             # KB usage documentation
│
├── mcp-servers/               # Custom MCP servers
│   ├── ghl-api-server/       # GoHighLevel API MCP
│   │   ├── src/
│   │   │   ├── index.ts      # Server entry point
│   │   │   ├── auth/         # OAuth implementation
│   │   │   ├── tools/        # MCP tool definitions
│   │   │   └── utils/        # Rate limiting, helpers
│   │   ├── dist/             # Compiled output
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── chroma-mcp/           # Vector DB MCP wrapper
│   └── memory-service/       # Conversation memory MCP
│
├── scripts/                   # Knowledge base scripts
│   ├── scrape-ghl-docs.js    # Firecrawl documentation scraper
│   ├── extract-yt-transcripts.js  # YouTube content extractor
│   ├── chunk-documents.js    # Semantic chunking
│   ├── build-knowledge-base.js    # Orchestration
│   └── embed-content.js      # Generate embeddings
│
├── config/                    # Configuration files
│   ├── chroma-config.json    # Vector DB settings
│   ├── mcp-servers.json      # MCP server registry
│   └── embeddings.json       # Embedding model config
│
├── tests/                     # Test suite
│   ├── mcp-servers/          # MCP server tests
│   ├── knowledge-base/       # KB retrieval tests
│   └── integration/          # End-to-end tests
│
├── .gitignore
├── package.json              # Project dependencies
├── README.md                 # Project overview
└── LICENSE
```

## Key Directories

### MCP Servers (`mcp-servers/`)

Each MCP server is an independent TypeScript project:

```
mcp-servers/ghl-api-server/
├── src/
│   ├── index.ts              # FastMCP server setup
│   ├── auth/
│   │   ├── oauth.ts          # OAuth 2.0 manager
│   │   └── token-store.ts    # Encrypted token storage
│   ├── tools/
│   │   ├── workflows.ts      # Workflow operations
│   │   ├── contacts.ts       # Contact management
│   │   ├── funnels.ts        # Funnel tools
│   │   └── calendars.ts      # Calendar operations
│   └── utils/
│       ├── rate-limiter.ts   # API rate limiting
│       ├── validators.ts     # Zod schemas
│       └── logger.ts         # Logging utility
├── dist/                     # Compiled JS
├── package.json
└── tsconfig.json
```

### Scripts (`scripts/`)

Knowledge base pipeline scripts:

```
scripts/
├── scrape-ghl-docs.js        # Step 1: Scrape GHL docs
├── extract-yt-transcripts.js # Step 2: Get YouTube content
├── chunk-documents.js        # Step 3: Semantic chunking
├── embed-content.js          # Step 4: Generate embeddings
├── build-knowledge-base.js   # Orchestrator: Runs all steps
└── utils/
    ├── chunker.js            # Chunking algorithm
    └── embedder.js           # Embedding generation
```

### Knowledge Base (`kb/`)

Structured content storage:

```
kb/
├── ghl-docs/
│   ├── raw/
│   │   ├── workflows.md
│   │   ├── contacts.md
│   │   └── api-reference.md
│   └── processed/
│       ├── workflows-chunk-001.json
│       ├── workflows-chunk-002.json
│       └── metadata.json
│
└── youtube-transcripts/
    ├── by-creator/
    │   ├── robb-bailey/
    │   │   ├── video-1-transcript.md
    │   │   └── video-2-transcript.md
    │   └── shaun-clark/
    │       └── video-1-transcript.md
    └── by-topic/
        ├── workflows/
        ├── funnels/
        └── api/
```

## Configuration Files

### `.claude/settings.local.json`

MCP server configuration for Claude Code:

```json
{
  "mcp": {
    "servers": {
      "ghl-api": {
        "command": "node",
        "args": ["./mcp-servers/ghl-api-server/dist/index.js"],
        "env": {
          "GHL_CLIENT_ID": "${GHL_CLIENT_ID}",
          "GHL_CLIENT_SECRET": "${GHL_CLIENT_SECRET}"
        }
      },
      "chroma-db": {
        "transport": "http",
        "url": "http://localhost:8000"
      }
    }
  }
}
```

### `package.json` Scripts

```json
{
  "scripts": {
    "scrape-docs": "node scripts/scrape-ghl-docs.js",
    "extract-yt": "node scripts/extract-yt-transcripts.js",
    "chunk-docs": "node scripts/chunk-documents.js",
    "build-kb": "node scripts/build-knowledge-base.js",
    "embed-content": "node scripts/embed-content.js",
    "start-chroma": "docker run -p 8000:8000 chromadb/chroma",
    "build-ghl-mcp": "cd mcp-servers/ghl-api-server && npm run build",
    "dev-ghl-mcp": "cd mcp-servers/ghl-api-server && npm run dev",
    "test-mcp": "node tests/mcp-servers/test-ghl-api.js",
    "test-kb": "node tests/knowledge-base/test-retrieval.js"
  }
}
```

## Development Workflow

1. **Start Chroma**: `npm run start-chroma`
2. **Build MCP servers**: `npm run build-ghl-mcp`
3. **Populate KB**: `npm run build-kb`
4. **Run tests**: `npm test`
5. **Start Claude Code**: IDE loads MCP servers from `.claude/settings.local.json`

---

**Note:** This structure will be created during Epic 1 (Story 1.1: Project Structure & Configuration)
