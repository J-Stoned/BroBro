# 6. Request/Response Flows

### 6.1 Knowledge Query Flow

**User invokes:** `/ghl-search "lead nurturing workflow best practices"`

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode
    participant SlashCmd as /ghl-search
    participant MemoryMCP as Memory Service
    participant ChromaMCP as Chroma Server
    participant ChromaDB as Chroma Vector DB

    User->>ClaudeCode: /ghl-search "lead nurturing..."
    ClaudeCode->>SlashCmd: Execute command

    SlashCmd->>MemoryMCP: Get conversation context
    MemoryMCP-->>SlashCmd: Previous queries, preferences

    SlashCmd->>SlashCmd: Enhance query with context
    SlashCmd->>ChromaMCP: query({ collection: "all", text: "...", n: 5 })

    ChromaMCP->>ChromaDB: Embedding search (cosine similarity)
    ChromaDB-->>ChromaMCP: Top 5 results + metadata

    ChromaMCP-->>SlashCmd: Results with sources
    SlashCmd->>SlashCmd: Format response with citations

    SlashCmd-->>ClaudeCode: Markdown response
    ClaudeCode-->>User: Display formatted answer

    SlashCmd->>MemoryMCP: Store query + results
```

**Latency Budget:**
- Embedding generation: ~15ms
- Vector search: ~50ms
- Result formatting: ~10ms
- **Total: ~75ms** (well under 2 second requirement)

### 6.2 Workflow Creation Flow

**User invokes:** `/ghl-workflow "create lead nurture for real estate"`

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode
    participant WorkflowCmd as /ghl-workflow
    participant ChromaMCP as Chroma Server
    participant GHLMCP as GHL API Server
    participant GHLAPI as GoHighLevel API

    User->>ClaudeCode: /ghl-workflow "lead nurture real estate"
    ClaudeCode->>WorkflowCmd: Execute

    WorkflowCmd->>ChromaMCP: Search similar workflows
    WorkflowCmd->>ChromaMCP: query(collection: "ghl-best-practices", text: "...")
    ChromaMCP-->>WorkflowCmd: Workflow patterns + examples

    WorkflowCmd->>WorkflowCmd: Generate workflow JSON config
    WorkflowCmd-->>User: Present config + explanation

    User->>WorkflowCmd: "Approve and deploy"

    WorkflowCmd->>GHLMCP: create_workflow(locationId, config)
    GHLMCP->>GHLMCP: Get OAuth token (refresh if needed)
    GHLMCP->>GHLAPI: POST /workflows
    GHLAPI-->>GHLMCP: {workflowId: "abc123", status: "active"}

    GHLMCP-->>WorkflowCmd: Success response
    WorkflowCmd-->>User: "Workflow created! ID: abc123"
```

### 6.3 Tutorial Discovery Flow

**User invokes:** `/ghl-tutorial "SaaS mode setup"`

```mermaid
sequenceDiagram
    participant User
    participant TutCmd as /ghl-tutorial
    participant ChromaMCP
    participant ChromaDB

    User->>TutCmd: /ghl-tutorial "SaaS mode setup"

    TutCmd->>ChromaMCP: query({<br/>  collection: "ghl-tutorials",<br/>  text: "SaaS mode setup",<br/>  where: {topics: "saas-mode"}<br/>})

    ChromaMCP->>ChromaDB: Filtered vector search
    ChromaDB-->>ChromaMCP: Top videos with timestamps

    ChromaMCP-->>TutCmd: Results array

    TutCmd->>TutCmd: Format with video links + timestamps

    TutCmd-->>User: Markdown response:<br/>"1. 'SaaS Mode Guide' by Robb Bailey (12:30)<br/>   https://youtube.com/watch?v=...<br/>2. 'White Label Setup' by Shaun Clark (08:15)<br/>   ..."
```

---
