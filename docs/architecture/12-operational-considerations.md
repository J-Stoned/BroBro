# 12. Operational Considerations

### 12.1 Logging

**Structured Logging:**

```typescript
// mcp-servers/ghl-api-server/src/utils/logger.ts

import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({ format: winston.format.simple() })
  ]
});

// Usage
logger.info('Workflow created', { workflowId: 'wf_123', locationId: 'loc_456' });
logger.error('OAuth token refresh failed', { error: err.message });
```

### 12.2 Error Handling

**MCP Server Error Responses:**

```typescript
// Standardized error format

interface MCPError {
  code: string;
  message: string;
  details?: any;
  retryable: boolean;
}

try {
  const result = await ghlClient.workflows.create(config);
  return { success: true, data: result };
} catch (error) {
  if (error.status === 429) {
    return {
      success: false,
      error: {
        code: 'RATE_LIMIT_EXCEEDED',
        message: 'GoHighLevel API rate limit reached. Retrying in 10 seconds...',
        retryable: true
      }
    };
  }

  if (error.status === 401) {
    return {
      success: false,
      error: {
        code: 'AUTH_FAILED',
        message: 'OAuth token expired. Please re-authenticate.',
        retryable: false
      }
    };
  }

  // Generic error
  return {
    success: false,
    error: {
      code: 'UNKNOWN_ERROR',
      message: error.message,
      retryable: false
    }
  };
}
```

### 12.3 Monitoring & Health Checks

**MCP Server Health:**

```typescript
// Add health check tool to each MCP server

{
  name: 'health_check',
  description: 'Check server health and dependencies',
  parameters: {},
  handler: async () => {
    const checks = {
      server: 'ok',
      ghl_api: await checkGHLConnection(),
      oauth_token: await checkOAuthToken(),
      rate_limit: getRateLimitStatus()
    };

    return {
      status: Object.values(checks).every(v => v === 'ok' || v.status === 'ok') ? 'healthy' : 'degraded',
      checks
    };
  }
}
```

---
