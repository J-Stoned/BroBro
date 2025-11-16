# BroBro Backend Routes Documentation

## Active Routes Summary

This document maps all active routes in the BroBro FastAPI backend as of 2025-11-16.

---

## 1. GHL Routes (`routes/ghl_routes.py`)
**Status:** Active
**Purpose:** GoHighLevel API integration
**Used By:** GHL API OAuth flows

**Endpoints:**
- `POST /api/ghl/oauth/authorize` - OAuth authorization
- `GET /api/ghl/oauth/callback` - OAuth callback handling
- `GET /api/ghl/validate-token` - Token validation

---

## 2. Workflow Routes (`routes/workflow_routes.py`)
**Status:** Active (Epic 12)
**Purpose:** Workflow management and execution
**Used By:** Frontend workflow builder and executor

**Endpoints:**
- `POST /api/workflows` - Create workflow
- `GET /api/workflows` - List workflows
- `GET /api/workflows/{id}` - Get workflow details
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/{id}/execute` - Execute workflow
- `GET /api/workflows/{id}/executions` - Get execution history

---

## 3. Analytics Routes (`routes/analytics_routes.py`)
**Status:** Active (Epic 13)
**Purpose:** Analytics and performance metrics tracking
**Used By:** Analytics dashboard, performance monitoring
**Note:** Analytics module fully initialized with MetricsCollector and AlertManager

**Endpoints:**
- `GET /api/analytics/metrics` - Get performance metrics
- `POST /api/analytics/events` - Log analytics event
- `GET /api/analytics/workflows` - Workflow performance analytics
- `GET /api/analytics/searches` - Search analytics
- `GET /api/analytics/alerts` - Alert history
- `GET /api/analytics/reports` - Generate reports

---

## 4. Workflow Testing Routes (`routes/workflow_testing_routes.py`)
**Status:** Active (Enhancement 5)
**Purpose:** Test workflows in sandbox environment
**Used By:** Workflow debugging and validation

**Endpoints:**
- `POST /api/workflows/test` - Test workflow
- `POST /api/workflows/validate` - Validate workflow syntax
- `POST /api/workflows/debug` - Debug workflow execution

---

## 5. Search Analytics Routes (`routes/search_analytics_routes.py`)
**Status:** Active (Enhancement 6)
**Purpose:** Search-specific analytics and logging
**Used By:** Search optimization, usage analytics

**Endpoints:**
- `POST /api/search/log` - Log search query
- `GET /api/search/analytics` - Get search analytics
- `GET /api/search/trending` - Trending searches

---

## 6. AI Generation Routes (`routes/ai_generation_routes.py`)
**Status:** Active (Enhancement 8)
**Purpose:** AI-powered content generation
**Used By:** Content creation features, email generation

**Endpoints:**
- `POST /api/ai/generate` - Generate content
- `POST /api/ai/refine` - Refine generated content
- `POST /api/ai/templates` - Content templates

---

## 7. Version Control Routes (`routes/version_control_routes.py`)
**Status:** Active (Enhancement 9)
**Purpose:** Version control for workflows and content
**Used By:** Undo/redo, version history

**Endpoints:**
- `GET /api/versions` - List versions
- `POST /api/versions/{id}/restore` - Restore version
- `GET /api/versions/{id}/diff` - Compare versions

---

## 8. Gemini Routes (`routes/gemini_routes.py`)
**Status:** Active (Primary - Google AI Integration)
**Purpose:** Gemini File Search integration (PRIMARY SEARCH MECHANISM)
**Used By:** Main chat/search endpoint, knowledge base queries

**Endpoints:**
- `POST /api/search` - Main search endpoint (uses Gemini)
- `POST /api/query` - Query knowledge base (legacy, redirects to /search)
- `GET /api/search/status` - Gemini connection status

---

## 9. Chat Endpoints (`main.py`)
**Status:** Active
**Purpose:** Main chat interface
**Used By:** Chat UI, desktop app, CLI

**Endpoints:**
- `POST /api/chat` - Main chat endpoint (Claude + Gemini File Search)
  - Rate Limited: 10 req/min
  - Authentication: Via API key in headers

---

## 10. Health & Status (`main.py`)
**Status:** Active
**Purpose:** System health monitoring
**Used By:** Load balancers, uptime monitoring

**Endpoints:**
- `GET /health` - Health check (minimal)
- `GET /api/status` - Detailed status (includes Gemini connection)

---

## WebSocket Routes
**Status:** Active

- `WS /ws/collaborate` - Real-time collaboration (Enhancement 9)

---

## Routes Summary Table

| Module | Status | Used By | Priority |
|--------|--------|---------|----------|
| ghl_routes.py | ✅ Active | OAuth flows | Medium |
| workflow_routes.py | ✅ Active | Workflow builder | High |
| analytics_routes.py | ✅ Active | Dashboard, metrics | High |
| workflow_testing_routes.py | ✅ Active | Testing | Low |
| search_analytics_routes.py | ✅ Active | Search optimization | Medium |
| ai_generation_routes.py | ✅ Active | Content generation | Medium |
| version_control_routes.py | ✅ Active | History/undo | Low |
| gemini_routes.py | ✅ Active | PRIMARY SEARCH | Critical |
| main.py (chat, health) | ✅ Active | All | Critical |

---

## Verified Dependencies
- **MetricsCollector** (analytics/metrics_collector.py): Used in analytics_routes.py ✅
- **AlertManager** (analytics/alert_manager.py): Used in analytics_routes.py ✅

---

## Notes

### Deprecated/Not Using Anymore
- **ChromaDB** - Replaced by Gemini File Search (April 2025)
  - All ChromaDB embed scripts archived to `_archive/legacy-root/old-scripts/`
  - Backend no longer imports chromadb
  - Desktop app backend updated to use Gemini

### Configuration
- CORS is hardcoded for localhost dev servers (line 148 in main.py)
  - TODO: Use environment variable for production CORS_ORIGINS

---

Last Updated: 2025-11-16
Verified By: Code Quality Review
