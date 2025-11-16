# 4. Technical Assumptions

### 4.1 Repository Structure

**Repository Type:** Monorepo

All components (MCP servers, scripts, slash commands, knowledge base) reside in a single repository:
```
BroBro/
├── mcp-servers/          # Custom MCP server implementations
├── scripts/              # KB building, scraping, embedding scripts
├── kb/                   # Knowledge base content
├── config/               # Configuration files
├── .claude/commands/     # Slash command definitions
└── docs/                 # PRD, Architecture, user guides
```

**Rationale:** Simplifies dependency management, versioning, and deployment for a single-purpose project.

### 4.2 Service Architecture

**Architecture:** Modular Monolith with MCP Server Microservices

**Core Components:**
- **GHL API MCP Server** (TypeScript, stdio transport): Custom server for GoHighLevel API integration
- **Chroma Vector DB** (HTTP transport, Docker): Local vector database for embeddings
- **Memory Service MCP Server** (HTTP transport): Conversation context persistence
- **Knowledge Base Builder** (Node.js scripts): Offline scripts for scraping, chunking, embedding
- **Slash Commands** (Markdown): Declarative command definitions in `.claude/commands/`

**Rationale:** MCP architecture enables modularity while maintaining local-first deployment. Each server can be developed, tested, and upgraded independently.

### 4.3 Technology Stack

**Runtime & Languages:**
- Node.js 20+ (LTS)
- TypeScript 5.x for MCP servers (type safety, better IDE support)
- JavaScript (ES modules) for utility scripts

**MCP Framework:**
- FastMCP (TypeScript) for GHL API server
- Official MCP SDK for compatibility

**Vector Database:**
- Chroma (local deployment via Docker or Python)
- Alternative: Qdrant (if performance issues arise)

**Embeddings:**
- sentence-transformers/all-MiniLM-L6-v2 (384 dims, 14.7ms/1K tokens)
- Fallback: BGE-Base-v1.5 (if accuracy insufficient)

**GHL API Client:**
- @gohighlevel/api-client v2.2.1 (official SDK)
- OAuth 2.0 with automatic token refresh

**Content Acquisition:**
- Firecrawl MCP (documentation scraping)
- YouTube Transcript Pro MCP (transcript extraction)
- Docs Scraper MCP (specialized crawling)

**Development Tools:**
- BMAD-METHOD for agile development workflow
- ESLint + Prettier for code quality
- Jest for unit testing (MCP servers)

### 4.4 Testing Requirements

**Testing Strategy:** Unit + Integration Testing

**Unit Testing:**
- Jest for MCP server tools (workflows, contacts, funnels)
- Mocked GHL API responses for offline testing
- Test coverage target: 80%+ for MCP server tools

**Integration Testing:**
- End-to-end slash command tests with real knowledge base
- OAuth flow testing with test GHL account
- Vector search accuracy benchmarking

**Manual Testing:**
- User acceptance testing for slash commands
- Knowledge base query relevance validation
- Workflow configuration deployment to test GHL account

**Rationale:** Unit tests ensure MCP server reliability. Integration tests validate real-world usage. Manual testing verifies domain expertise quality.

### 4.5 Deployment & Infrastructure

**Deployment Model:** Local-First with Optional Cloud Path

**MVP (Local):**
- All components run on user's Windows machine
- Chroma via Docker Desktop
- MCP servers start automatically via Claude Code configuration
- No external dependencies beyond npm packages

**Future (Cloud-Ready):**
- Chroma deployed to cloud VM for multi-device access
- MCP servers deployed as HTTP endpoints (Azure Functions, AWS Lambda)
- Knowledge base synced to cloud storage

**Rationale:** Local deployment eliminates latency, cost, and privacy concerns for MVP. Architecture designed for cloud migration when needed.

### 4.6 Additional Technical Assumptions

**Assumption 1:** User has Docker Desktop or Python 3.9+ installed for running Chroma locally

**Assumption 2:** User has GoHighLevel Agency Pro account with API access and can generate OAuth credentials

**Assumption 3:** Firecrawl API budget of ~$50-100 is acceptable for one-time documentation scraping

**Assumption 4:** YouTube transcripts are available for target tutorial videos (fallback to manual if not)

**Assumption 5:** Claude Code supports MCP server configuration via `.claude/settings.local.json`

**Assumption 6:** GoHighLevel API v2.0 remains stable (no breaking changes) during development

**Assumption 7:** Semantic chunking with all-MiniLM-L6-v2 provides sufficient accuracy for domain-specific queries (will benchmark early)

---
