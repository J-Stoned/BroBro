# 9. Performance Optimization

### 9.1 Query Optimization

**Caching Strategy:**

```typescript
// In-memory LRU cache for frequent queries
import LRU from 'lru-cache';

const queryCache = new LRU({
  max: 500,        // cache 500 queries
  ttl: 1000 * 60 * 60  // 1 hour TTL
});

async function cachedQuery(queryText: string, collection: string) {
  const cacheKey = `${collection}:${queryText}`;

  if (queryCache.has(cacheKey)) {
    return queryCache.get(cacheKey);
  }

  const results = await chromaDB.query({ collection, queryText });
  queryCache.set(cacheKey, results);

  return results;
}
```

**Lazy Loading:**

```typescript
// Load embeddings on-demand, not all at once
async function getEmbedding(text: string): Promise<number[]> {
  if (!embeddingModel) {
    embeddingModel = await loadModel('all-MiniLM-L6-v2');
  }
  return await embeddingModel.encode(text);
}
```

### 9.2 Batch Processing

**Knowledge Base Indexing:**

```javascript
// scripts/embed-content.js

const BATCH_SIZE = 100;

async function batchIndex(chunks) {
  for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
    const batch = chunks.slice(i, i + BATCH_SIZE);

    // Generate embeddings in parallel
    const embeddings = await Promise.all(
      batch.map(chunk => generateEmbedding(chunk.content))
    );

    // Batch insert to Chroma
    await chromaCollection.add({
      ids: batch.map(c => c.id),
      embeddings: embeddings,
      metadatas: batch.map(c => c.metadata),
      documents: batch.map(c => c.content)
    });

    console.log(`Indexed ${i + batch.length} / ${chunks.length}`);
  }
}
```

### 9.3 Performance Metrics

**Target Metrics:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query latency (p95) | <2 seconds | Time from slash command to response |
| Embedding generation | <20ms/chunk | all-MiniLM-L6-v2 inference time |
| Vector search | <100ms | Chroma query time for top-5 results |
| MCP server startup | <5 seconds | Time for all servers to be ready |
| Memory footprint | <4GB RAM | Chroma + all MCP servers + Node.js |
| Indexing throughput | >50 docs/min | Knowledge base pipeline |

**Monitoring:**

```javascript
// Simple performance logging
const performanceLog = {
  queryLatencies: [],
  embeddingTimes: [],

  logQuery(durationMs) {
    this.queryLatencies.push(durationMs);
    if (durationMs > 2000) {
      console.warn(`Slow query: ${durationMs}ms`);
    }
  },

  getP95() {
    const sorted = this.queryLatencies.sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length * 0.95)];
  }
};
```

---
