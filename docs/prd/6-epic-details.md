# 6. Epic Details

### Epic 1: Foundation & Local Knowledge Infrastructure

**Epic Goal:**
Establish the foundational project structure with proper configuration, install and configure all required MCP servers (Chroma, Memory Service, Firecrawl, YouTube extractors), and create the offline script pipeline for knowledge base construction including scraping, chunking, and embedding generation.

#### Story 1.1: Project Structure & Configuration Setup

**As a** developer,
**I want** a well-organized project structure with configuration files,
**so that** the codebase is maintainable and all components have clear locations.

**Acceptance Criteria:**
1. Directory structure created with folders: `mcp-servers/`, `scripts/`, `kb/`, `config/`, `docs/`
2. `package.json` configured with Node.js 20+, ES modules, and core dependencies
3. TypeScript configuration (`tsconfig.json`) created for MCP server development
4. `.gitignore` includes `node_modules/`, `.env`, `chroma_db/`, knowledge base raw files
5. `.env.example` template created with placeholders for GHL OAuth, Firecrawl API key
6. README.md created with project overview and setup instructions

#### Story 1.2: Chroma Vector Database Setup

**As a** developer,
**I want** Chroma vector database running locally,
**so that** I can store and query embeddings for the knowledge base.

**Acceptance Criteria:**
1. Docker Desktop installed and running on Windows
2. Chroma container running on `localhost:8000` with persistent volume
3. Chroma collections created: `ghl-docs`, `ghl-tutorials`, `ghl-best-practices`, `ghl-snapshots`
4. Chroma MCP server configured in `.claude/settings.local.json`
5. Test connection to Chroma via MCP tool succeeds
6. Documentation includes instructions for starting/stopping Chroma

#### Story 1.3: Memory Service MCP Server Configuration

**As a** user,
**I want** conversation context to persist across interactions,
**so that** the assistant remembers previous questions and provides coherent multi-turn conversations.

**Acceptance Criteria:**
1. Memory Service MCP server installed (HTTP transport)
2. Configured in `.claude/settings.local.json` with correct URL
3. Test memory storage and retrieval via simple commands
4. Memory persists across Claude Code restarts
5. Memory can be cleared manually when needed

#### Story 1.4: Content Acquisition MCP Servers Setup

**As a** developer,
**I want** Firecrawl and YouTube MCP servers installed,
**so that** I can scrape GHL documentation and extract tutorial transcripts.

**Acceptance Criteria:**
1. Firecrawl MCP server installed with API key configured
2. YouTube Transcript Pro MCP server installed
3. YouTube Video Intelligence Suite MCP (fallback) installed
4. Test scrape of single GHL doc page succeeds
5. Test YouTube transcript extraction from sample video succeeds
6. MCP servers configured in `.claude/settings.local.json`

#### Story 1.5: Knowledge Base Pipeline Scripts Foundation

**As a** developer,
**I want** foundational Node.js scripts for KB pipeline,
**so that** I can orchestrate scraping, chunking, and embedding workflows.

**Acceptance Criteria:**
1. `scripts/scrape-ghl-docs.js` created with Firecrawl integration
2. `scripts/extract-yt-transcripts.js` created with YouTube MCP integration
3. `scripts/chunk-documents.js` created with semantic chunking logic (512 tokens, 10% overlap)
4. `scripts/embed-content.js` created with all-MiniLM-L6-v2 integration
5. `scripts/build-knowledge-base.js` created as orchestration script
6. All scripts accept CLI arguments for configuration (input/output paths, limits)
7. Scripts log progress and errors to console and file

#### Story 1.6: YouTube Sources Configuration File

**As a** knowledge curator,
**I want** a configuration file to manage YouTube content sources,
**so that** I can easily specify which creators, videos, and playlists to scrape for the knowledge base.

**Acceptance Criteria:**
1. `kb/youtube-sources.json` configuration file created with complete schema
2. Template includes sections for: creators (channels), specific videos, playlists
3. Creator schema includes: name, channelId, maxVideos, topics, priority
4. Example sources pre-populated: Robb Bailey, Shaun Clark, GHL Official
5. Documentation added to README explaining how to add/update sources
6. JSON schema validated (well-formed, no syntax errors)
7. `scripts/extract-yt-transcripts.js` configured to read from this file

---

### Epic 2: Knowledge Base Population & Indexing

**Epic Goal:**
Execute the complete knowledge base construction pipeline: scrape all official GoHighLevel documentation, extract 50-100 YouTube tutorial transcripts, apply semantic chunking, generate embeddings using all-MiniLM-L6-v2, and populate Chroma vector database with fully indexed and searchable content.

#### Story 2.1: GoHighLevel Documentation Scraping

**As a** knowledge curator,
**I want** all official GHL documentation scraped and saved,
**so that** the knowledge base covers 100% of platform features.

**Acceptance Criteria:**
1. Firecrawl crawls help.gohighlevel.com sitemap completely
2. Firecrawl crawls marketplace.gohighlevel.com/docs/ (API docs)
3. Raw HTML/Markdown saved to `kb/ghl-docs/raw/`
4. Metadata extracted: page title, URL, category, last updated date
5. Total pages scraped: 500+ (verify coverage)
6. Failed pages logged for manual review
7. Scraping respects robots.txt and rate limits

#### Story 2.2: YouTube Tutorial Curation & Extraction

**As a** knowledge curator,
**I want** transcripts from 50-100 curated GHL tutorial videos,
**so that** the knowledge base includes visual learning content and expert insights.

**Acceptance Criteria:**
1. `kb/youtube-sources.json` reviewed and populated with 50-100 videos from Robb Bailey, Shaun Clark, other verified experts
2. `scripts/extract-yt-transcripts.js` reads configuration file and processes all sources
3. Videos categorized by topic: workflows, funnels, SaaS mode, API, best practices
4. Transcripts extracted using YouTube Transcript Pro MCP
5. Fallback to YouTube Intelligence Suite for videos with unavailable transcripts
6. Metadata saved: video title, creator, URL, duration, publish date, category
7. Transcripts saved to `kb/youtube-transcripts/by-creator/` and `/by-topic/`
8. Index file (`kb/youtube-transcripts/index.json`) created with all metadata
9. Failed extractions logged to `kb/youtube-transcripts/failed.log` for manual review

#### Story 2.3: Best Practices & Snapshot Reference Curation

**As a** knowledge curator,
**I want** curated best practices and snapshot marketplace information indexed,
**so that** users get expert guidance on workflows, SaaS mode, and snapshot selection.

**Acceptance Criteria:**
1. Best practices documented for: lead nurturing, appointment automation, form optimization, SaaS setup
2. Snapshot marketplace information compiled: Extendly, GHL Central, Snapshot Marketplace
3. Each snapshot profile includes: name, features, pricing, use cases, reviews
4. Files saved to `kb/best-practices/` and `kb/snapshots-reference/`
5. Content formatted in structured Markdown for easy parsing
6. Source citations included for all information

#### Story 2.4: Semantic Chunking Pipeline

**As a** developer,
**I want** all knowledge base content chunked using semantic chunking strategy,
**so that** embeddings preserve context and search accuracy is maximized.

**Acceptance Criteria:**
1. Semantic chunking implemented with 512-token chunks, 10% overlap (51 tokens)
2. Documents split on semantic boundaries (headings, paragraphs, code blocks)
3. Chunks include metadata: document title, section, chunk index, total chunks
4. Special handling for code examples (preserved as single chunks)
5. Processed chunks saved to `kb/*/processed/`
6. Total chunks generated: 10,000+ (verify coverage)
7. Chunk quality validated via manual review of 50 random samples

#### Story 2.5: Embedding Generation & Chroma Indexing

**As a** developer,
**I want** embeddings generated for all chunks and indexed in Chroma,
**so that** semantic search is fast and accurate.

**Acceptance Criteria:**
1. all-MiniLM-L6-v2 model loaded and initialized
2. Embeddings generated for all processed chunks (384 dimensions)
3. Embeddings uploaded to Chroma collections: `ghl-docs`, `ghl-tutorials`, `ghl-best-practices`, `ghl-snapshots`
4. Metadata indexed with embeddings for filtering and source attribution
5. Embedding generation time: <20ms per chunk (benchmark)
6. Test semantic search query returns relevant results with 90%+ accuracy
7. Total vectors in Chroma: 10,000+ across all collections

---

### Epic 3: Custom GHL API MCP Server

**Epic Goal:**
Build a production-ready TypeScript MCP server using FastMCP framework that implements OAuth 2.0 authentication with automatic token refresh, respects GoHighLevel API rate limits (100 req/10s, 200k/day), and provides MCP tools for creating/managing workflows, contacts, funnels, forms, calendars, and snapshots.

#### Story 3.1: GHL API MCP Server Foundation

**As a** developer,
**I want** a TypeScript MCP server with proper project structure and FastMCP integration,
**so that** I can build GHL API tools on a solid foundation.

**Acceptance Criteria:**
1. `mcp-servers/ghl-api-server/` directory created with TypeScript project
2. `package.json` includes FastMCP, @gohighlevel/api-client, Zod for validation
3. `tsconfig.json` configured for ES2022, strict type checking
4. `src/index.ts` created with FastMCP server initialization
5. Server supports both stdio (dev) and HTTP (future) transports
6. Build script compiles TypeScript to `dist/`
7. Server starts successfully and responds to MCP handshake

#### Story 3.2: OAuth 2.0 Authentication Implementation

**As a** user,
**I want** seamless OAuth 2.0 authentication with GoHighLevel,
**so that** API tools work without manual token management.

**Acceptance Criteria:**
1. OAuth 2.0 flow implemented: authorization code exchange for access token
2. Client ID and Client Secret loaded from environment variables
3. Access tokens auto-refresh before 24-hour expiry
4. Tokens stored securely in encrypted local file (not .env or git)
5. `test_oauth` tool added to verify connection and refresh flow
6. OAuth errors logged with clear troubleshooting messages
7. Documentation includes OAuth setup guide with GHL marketplace screenshots

#### Story 3.3: Rate Limiting & Error Handling

**As a** developer,
**I want** robust rate limiting and error handling,
**so that** the MCP server respects GHL API limits and gracefully handles failures.

**Acceptance Criteria:**
1. Rate limiter implemented: max 100 requests per 10 seconds
2. Daily limit tracker: max 200,000 requests per day
3. Requests queued when limits approached, with exponential backoff
4. Retry logic for transient errors (3 attempts with backoff)
5. Meaningful error messages for OAuth failures, rate limits, invalid requests
6. All errors logged with timestamp, endpoint, request details
7. MCP tool errors return structured error objects (not raw exceptions)

#### Story 3.4: Workflow Management Tools

**As a** user,
**I want** MCP tools for GHL workflow operations,
**so that** I can create, list, update, and delete workflows programmatically.

**Acceptance Criteria:**
1. `create_workflow` tool: accepts name, trigger, actions; returns workflow ID
2. `list_workflows` tool: accepts locationId; returns array of workflows
3. `get_workflow` tool: accepts workflowId; returns full workflow configuration
4. `update_workflow` tool: accepts workflowId and changes; returns updated workflow
5. `delete_workflow` tool: accepts workflowId; confirms deletion
6. All tools validate inputs using Zod schemas
7. Tools tested with real GHL test account

#### Story 3.5: Contacts, Funnels, Forms, Calendars Tools

**As a** user,
**I want** MCP tools for contacts, funnels, forms, and calendars,
**so that** I can manage all major GHL entities via the assistant.

**Acceptance Criteria:**
1. **Contacts:** `create_contact`, `search_contacts`, `update_contact`, `get_contact`
2. **Funnels:** `list_funnels`, `get_funnel_pages`, `create_funnel`
3. **Forms:** `list_forms`, `get_form_submissions`
4. **Calendars:** `list_calendars`, `create_appointment`
5. All tools accept required parameters and return structured responses
6. Zod validation for all inputs
7. Integration tests cover all tools with test GHL account

#### Story 3.6: MCP Server Integration & Configuration

**As a** user,
**I want** the GHL API MCP server integrated with Claude Code,
**so that** slash commands can invoke API tools seamlessly.

**Acceptance Criteria:**
1. GHL API MCP server added to `.claude/settings.local.json`
2. Server configured with stdio transport for local development
3. Environment variables loaded from `.env` (GHL_CLIENT_ID, GHL_CLIENT_SECRET)
4. Server auto-starts when Claude Code opens project
5. Server logs visible in Claude Code MCP server panel
6. Test tool invocation from Claude Code succeeds (e.g., `list_workflows`)
7. Documentation includes troubleshooting guide for common MCP issues

---

### Epic 4: Slash Commands & User Interface

**Epic Goal:**
Create 15+ specialized slash commands organized by category (workflows, funnels, API, search, best practices) with inline help, examples, and integration with knowledge base and GHL API MCP server, providing a complete conversational interface for all GHL Wiz capabilities.

#### Story 4.1: Workflow Slash Commands

**As a** GHL user,
**I want** slash commands for workflow automation,
**so that** I can design, generate, and deploy workflows efficiently.

**Acceptance Criteria:**
1. `/ghl-workflow [goal]` - Interactive workflow designer with KB search for similar patterns
2. `/ghl-lead-nurture [niche]` - Lead nurturing automation generator with 2025 best practices
3. `/ghl-appointment` - Appointment reminder automation (24hr, 1hr, no-show follow-up)
4. Each command includes inline help with usage examples
5. Commands query `ghl-tutorials` and `ghl-best-practices` collections
6. Commands generate valid workflow JSON configurations
7. Commands offer to deploy workflows via `create_workflow` MCP tool

#### Story 4.2: Funnel & Form Slash Commands

**As a** GHL user,
**I want** slash commands for funnels and forms,
**so that** I can build high-converting pages with expert guidance.

**Acceptance Criteria:**
1. `/ghl-funnel [type]` - Funnel builder assistant with template suggestions
2. `/ghl-form [goal]` - Form optimization helper with conversion best practices
3. `/ghl-landing-page` - Landing page design guidance with examples
4. Commands search `ghl-docs` for latest funnel/form builder features
5. Commands reference YouTube tutorials for visual walkthroughs
6. Commands provide step-by-step checklists for implementation
7. Commands suggest A/B testing strategies

#### Story 4.3: API & Integration Slash Commands

**As a** developer,
**I want** slash commands for API integration,
**so that** I can quickly implement GHL API calls with proper authentication.

**Acceptance Criteria:**
1. `/ghl-api [operation]` - API integration assistant with endpoint discovery
2. `/ghl-oauth` - OAuth 2.0 setup guide with step-by-step instructions
3. `/ghl-test-endpoint [endpoint]` - Test API endpoints with sample data
4. Commands fetch endpoint docs from `ghl-docs` collection (API section)
5. Commands generate code examples (JavaScript, Python, cURL)
6. Commands use `test_oauth` MCP tool to validate authentication
7. Commands explain rate limits and error handling

#### Story 4.4: Knowledge Search Slash Commands

**As a** GHL user,
**I want** slash commands for searching the knowledge base,
**so that** I can find answers, tutorials, and best practices quickly.

**Acceptance Criteria:**
1. `/ghl-search [query]` - Semantic search across all collections with ranked results
2. `/ghl-tutorial [topic]` - Find YouTube tutorials with timestamps and summaries
3. `/ghl-best-practice [feature]` - Query curated best practices with rationale
4. Commands return top 5 results with snippets and source citations
5. Commands offer to expand results or refine query
6. Commands suggest related topics for exploration
7. Search queries complete in <2 seconds (95th percentile)

#### Story 4.5: Advanced Feature Slash Commands

**As a** GHL user,
**I want** slash commands for SaaS mode and snapshots,
**so that** I can configure advanced GHL features correctly.

**Acceptance Criteria:**
1. `/ghl-saas` - SaaS mode configuration guide (Stripe, plans, white label, rebilling)
2. `/ghl-snapshot [use-case]` - Snapshot marketplace guidance with recommendations
3. Commands search `ghl-best-practices` and `ghl-snapshots` collections
4. Commands provide setup checklists and common pitfall warnings
5. Commands reference official GHL docs for current feature status
6. Commands include cost/pricing considerations
7. Documentation includes real-world use case examples

#### Story 4.6: Slash Command Documentation & Help System

**As a** user,
**I want** comprehensive documentation for all slash commands,
**so that** I can discover features and use commands effectively.

**Acceptance Criteria:**
1. Each slash command includes frontmatter with description and examples
2. `/ghl-help` command lists all available commands with categories
3. `/ghl-help [command]` shows detailed help for specific command
4. README.md includes slash command reference table
5. Each command demonstrates usage with realistic example
6. Commands include "Did you mean?" suggestions for typos
7. Onboarding guide created for new users

---

### Epic 5: Testing, Documentation & Deployment

**Epic Goal:**
Validate end-to-end functionality of all components (knowledge base, MCP servers, slash commands) through comprehensive testing, create production-ready documentation including setup guide and user manual, benchmark system performance, and prepare the project for production use.

#### Story 5.1: Knowledge Base Quality Validation

**As a** quality engineer,
**I want** to validate knowledge base accuracy and search relevance,
**so that** users receive correct and helpful answers.

**Acceptance Criteria:**
1. Semantic search benchmark: 50 test queries with expected results
2. Search relevance score: 90%+ for top-3 results across test queries
3. Source attribution validated: all results include correct doc/video citations
4. Chunk coherence review: manual inspection of 100 random chunks
5. Missing content check: verify coverage of major GHL features (workflows, funnels, API, SaaS)
6. Tutorial quality review: validate 10 random YouTube transcripts for accuracy
7. Test report generated with benchmark results and improvement recommendations

#### Story 5.2: MCP Server Integration Testing

**As a** quality engineer,
**I want** to test all MCP servers end-to-end,
**so that** API tools and knowledge retrieval work reliably.

**Acceptance Criteria:**
1. OAuth flow tested: authorization code exchange, token refresh, expiry handling
2. Rate limiting tested: verify throttling at 100 req/10s and 200k/day limits
3. All GHL API tools tested with real test account (workflows, contacts, funnels, forms, calendars)
4. Error handling tested: invalid inputs, network failures, expired tokens
5. Chroma vector DB tested: query performance, metadata filtering, collection isolation
6. Memory Service tested: context persistence across sessions
7. Integration test suite created with Jest (80%+ coverage)

#### Story 5.3: Slash Command User Acceptance Testing

**As a** user,
**I want** all slash commands tested in realistic scenarios,
**so that** they provide valuable, accurate assistance.

**Acceptance Criteria:**
1. All 15+ slash commands tested with realistic use cases
2. Workflow commands tested: verify generated JSON is valid and deployable
3. Search commands tested: verify results are relevant and well-cited
4. API commands tested: verify code examples work with GHL API
5. Response time tested: 95% of knowledge queries under 2 seconds
6. User feedback collected: 5 test users try commands and report issues
7. Bug fixes completed for all critical issues found

#### Story 5.4: Performance Benchmarking & Optimization

**As a** quality engineer,
**I want** to benchmark system performance,
**so that** we meet non-functional requirements and identify optimization opportunities.

**Acceptance Criteria:**
1. Knowledge query latency benchmarked: p50, p95, p99 percentiles
2. Embedding generation speed benchmarked: verify 14.7ms/1K tokens for all-MiniLM
3. Chroma query performance benchmarked: measure QPS and latency at scale
4. MCP server startup time measured: verify auto-start completes in <5 seconds
5. Memory usage profiled: ensure Chroma + MCP servers stay under 4GB RAM
6. Optimization applied if benchmarks miss targets (e.g., switch to BGE embeddings if accuracy insufficient)
7. Performance report created with baseline metrics for future comparison

#### Story 5.5: Documentation & User Guide Creation

**As a** user,
**I want** comprehensive documentation,
**so that** I can set up GHL Wiz and use it effectively.

**Acceptance Criteria:**
1. **Setup Guide** created: prerequisites, installation steps, MCP configuration, OAuth setup
2. **User Guide** created: slash command reference, usage examples, best practices
3. **Developer Guide** created: MCP server architecture, knowledge base pipeline, extending functionality
4. **Troubleshooting Guide** created: common errors, MCP server issues, OAuth problems
5. All guides include screenshots, code examples, and clear step-by-step instructions
6. README.md updated with quick start, feature overview, and links to guides
7. Documentation reviewed by test users for clarity

#### Story 5.6: Production Readiness & Deployment Checklist

**As a** project owner,
**I want** a production-ready system,
**so that** I can use GHL Wiz reliably for real work.

**Acceptance Criteria:**
1. All tests passing (unit, integration, user acceptance)
2. All 15+ slash commands functional and documented
3. Knowledge base fully indexed with 50+ tutorials, 100% GHL docs coverage
4. MCP servers configured and auto-starting
5. OAuth credentials configured (production or test account)
6. Logs configured for debugging (file-based with rotation)
7. Deployment checklist completed: verify all components, create backup, tag v1.0 release
8. Post-deployment smoke test: test 3 critical workflows to verify system operational

---
