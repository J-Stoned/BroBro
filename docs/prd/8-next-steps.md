# 8. Next Steps

### 8.1 UX Expert Prompt

_Note: UX Expert involvement is minimal for this CLI-based project. If a future web UI is planned, invoke:_

```
/ux-expert

Please review the PRD for GHL Wiz (docs/prd.md) and create a UX specification
for a potential web-based interface. Focus on command discoverability,
search result presentation, and workflow configuration visualization.
```

### 8.2 Architect Prompt

```
/architect

Please review the PRD for GHL Wiz (docs/prd.md) and create a comprehensive
Architecture document that details:

1. System architecture diagram (MCP servers, vector DB, knowledge pipeline)
2. Data flow for knowledge base construction (scraping → chunking → embedding → indexing)
3. Request/response flow for slash commands (user query → KB search → response generation)
4. MCP server design for GHL API integration (OAuth, rate limiting, tools)
5. Technology stack justification and alternatives considered
6. Deployment architecture (local-first with cloud migration path)
7. Security considerations (OAuth token storage, API key management)
8. Performance optimization strategies (caching, lazy loading, batch processing)
9. Error handling and logging strategy
10. Future extensibility (adding more MCP servers, new slash commands, cloud deployment)

The architecture should be detailed enough for the Dev agent to implement
without ambiguity, while maintaining alignment with the PRD requirements.
```

---

**End of PRD**
