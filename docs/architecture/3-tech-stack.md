# 3. Tech Stack

### 3.1 Complete Technology Specification

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Runtime** | Node.js | 20+ LTS | Long-term support, excellent TypeScript/async support, large MCP ecosystem |
| **Languages** | TypeScript | 5.x | Type safety for MCP servers, better IDE support, reduced bugs |
| | JavaScript (ES Modules) | ES2022 | Scripts and utilities, simpler for batch processing |
| **MCP Framework** | FastMCP (TypeScript) | Latest | Zero boilerplate, Zod validation, built on official SDK, production-ready |
| | @modelcontextprotocol/sdk | Latest | Official SDK for compatibility and standards compliance |
| **Vector Database** | Chroma | Latest | Lightweight, local-first, excellent Python/JS clients, fast setup |
| **Embedding Model** | all-MiniLM-L6-v2 | Latest | 384 dims, 14.7ms/1K tokens, 84% accuracy, perfect for domain queries |
| | (Fallback: BGE-Base-v1.5) | Latest | If accuracy insufficient, higher quality (87%+) at cost of speed |
| **GHL API Client** | @gohighlevel/api-client | 2.2.1 | Official SDK, OAuth 2.0, auto token refresh, comprehensive endpoint coverage |
| **Content Scraping** | Firecrawl MCP | Latest | Robust documentation scraping, sitemap support, rate limiting |
| | Docs Scraper MCP | Latest | Specialized for doc sites, handles complex navigation |
| **YouTube Extraction** | YouTube Transcript Pro | Latest | Production-ready, 4 tools, hybrid architecture (Data API + yt-dlp) |
| | YouTube Intelligence Suite | Latest | Fallback, 8 tools, smart format handling, no API key required |
| **Memory/Context** | Memory Service MCP | Latest | Conversation persistence, session management |
| **Validation** | Zod | Latest | Schema validation for MCP tool inputs, runtime type checking |
| **Testing** | Jest | Latest | Unit/integration tests for MCP servers, wide TypeScript support |
| **Build Tools** | TypeScript Compiler (tsc) | Latest | Compile TS to JS for MCP servers |
| | npm scripts | N/A | Build orchestration, task running |
| **Container Runtime** | Docker Desktop | Latest | Run Chroma in isolated container on Windows |
| **Development** | BMAD-METHOD | 4.x | Agile AI development workflow, systematic story-driven development |
| | ESLint | Latest | Code quality, consistency |
| | Prettier | Latest | Code formatting |
| **IDE Integration** | Claude Code | Latest | Primary user interface, MCP server orchestration |

### 3.2 Alternative Technologies Considered

| Decision | Alternatives Considered | Rationale for Choice |
|----------|------------------------|---------------------|
| **Vector DB** | Qdrant, Pinecone, Weaviate | **Chroma**: Simplest local setup on Windows, Python/JS clients, adequate performance for 10k+ vectors |
| **Embedding Model** | OpenAI Ada-002, BGE-M3, E5-Base | **all-MiniLM-L6-v2**: Fastest (14.7ms/1K), local (no API costs), sufficient accuracy for domain-specific |
| **MCP Framework** | Official SDK only, Custom implementation | **FastMCP**: Reduces boilerplate by 80%, Zod validation, TypeScript-first, rapid development |
| **Chunking** | Fixed-size, Recursive character, LangChain splitters | **Semantic chunking**: Preserves context, respects document structure, best for technical docs |
| **Content Scraping** | Puppeteer, Playwright, Cheerio | **Firecrawl MCP**: Built for docs, handles SPAs, rate limiting, MCP integration out-of-box |

---
