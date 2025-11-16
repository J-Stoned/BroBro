# 4. System Architecture

### 4.1 Component Architecture

```mermaid
graph LR
    subgraph "User Layer"
        U[User]
        CC[Claude Code]
    end

    subgraph "Command Layer"
        WF[/ghl-workflow]
        SRC[/ghl-search]
        API[/ghl-api]
        TUT[/ghl-tutorial]
        BP[/ghl-best-practice]
    end

    subgraph "MCP Servers"
        GHL[GHL API Server]
        CHR[Chroma Server]
        MEM[Memory Server]
        YT[YouTube Server]
        FC[Firecrawl Server]
    end

    subgraph "Data Stores"
        VDB[(Chroma Vector DB)]
        FS[File System<br/>kb/]
        CFG[Config & Tokens<br/>.env]
    end

    U -->|Writes command| CC
    CC -->|Routes to| WF
    CC -->|Routes to| SRC
    CC -->|Routes to| API

    WF -->|Query KB| CHR
    WF -->|Create workflow| GHL

    SRC -->|Semantic search| CHR
    SRC -->|Get context| MEM

    API -->|Call GHL API| GHL
    API -->|Get examples| CHR

    TUT -->|Search videos| CHR
    TUT -->|Extract new| YT

    CHR -->|Vector query| VDB
    GHL -->|OAuth| CFG
    GHL -->|HTTP| External_GHL_API
    YT -->|Fetch| External_YouTube
    FC -->|Scrape| External_GHL_Docs

    style CC fill:#bbdefb
    style VDB fill:#d1c4e9
    style External_GHL_API fill:#c8e6c9
```

### 4.2 MCP Server Design

#### 4.2.1 GHL API MCP Server

**Server ID:** `ghl-api`
**Transport:** stdio (local) → HTTP (future cloud)
**Framework:** FastMCP (TypeScript)
**Location:** `mcp-servers/ghl-api-server/`

**Tools Provided:**

```yaml
Tools:
  # Workflows
  - create_workflow:
      parameters:
        - locationId: string (required)
        - name: string (required)
        - trigger: object (required)
        - actions: array<object> (required)
      returns: { workflowId: string, status: string }

  - list_workflows:
      parameters:
        - locationId: string (required)
      returns: array<{id, name, status, trigger}>

  - get_workflow:
      parameters:
        - workflowId: string (required)
      returns: { id, name, trigger, actions, metadata }

  - update_workflow:
      parameters:
        - workflowId: string (required)
        - changes: object (required)
      returns: { workflowId, status }

  - delete_workflow:
      parameters:
        - workflowId: string (required)
      returns: { success: boolean }

  # Contacts
  - create_contact:
      parameters:
        - locationId: string
        - contact: object (email, name, phone, etc.)
      returns: { contactId, status }

  - search_contacts:
      parameters:
        - locationId: string
        - query: string
        - filters: object (optional)
      returns: array<Contact>

  - update_contact:
      parameters:
        - contactId: string
        - updates: object
      returns: { contactId, status }

  # Funnels
  - list_funnels:
      parameters:
        - locationId: string
      returns: array<{id, name, pages, status}>

  - get_funnel_pages:
      parameters:
        - funnelId: string
      returns: array<{pageId, name, url, type}>

  - create_funnel:
      parameters:
        - locationId: string
        - name: string
        - pages: array<object>
      returns: { funnelId, status }

  # Forms
  - list_forms:
      parameters:
        - locationId: string
      returns: array<{formId, name, fields}>

  - get_form_submissions:
      parameters:
        - formId: string
        - dateRange: object (optional)
      returns: array<Submission>

  # Calendars
  - list_calendars:
      parameters:
        - locationId: string
      returns: array<{calendarId, name, slots}>

  - create_appointment:
        parameters:
        - calendarId: string
        - contact: object
        - dateTime: string
      returns: { appointmentId, status }

  # Utilities
  - test_oauth:
      parameters: {}
      returns: { authenticated: boolean, tokenExpiry: string }
```

**OAuth 2.0 Implementation:**

```typescript
// mcp-servers/ghl-api-server/src/auth/oauth.ts

interface OAuthConfig {
  clientId: string;          // from GHL_CLIENT_ID env
  clientSecret: string;      // from GHL_CLIENT_SECRET env
  redirectUri: string;       // localhost callback
  tokenEndpoint: string;     // GHL token URL
}

interface TokenStore {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;         // Unix timestamp
}

class OAuth2Manager {
  private tokenStore: TokenStore;

  async getAccessToken(): Promise<string> {
    if (this.isTokenExpired()) {
      await this.refreshAccessToken();
    }
    return this.tokenStore.accessToken;
  }

  private isTokenExpired(): boolean {
    return Date.now() >= this.tokenStore.expiresAt - 300000; // 5 min buffer
  }

  private async refreshAccessToken(): Promise<void> {
    // Exchange refresh token for new access token
    // Update tokenStore
    // Persist to encrypted file
  }
}
```

**Rate Limiting:**

```typescript
// mcp-servers/ghl-api-server/src/utils/rate-limiter.ts

class RateLimiter {
  private requestQueue: Array<{fn: Function, resolve: Function}> = [];
  private burstLimit = 100;    // 100 req / 10 seconds
  private dailyLimit = 200000; // 200k req / day
  private requestWindow: number[] = [];

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    await this.checkLimits();
    this.recordRequest();
    return await fn();
  }

  private async checkLimits(): Promise<void> {
    // Remove requests outside 10-second window
    // Check if under burst limit
    // Check daily limit
    // Queue and delay if limits exceeded
  }
}
```

#### 4.2.2 Chroma Vector DB MCP Server

**Server ID:** `chroma-db`
**Transport:** HTTP (localhost:8000)
**Framework:** Official Chroma Python server
**Deployment:** Docker container

**Collections:**

```yaml
Collections:
  ghl-docs:
    embedding_dimension: 384
    metadata_schema:
      - doc_title: string
      - doc_url: string
      - section: string
      - category: string (workflows|funnels|api|etc)
      - last_updated: date

  ghl-tutorials:
    embedding_dimension: 384
    metadata_schema:
      - video_title: string
      - creator: string
      - video_url: string
      - timestamp: string
      - duration: integer
      - publish_date: date
      - topics: array<string>

  ghl-best-practices:
    embedding_dimension: 384
    metadata_schema:
      - practice_title: string
      - category: string
      - source: string
      - effectiveness: string (proven|experimental)

  ghl-snapshots:
    embedding_dimension: 384
    metadata_schema:
      - snapshot_name: string
      - marketplace: string (extendly|ghl-central|etc)
      - features: array<string>
      - pricing: string
      - use_cases: array<string>
```

**Query Interface:**

```typescript
// Queried via MCP tools
interface ChromaQuery {
  collection: 'ghl-docs' | 'ghl-tutorials' | 'ghl-best-practices' | 'ghl-snapshots';
  queryText: string;
  nResults?: number;        // default 5
  where?: object;           // metadata filters
  whereDocument?: object;   // document filters
}

// Example usage in slash command
const results = await chromaMCP.query({
  collection: 'ghl-tutorials',
  queryText: 'lead nurturing workflow automation',
  nResults: 5,
  where: { creator: 'Robb Bailey', topics: { $contains: 'workflows' } }
});
```

#### 4.2.3 YouTube MCP Servers

**Primary:** `youtube-transcript-pro`
**Fallback:** `youtube-intelligence`

**Tools:**

```yaml
youtube-transcript-pro:
  - get_transcript:
      parameters:
        - videoId: string
        - language: string (default: 'en')
      returns: { text: string, language: string }

  - get_timed_transcript:
      parameters:
        - videoId: string
      returns: array<{text, start, duration}>

  - get_video_info:
      parameters:
        - videoId: string
      returns: { title, creator, duration, publishDate }
```

#### 4.2.4 Firecrawl MCP Server

**Tools:**

```yaml
firecrawl:
  - scrape:
      parameters:
        - url: string
        - waitFor: integer (ms)
      returns: { markdown: string, html: string, metadata: object }

  - crawl:
      parameters:
        - url: string
        - maxPages: integer
        - includePaths: array<string>
      returns: { pages: array<{url, markdown}> }
```

---
