# BroBro - Next Session Action Plan

## 📊 Current Status

**Project:** 53% Complete (16/30 stories)
- ✅ Epic 1: Infrastructure & Setup (7/7 complete)
- ✅ Epic 2: Knowledge Base Assembly (5/5 complete)
- 🔄 **Epic 3: MCP Server Implementation (3/6 complete)**
  - ✅ Story 3.1: MCP Server Foundation
  - ✅ Story 3.2: OAuth 2.0 Authentication
  - ✅ Story 3.3: Rate Limiting & Error Handling
  - **→ Story 3.4: Workflow Management Tools (NEXT)**
  - ⏳ Story 3.5: Contact/Funnel/Calendar Tools
  - ⏳ Story 3.6: Production Deployment

---

## 🎯 Next Story: 3.4 - Workflow Management Tools

### Story Overview
Create MCP tools for complete GHL workflow operations (create, list, get, update, delete).

### Estimated Time
**3-4 hours** for complete implementation

### Prerequisites (Already Complete ✅)
- ✅ MCP Server running with FastMCP
- ✅ OAuth 2.0 authentication working
- ✅ Rate limiting active (100 req/10s, 200k/day)
- ✅ Error handler with retry logic
- ✅ Logger utility operational

---

## 📋 Implementation Plan for Story 3.4

### Phase 1: GHL API Client Setup (45 min)

**File to Create:** `src/api/ghl-client.ts`

**Tasks:**
1. Install @gohighlevel/api-client dependency (if not already)
2. Create GHL API client wrapper
3. Integrate with OAuth manager for token retrieval
4. Integrate with rate limiter for API calls
5. Add error handling for GHL-specific errors

**Code Pattern:**
```typescript
import { oauthManager } from '../auth/oauth-manager.js';
import { rateLimiter } from '../utils/rate-limiter.js';
import axios from 'axios';

export class GHLClient {
  private baseURL = 'https://services.leadconnectorhq.com';

  async request(method, endpoint, data?) {
    return await rateLimiter.execute(async () => {
      const token = await oauthManager.getAccessToken();
      return await axios({
        method,
        url: `${this.baseURL}${endpoint}`,
        headers: { Authorization: `Bearer ${token}` },
        data
      });
    });
  }
}
```

---

### Phase 2: Workflow Tools Implementation (90 min)

**File to Create:** `src/tools/workflows.ts`

**Tools to Implement:**

#### 1. `create_workflow`
```typescript
Parameters:
- locationId: string (required)
- name: string (required)
- trigger: object (required)
  - type: string (e.g., "form_submit", "tag_added")
  - config: object (trigger-specific settings)
- actions: array<object> (required)
  - type: string (e.g., "send_email", "wait")
  - config: object (action-specific settings)

Returns:
- workflowId: string
- status: string
- message: string
```

#### 2. `list_workflows`
```typescript
Parameters:
- locationId: string (required)
- status?: string (optional: "active", "inactive", "draft")
- limit?: number (optional, default: 100)

Returns:
- workflows: array<{id, name, status, trigger, createdAt, updatedAt}>
- total: number
```

#### 3. `get_workflow`
```typescript
Parameters:
- workflowId: string (required)

Returns:
- id: string
- name: string
- locationId: string
- status: string
- trigger: object
- actions: array<object>
- metadata: object
```

#### 4. `update_workflow`
```typescript
Parameters:
- workflowId: string (required)
- changes: object (required)
  - name?: string
  - status?: string
  - trigger?: object
  - actions?: array<object>

Returns:
- workflowId: string
- status: string
- message: string
```

#### 5. `delete_workflow`
```typescript
Parameters:
- workflowId: string (required)
- confirm: boolean (required, must be true)

Returns:
- success: boolean
- workflowId: string
- message: string
```

---

### Phase 3: Tool Registration (20 min)

**File to Modify:** `src/index.ts`

**Tasks:**
1. Import workflow tools
2. Create `registerWorkflowTools()` function
3. Call registration function in server initialization
4. Update tool count in logging

**Code Pattern:**
```typescript
import {
  createWorkflowTool,
  listWorkflowsTool,
  getWorkflowTool,
  updateWorkflowTool,
  deleteWorkflowTool
} from './tools/workflows.js';

function registerWorkflowTools(server: FastMCP): void {
  server.addTool({
    name: createWorkflowTool.name,
    description: createWorkflowTool.description,
    parameters: createWorkflowTool.schema,
    execute: createWorkflowTool.handler
  });
  // ... repeat for all 5 tools

  logger.info('Workflow tools registered', {
    tools: ['create_workflow', 'list_workflows', 'get_workflow',
            'update_workflow', 'delete_workflow']
  });
}
```

---

### Phase 4: Testing & Validation (45 min)

**Manual Testing Checklist:**

1. **Build Test**
   ```bash
   cd mcp-servers/ghl-api-server
   npm run build
   # Should compile with 0 errors
   ```

2. **OAuth Setup** (if not done already)
   - Create GHL Marketplace app
   - Configure OAuth credentials in `.env`
   - Run `authenticate_ghl` tool
   - Verify `.tokens.enc` created

3. **Workflow Operations Test**
   ```bash
   # Test 1: Create workflow
   create_workflow --locationId="YOUR_LOCATION_ID" --name="Test Workflow" ...

   # Test 2: List workflows
   list_workflows --locationId="YOUR_LOCATION_ID"

   # Test 3: Get workflow
   get_workflow --workflowId="WORKFLOW_ID_FROM_CREATE"

   # Test 4: Update workflow
   update_workflow --workflowId="WORKFLOW_ID" --changes='{...}'

   # Test 5: Delete workflow
   delete_workflow --workflowId="WORKFLOW_ID" --confirm=true
   ```

4. **Rate Limiting Validation**
   - Create 150 workflows rapidly
   - Verify rate limiter queues requests after 100
   - Check `get_rate_limit_status` shows correct stats

5. **Error Handling Test**
   - Test with invalid locationId (should get friendly error)
   - Test with missing OAuth token (should prompt to authenticate)
   - Test with invalid workflow data (should show validation errors)

---

### Phase 5: Documentation (30 min)

**Files to Update:**

1. **Story 3.4 Status**
   - Update `docs/stories/3.4.story.md` status to "Complete"
   - Fill in Dev Agent Record section
   - Document completion notes

2. **README Update**
   - Add workflow tools to available tools list
   - Add usage examples
   - Update tool count (9 → 14 tools)

3. **Create Workflow Examples**
   - File: `mcp-servers/ghl-api-server/examples/workflows.md`
   - Include common workflow patterns
   - Show trigger and action configurations

---

## 🔧 Technical Details

### GHL API Endpoints (Story 3.4)

```
Base URL: https://services.leadconnectorhq.com

POST   /workflows                    # Create workflow
GET    /workflows?locationId=X       # List workflows
GET    /workflows/{workflowId}       # Get workflow
PUT    /workflows/{workflowId}       # Update workflow
DELETE /workflows/{workflowId}       # Delete workflow
```

### Authentication
- OAuth 2.0 Bearer token (managed by OAuth manager)
- Auto-refresh handles token expiry
- Rate limiter ensures API compliance

### Error Handling
- 401: Token expired → Trigger auto-refresh
- 403: Insufficient permissions → User-friendly message
- 404: Workflow not found → Clear error
- 429: Rate limit → Queue request with backoff
- 5xx: Server error → Retry with exponential backoff

---

## 📁 Files to Create/Modify

### New Files (2)
1. `src/api/ghl-client.ts` - GHL API client wrapper
2. `src/tools/workflows.ts` - 5 workflow MCP tools

### Modified Files (2)
3. `src/index.ts` - Register workflow tools
4. `docs/stories/3.4.story.md` - Update status to Complete

### Documentation Files (2)
5. `mcp-servers/ghl-api-server/README.md` - Add workflow tools
6. `mcp-servers/ghl-api-server/examples/workflows.md` - Usage examples

---

## ✅ Success Criteria

Story 3.4 is complete when:

1. ✅ All 5 workflow tools implemented
2. ✅ TypeScript compiles with 0 errors
3. ✅ Tools registered in MCP server
4. ✅ Integration with OAuth manager working
5. ✅ Integration with rate limiter working
6. ✅ Error handling comprehensive
7. ✅ Manual testing passed (all 5 operations work)
8. ✅ Documentation updated
9. ✅ Story 3.4 marked Complete

---

## 🚀 Quick Start Commands

```bash
# Navigate to server directory
cd "c:\Users\justi\BroBro\mcp-servers\ghl-api-server"

# Install any missing dependencies
npm install @gohighlevel/api-client

# Start development
# 1. Create GHL API client: src/api/ghl-client.ts
# 2. Create workflow tools: src/tools/workflows.ts
# 3. Register tools: update src/index.ts
# 4. Build: npm run build
# 5. Test: npm run start (then test tools in Claude)
```

---

## 📊 Expected Outcomes

After Story 3.4 completion:

- **Total Stories:** 17/30 (57% complete)
- **Epic 3 Progress:** 4/6 stories (67% complete)
- **MCP Tools:** 9 → 14 tools (5 new workflow tools)
- **Lines of Code:** ~4,700 total (+ ~800 for Story 3.4)
- **Functionality:** Full workflow CRUD operations via MCP

---

## 🔄 After Story 3.4

### Next: Story 3.5 - Contact, Funnel, Calendar Tools (4-5 hours)

Similar pattern to Story 3.4:
- Create `src/tools/contacts.ts` - Contact management
- Create `src/tools/funnels.ts` - Funnel operations
- Create `src/tools/calendars.ts` - Calendar integration
- ~15 more tools total
- Same integration with OAuth + rate limiter

### Then: Story 3.6 - Production Deployment (2-3 hours)

- HTTP transport configuration
- Production optimizations
- Deployment documentation
- **Epic 3 COMPLETE**

---

## 💡 Tips for Next Session

1. **Reference OAuth + Rate Limiter patterns** from Stories 3.2 and 3.3
2. **Copy tool structure** from `src/tools/auth.ts` or `src/tools/rate-limit.ts`
3. **Test incrementally** - Don't wait until all 5 tools are done
4. **Use GHL API docs** - https://highlevel.stoplight.io/docs/integrations/
5. **Check rate limits** regularly during testing

---

**Ready to start Story 3.4? You have all the foundation in place!** 🎉
