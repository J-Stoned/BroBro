# GHL Wiz - Project Brief

## Executive Summary

**Project Name:** GHL Wiz
**Type:** AI-Powered GoHighLevel Assistant with Local Knowledge Base
**Target Platform:** Claude Code (MCP-enabled)
**Primary Goal:** Create a comprehensive AI assistant that helps users build complete systems inside GoHighLevel including marketing automations, websites, workflows, funnels, forms, and API integrations.

## Problem Statement

GoHighLevel users face several challenges:
1. **Steep Learning Curve** - GHL has extensive features (workflows, funnels, forms, calendars, API) requiring significant time to master
2. **Scattered Documentation** - Information spread across official docs, YouTube tutorials, community forums
3. **Best Practices Discovery** - Difficulty finding current (2025) best practices and proven patterns
4. **Implementation Complexity** - Building workflows and automations requires understanding triggers, actions, and integration points
5. **API Integration Barriers** - OAuth 2.0 setup and API endpoint usage requires technical expertise

## Vision

GHL Wiz will be an intelligent assistant with deep domain expertise that:
- Answers any GHL-related question with context from official docs
- Suggests best practices based on 2025 industry standards
- Generates ready-to-use workflow configurations
- Provides step-by-step guidance for building funnels and forms
- Assists with API integration and OAuth setup
- References specific tutorial videos for visual learners

## Target Users

### Primary Users
1. **GHL Agency Owners** - Building client solutions, need fast answers and templates
2. **Marketing Automation Specialists** - Creating complex workflows and nurture sequences
3. **SaaS Mode Operators** - Setting up white-label GHL instances for resale

### Secondary Users
4. **Developers** - Integrating GHL via API v2.0
5. **GHL Consultants** - Teaching best practices to clients
6. **New GHL Users** - Learning the platform efficiently

## Key Features

### 1. Comprehensive Knowledge Base
- **Official Documentation**: Complete scrape of help.gohighlevel.com, marketplace.gohighlevel.com/docs
- **YouTube Tutorials**: Transcripts from top creators (Robb Bailey, Shaun Clark, etc.)
- **Best Practices**: Curated 2025 workflows, automation patterns, conversion tactics
- **Snapshot Reference**: Marketplace snapshot information (Extendly, GHL Central, etc.)

### 2. Specialized Slash Commands (15+)
**Workflows & Automations:**
- `/ghl-workflow` - Interactive workflow designer
- `/ghl-lead-nurture` - Lead nurturing automation generator
- `/ghl-appointment` - Appointment reminder automation

**Funnels & Websites:**
- `/ghl-funnel` - Funnel builder assistant
- `/ghl-form` - Form optimization helper
- `/ghl-landing-page` - Landing page design guidance

**API & Integration:**
- `/ghl-api` - API integration assistant
- `/ghl-oauth` - OAuth 2.0 setup guide
- `/ghl-test-endpoint` - Test API endpoints

**Knowledge & Learning:**
- `/ghl-search` - Knowledge base semantic search
- `/ghl-tutorial` - Find relevant video tutorials
- `/ghl-best-practice` - Query best practices database

**Advanced:**
- `/ghl-saas` - SaaS mode configuration
- `/ghl-snapshot` - Snapshot marketplace guidance

### 3. Custom MCP Servers
**GHL API MCP Server** (custom built):
- OAuth 2.0 authentication with auto-refresh
- Tools for: workflows, contacts, funnels, forms, calendars, snapshots
- Rate limiting (100 req/10s, 200k/day)
- Error handling and retry logic

**Knowledge Base MCP Servers**:
- Chroma vector database (local, fast)
- Memory Service (conversation context)
- txtai knowledge base (semantic graph)

**Content Acquisition MCP Servers**:
- Firecrawl (documentation scraping)
- YouTube Transcript Pro (tutorial extraction)
- Docs Scraper (specialized doc crawling)

### 4. RAG System Architecture
**Embedding Model:** all-MiniLM-L6-v2
- 384 dimensions
- 14.7ms/1K tokens (blazing fast)
- 84-85% accuracy (sufficient for domain-specific queries)

**Chunking Strategy:** Semantic chunking
- 512 tokens per chunk
- 10% overlap (51 tokens)
- Preserves context across boundaries

**Vector Collections:**
- `ghl-docs` - Official documentation
- `ghl-tutorials` - YouTube content
- `ghl-best-practices` - Curated guides
- `ghl-snapshots` - Marketplace information

## Technical Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│          Claude Code + Custom Slash Commands        │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │   MCP Server Layer   │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐   ┌────▼─────┐   ┌───▼────────┐
│ Vector │   │ YouTube  │   │  Web       │
│   DB   │   │ Content  │   │ Scraper    │
│(Chroma)│   │Extractor │   │(Firecrawl) │
└───┬────┘   └────┬─────┘   └───┬────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
          ┌────────▼─────────┐
          │ Knowledge Base   │
          │  - GHL Docs      │
          │  - Tutorials     │
          │  - Best Practices│
          └──────────────────┘
```

### Technology Stack
- **Runtime:** Node.js 20+
- **Language:** TypeScript (MCP servers), JavaScript (scripts)
- **Vector DB:** Chroma (local deployment)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **MCP Framework:** FastMCP (TypeScript)
- **GHL API:** @gohighlevel/api-client v2.2.1
- **Platform:** Claude Code (Windows)

## Success Criteria

### Functional Requirements
1. ✅ Answer 95%+ of GHL questions accurately with source citations
2. ✅ Generate usable workflow configurations that work in GHL
3. ✅ Provide API code examples for all major endpoints
4. ✅ Reference specific tutorial videos for complex topics
5. ✅ Create/update workflows via API successfully

### Non-Functional Requirements
1. **Performance:** <2 second response time for knowledge queries
2. **Accuracy:** 90%+ relevance for semantic search results
3. **Coverage:** 100% of official GHL docs indexed
4. **Freshness:** Best practices current as of 2025
5. **Usability:** Slash commands work without manual MCP server management

### Quality Metrics
- Knowledge base contains 50+ YouTube tutorial transcripts
- All 15+ slash commands functional and well-documented
- OAuth flow tested and working
- Zero critical bugs in MCP servers
- Documentation complete with examples

## Scope

### In Scope
- ✅ Complete GHL documentation scraping and indexing
- ✅ YouTube tutorial transcript extraction (50-100 videos)
- ✅ Custom GHL API MCP server development
- ✅ 15+ specialized slash commands
- ✅ Vector database setup and optimization
- ✅ RAG system with semantic search
- ✅ OAuth 2.0 implementation
- ✅ Best practices curation

### Out of Scope (for MVP)
- ❌ Web-based UI (CLI/IDE only for now)
- ❌ Multi-user support
- ❌ Cloud deployment
- ❌ Real-time GHL account monitoring
- ❌ Automated workflow deployment (manual review required)
- ❌ Mobile app

### Future Considerations
- Multi-language support (Spanish, Portuguese for LATAM market)
- Integration with Make.com/Zapier for extended automation
- Community-contributed workflow templates
- A/B testing suggestions for funnels
- GHL Marketplace app listing

## Constraints & Assumptions

### Technical Constraints
- Windows environment (user's OS)
- Local-first architecture (no cloud dependencies initially)
- Claude Code as primary interface
- GHL API rate limits: 100 req/10s, 200k req/day

### Assumptions
- User has GHL Agency Pro account (for API access)
- User can obtain OAuth credentials
- User has Docker or Python (for Chroma setup)
- Stable internet for documentation scraping
- YouTube transcripts available for target videos

### Budget Considerations
- Firecrawl API: ~$50-100 for documentation scraping (one-time)
- OpenAI API: Optional for enhanced chunking (~$10-20)
- Everything else: Free and open-source

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GHL API changes break integration | High | Medium | Version pinning, fallback to manual docs |
| YouTube transcripts unavailable | Medium | Low | Multiple extraction tools, manual backup |
| Embedding quality insufficient | Medium | Low | Benchmark early, switch to BGE if needed |
| Knowledge base too large for memory | High | Low | Chunking optimization, lazy loading |
| MCP server crashes | High | Medium | Error handling, auto-restart, logging |

## Timeline Estimate

### Phase 1: Foundation (Week 1-2)
- Project structure setup ✅
- BMAD integration ✅
- MCP server installation
- Chroma database setup

### Phase 2: Knowledge Base (Week 2-3)
- Documentation scraping
- YouTube transcript extraction
- Chunking and embedding generation
- Vector database population

### Phase 3: Custom Development (Week 3-4)
- GHL API MCP server development
- OAuth 2.0 implementation
- Tool creation (workflows, contacts, funnels)

### Phase 4: Slash Commands (Week 4-5)
- Create all 15+ slash commands
- Test with knowledge base
- Refine prompts and workflows

### Phase 5: Testing & Refinement (Week 5-6)
- End-to-end testing
- Quality assurance
- Documentation
- User guide creation

**Total Estimated Time:** 5-6 weeks

## Stakeholders

- **Product Owner:** Justin (project creator)
- **Development Team:** BMAD AI agents (Analyst, PM, Architect, SM, Dev, QA)
- **End Users:** GHL agency owners, automation specialists, developers

## References & Research

### Documentation Sources
- https://help.gohighlevel.com - Official support docs
- https://marketplace.gohighlevel.com/docs/ - API v2 documentation
- https://developers.gohighlevel.com/ - Developer community

### Key YouTube Creators
- Robb Bailey - GHL Platform Master
- Shaun Clark - GHL CEO, strategic insights
- (Additional 15-20 creators to be researched)

### Technical References
- BMAD-METHOD framework documentation
- Claude Code MCP documentation
- Chroma vector database guides
- FastMCP framework documentation
- GoHighLevel API v2 GitHub repo

## Next Steps

1. **Immediate:** Review and approve this project brief
2. **Planning Phase:**
   - Use BMAD `/pm` to generate comprehensive PRD
   - Use BMAD `/architect` to design detailed architecture
   - Use BMAD `/po` to shard into epics and stories
3. **Development Phase:**
   - Begin systematic implementation with BMAD `/sm` and `/dev`
   - Iterate with `/qa` for quality assurance

## Appendix

### Glossary
- **GHL:** GoHighLevel
- **MCP:** Model Context Protocol
- **RAG:** Retrieval-Augmented Generation
- **PRD:** Product Requirements Document
- **MVP:** Minimum Viable Product
- **OAuth:** Open Authorization standard
- **SaaS Mode:** White-label resale feature in GHL

### Related Documents
- `.bmad-core/user-guide.md` - BMAD workflow documentation
- `package.json` - Project dependencies
- `.claude/commands/BMad/` - Available BMAD agents and tasks

---

**Document Version:** 1.0
**Created:** October 25, 2025
**Author:** Claude (based on extensive research)
**Status:** Draft - Awaiting Approval
