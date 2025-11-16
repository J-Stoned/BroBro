# 11. Testing Strategy

### 11.1 Unit Tests

**MCP Server Tools:**

```typescript
// tests/mcp-servers/ghl-api/workflows.test.ts

import { describe, it, expect, vi } from 'vitest';
import { createWorkflow } from '../../../mcp-servers/ghl-api-server/src/tools/workflows';

describe('GHL API MCP - Workflows', () => {
  it('should create workflow with valid config', async () => {
    const mockGHLClient = {
      workflows: {
        create: vi.fn().mockResolvedValue({ id: 'wf_123', status: 'active' })
      }
    };

    const result = await createWorkflow(mockGHLClient, {
      locationId: 'loc_456',
      name: 'Test Workflow',
      trigger: { type: 'form_submitted' },
      actions: [{ type: 'send_email', template: 'welcome' }]
    });

    expect(result.workflowId).toBe('wf_123');
    expect(mockGHLClient.workflows.create).toHaveBeenCalledTimes(1);
  });

  it('should handle rate limit errors', async () => {
    const mockGHLClient = {
      workflows: {
        create: vi.fn().mockRejectedValue({ status: 429, message: 'Rate limit' })
      }
    };

    await expect(createWorkflow(mockGHLClient, {...}))
      .rejects.toThrow('Rate limit exceeded');
  });
});
```

### 11.2 Integration Tests

**End-to-End Slash Command:**

```typescript
// tests/integration/search-command.test.ts

import { executeSlashCommand } from '../helpers/claude-code-mock';
import { chromaDB } from '../helpers/test-db';

describe('Integration: /ghl-search', () => {
  beforeAll(async () => {
    // Seed test database
    await chromaDB.collection('ghl-docs').add({
      ids: ['doc1'],
      documents: ['Workflows in GoHighLevel allow automation...'],
      metadatas: [{ title: 'Workflow Overview', url: 'https://...' }]
    });
  });

  it('should return relevant docs with citations', async () => {
    const response = await executeSlashCommand('/ghl-search', 'workflow automation');

    expect(response).toContain('Workflows in GoHighLevel');
    expect(response).toContain('Source: Workflow Overview');
    expect(response).toContain('https://');
  });

  it('should complete in under 2 seconds', async () => {
    const start = Date.now();
    await executeSlashCommand('/ghl-search', 'lead nurturing');
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(2000);
  });
});
```

### 11.3 Performance Benchmarks

**Query Latency Benchmark:**

```typescript
// tests/benchmarks/query-performance.test.ts

describe('Performance: Knowledge Base Queries', () => {
  it('should achieve p95 < 2 seconds for 100 queries', async () => {
    const latencies = [];

    for (let i = 0; i < 100; i++) {
      const start = Date.now();
      await chromaDB.query({
        collection: 'ghl-docs',
        queryText: generateRandomQuery(),
        nResults: 5
      });
      latencies.push(Date.now() - start);
    }

    const p95 = getPercentile(latencies, 0.95);
    expect(p95).toBeLessThan(2000);
  });
});
```

---
