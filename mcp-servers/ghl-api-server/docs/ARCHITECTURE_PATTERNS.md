# Architecture Patterns - Quick Reference

This document provides copy-paste code patterns for the GHL API MCP Server implementation. All patterns follow the architecture defined in `docs/architecture/13-mcp-server-architecture.md`.

---

## Table of Contents

1. [Logger Patterns](#logger-patterns)
2. [Error Handling Patterns](#error-handling-patterns)
3. [FastMCP Tool Definition Patterns](#fastmcp-tool-definition-patterns)
4. [Zod Schema Patterns](#zod-schema-patterns)
5. [OAuth Patterns](#oauth-patterns) (Story 3.2+)
6. [Rate Limiting Patterns](#rate-limiting-patterns) (Story 3.3+)
7. [API Client Patterns](#api-client-patterns) (Story 3.4+)

---

## Logger Patterns

### Basic Logger Implementation

**File:** `src/utils/logger.ts`

```typescript
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

class Logger {
  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private formatMessage(level: LogLevel, message: string): string {
    return `[${this.formatTimestamp()}] [${level}] ${message}`;
  }

  log(level: LogLevel, message: string, ...args: any[]): void {
    const formattedMessage = this.formatMessage(level, message);

    if (level === LogLevel.ERROR) {
      console.error(formattedMessage, ...args);
    } else if (level === LogLevel.WARN) {
      console.warn(formattedMessage, ...args);
    } else {
      console.log(formattedMessage, ...args);
    }
  }

  debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }

  info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }

  warn(message: string, ...args: any[]): void {
    this.log(LogLevel.WARN, message, ...args);
  }

  error(message: string, error?: any): void {
    if (error) {
      this.log(LogLevel.ERROR, message, {
        message: error.message,
        stack: error.stack,
        ...error
      });
    } else {
      this.log(LogLevel.ERROR, message);
    }
  }
}

export const logger = new Logger();
```

### Logger Usage Examples

```typescript
import { logger } from './utils/logger.js';

// Simple info message
logger.info('Server starting...');

// Debug with context
logger.debug('Processing request', { userId: '123', action: 'create' });

// Warning
logger.warn('Rate limit approaching', { current: 95, limit: 100 });

// Error with exception
try {
  throw new Error('Something failed');
} catch (error) {
  logger.error('Operation failed', error);
}
```

---

## Error Handling Patterns

### Error Types Enum

**File:** `src/utils/errors.ts`

```typescript
export enum ErrorType {
  AUTHENTICATION = 'AUTHENTICATION_ERROR',
  RATE_LIMIT = 'RATE_LIMIT_ERROR',
  VALIDATION = 'VALIDATION_ERROR',
  NETWORK = 'NETWORK_ERROR',
  API = 'API_ERROR',
  UNKNOWN = 'UNKNOWN_ERROR'
}

export interface MCPError {
  type: ErrorType;
  message: string;
  details?: any;
  retryable: boolean;
}
```

### Error Handler Class

**File:** `src/utils/error-handler.ts`

```typescript
import { AxiosError } from 'axios';
import { ErrorType, MCPError } from './errors.js';
import { logger } from './logger.js';

export class ErrorHandler {
  static handleError(error: unknown): MCPError {
    logger.error('Handling error', error);

    // Axios HTTP errors
    if (error instanceof AxiosError) {
      const status = error.response?.status;

      // Authentication errors (401, 403)
      if (status === 401 || status === 403) {
        return {
          type: ErrorType.AUTHENTICATION,
          message: 'Authentication failed. Please re-authenticate with GoHighLevel.',
          details: error.response?.data,
          retryable: false
        };
      }

      // Rate limit errors (429)
      if (status === 429) {
        const retryAfter = error.response?.headers['retry-after'];
        return {
          type: ErrorType.RATE_LIMIT,
          message: `Rate limit exceeded. Retry after ${retryAfter || 'unknown'} seconds.`,
          details: { retryAfter },
          retryable: true
        };
      }

      // Validation errors (400, 422)
      if (status === 400 || status === 422) {
        return {
          type: ErrorType.VALIDATION,
          message: 'Invalid request parameters.',
          details: error.response?.data,
          retryable: false
        };
      }

      // Server errors (5xx)
      if (status && status >= 500) {
        return {
          type: ErrorType.API,
          message: 'GoHighLevel API server error. Please try again.',
          details: error.response?.data,
          retryable: true
        };
      }

      // Network errors
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        return {
          type: ErrorType.NETWORK,
          message: 'Network error. Check your internet connection.',
          details: { code: error.code },
          retryable: true
        };
      }
    }

    // Unknown errors
    return {
      type: ErrorType.UNKNOWN,
      message: error instanceof Error ? error.message : 'An unknown error occurred',
      details: error,
      retryable: false
    };
  }

  static formatForUser(error: MCPError): string {
    let message = `[${error.type}] ${error.message}`;

    if (error.details) {
      message += `\n\nDetails: ${JSON.stringify(error.details, null, 2)}`;
    }

    if (error.retryable) {
      message += '\n\nThis error is retryable. The request will be automatically retried.';
    }

    return message;
  }
}
```

### Error Handling in Tools

```typescript
import { ErrorHandler } from '../utils/error-handler.js';
import { logger } from '../utils/logger.js';

server.addTool({
  name: 'example_tool',
  description: 'Example with error handling',
  schema: z.object({ /* ... */ }),
  handler: async (params) => {
    try {
      // Your logic here
      const result = await someOperation();
      return { success: true, data: result };
    } catch (error) {
      const mcpError = ErrorHandler.handleError(error);
      logger.error('Tool execution failed', mcpError);

      return {
        success: false,
        error: ErrorHandler.formatForUser(mcpError)
      };
    }
  }
});
```

---

## FastMCP Tool Definition Patterns

### Minimal Tool (No Parameters)

```typescript
import { FastMCP } from 'fastmcp';
import { z } from 'zod';

const server = new FastMCP({ name: 'ghl-api', version: '1.0.0' });

server.addTool({
  name: 'test_connection',
  description: 'Test MCP server connection and verify server is running',
  schema: z.object({}),
  handler: async () => {
    return {
      status: 'connected',
      server: 'ghl-api',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    };
  }
});
```

### Tool with Simple Parameters

```typescript
server.addTool({
  name: 'get_workflow',
  description: 'Get detailed workflow configuration by ID',
  schema: z.object({
    workflowId: z.string().describe('The workflow ID to retrieve')
  }),
  handler: async (params) => {
    logger.info(`Fetching workflow: ${params.workflowId}`);

    // Your logic here
    const workflow = await fetchWorkflow(params.workflowId);

    return {
      success: true,
      workflow
    };
  }
});
```

### Tool with Complex Parameters

```typescript
const CreateWorkflowSchema = z.object({
  locationId: z.string()
    .optional()
    .describe('GHL location ID (defaults to authenticated location)'),
  name: z.string()
    .min(1)
    .max(100)
    .describe('Workflow name'),
  trigger: z.object({
    type: z.enum(['ContactCreated', 'ContactTagAdded', 'FormSubmitted']),
    filters: z.record(z.any()).optional()
  }).describe('Workflow trigger configuration'),
  actions: z.array(z.object({
    type: z.string(),
    settings: z.record(z.any())
  })).min(1).describe('Array of workflow actions'),
  status: z.enum(['draft', 'active'])
    .default('draft')
    .describe('Initial workflow status')
});

server.addTool({
  name: 'create_workflow',
  description: 'Create a new workflow in GoHighLevel',
  schema: CreateWorkflowSchema,
  handler: async (params) => {
    logger.info('Creating workflow', { name: params.name });

    try {
      const result = await createWorkflow(params);
      return {
        success: true,
        workflowId: result.id,
        name: result.name,
        status: result.status
      };
    } catch (error) {
      const mcpError = ErrorHandler.handleError(error);
      return {
        success: false,
        error: ErrorHandler.formatForUser(mcpError)
      };
    }
  }
});
```

### Organized Tool Registration Pattern

**File:** `src/tools/test.ts`

```typescript
import { FastMCP } from 'fastmcp';
import { z } from 'zod';
import { logger } from '../utils/logger.js';

export class TestTools {
  static register(server: FastMCP): void {
    server.addTool({
      name: 'test_connection',
      description: 'Test MCP server connection',
      schema: z.object({}),
      handler: async () => {
        logger.info('Test connection invoked');
        return {
          status: 'connected',
          server: 'ghl-api',
          version: '1.0.0',
          timestamp: new Date().toISOString()
        };
      }
    });
  }
}
```

**File:** `src/index.ts`

```typescript
import { FastMCP } from 'fastmcp';
import { TestTools } from './tools/test.js';
import { logger } from './utils/logger.js';

const server = new FastMCP({
  name: 'ghl-api',
  version: '1.0.0'
});

// Register tool categories
TestTools.register(server);

// Start server
logger.info('Starting GHL API MCP Server...');
server.start();
logger.info('Server started successfully on stdio transport');
```

---

## Zod Schema Patterns

### Common Field Types

```typescript
import { z } from 'zod';

// Required string
z.string()

// Optional string
z.string().optional()

// String with constraints
z.string().min(1).max(100)

// Email
z.string().email()

// URL
z.string().url()

// Enum
z.enum(['draft', 'active', 'inactive'])

// Number with range
z.number().min(1).max(100)

// Boolean with default
z.boolean().default(false)

// Array of strings
z.array(z.string())

// Array with min length
z.array(z.string()).min(1)

// Object with specific shape
z.object({
  name: z.string(),
  age: z.number()
})

// Record (key-value map)
z.record(z.any())
z.record(z.string(), z.number())

// Union types
z.union([z.string(), z.number()])

// Optional with description
z.string().optional().describe('User email address')
```

### Reusable Schema Patterns

```typescript
// Contact schema (reusable)
const ContactSchema = z.object({
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  email: z.string().email().optional(),
  phone: z.string().optional(),
  tags: z.array(z.string()).optional(),
  customFields: z.record(z.any()).optional()
});

// Use in tool
server.addTool({
  name: 'create_contact',
  description: 'Create a new contact',
  schema: z.object({
    locationId: z.string().optional(),
    contact: ContactSchema
  }),
  handler: async (params) => {
    // params.contact is fully typed!
    return { success: true };
  }
});
```

### Schema with Validation

```typescript
const WorkflowNameSchema = z.string()
  .min(1, 'Workflow name cannot be empty')
  .max(100, 'Workflow name must be less than 100 characters')
  .regex(/^[a-zA-Z0-9\s-_]+$/, 'Workflow name contains invalid characters');

// Use in schema
const CreateWorkflowSchema = z.object({
  name: WorkflowNameSchema,
  // ... other fields
});
```

---

## OAuth Patterns

*Note: These patterns are for Story 3.2+. Story 3.1 does not require OAuth.*

### OAuth Manager Class Structure

**File:** `src/auth/oauth-manager.ts`

```typescript
import crypto from 'crypto';
import fs from 'fs/promises';
import axios from 'axios';
import { logger } from '../utils/logger.js';

interface TokenStore {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  locationId: string;
  companyId: string;
  scope: string[];
}

export class OAuthManager {
  private tokenStore: TokenStore | null = null;
  private readonly tokenFilePath = './.tokens.enc';
  private readonly encryptionKey: Buffer;

  constructor() {
    const key = process.env.ENCRYPTION_KEY;
    if (!key || key.length !== 64) {
      throw new Error('ENCRYPTION_KEY must be 64 hex characters (32 bytes)');
    }
    this.encryptionKey = Buffer.from(key, 'hex');
  }

  async getAccessToken(): Promise<string> {
    if (!this.tokenStore) {
      await this.loadTokens();
    }

    if (!this.tokenStore) {
      throw new Error('No tokens available. Please authenticate first.');
    }

    // Refresh if expiring within 5 minutes
    const bufferTime = 5 * 60 * 1000;
    if (Date.now() >= this.tokenStore.expiresAt - bufferTime) {
      await this.refreshAccessToken();
    }

    return this.tokenStore.accessToken;
  }

  isAuthenticated(): boolean {
    return this.tokenStore !== null && Date.now() < this.tokenStore.expiresAt;
  }

  getLocationId(): string {
    if (!this.tokenStore) {
      throw new Error('No active session. Please authenticate first.');
    }
    return this.tokenStore.locationId;
  }

  // Additional methods: exchangeCodeForTokens, refreshAccessToken, saveTokens, loadTokens
  // See architecture doc for full implementation
}
```

### OAuth Tool Pattern

```typescript
server.addTool({
  name: 'authenticate_ghl',
  description: 'Initiate OAuth authentication flow with GoHighLevel',
  schema: z.object({}),
  handler: async () => {
    try {
      const authUrl = buildAuthorizationUrl();
      await open(authUrl);

      return {
        success: true,
        message: 'Browser opened for authentication. Please complete the OAuth flow.',
        authUrl
      };
    } catch (error) {
      const mcpError = ErrorHandler.handleError(error);
      return {
        success: false,
        error: ErrorHandler.formatForUser(mcpError)
      };
    }
  }
});
```

---

## Rate Limiting Patterns

*Note: These patterns are for Story 3.3+. Story 3.1 does not require rate limiting.*

### Rate Limiter Usage

```typescript
import { RateLimiter } from '../utils/rate-limiter.js';

const rateLimiter = new RateLimiter({
  burstLimit: 100,      // 100 requests per 10 seconds
  burstWindow: 10000,   // 10 seconds in ms
  dailyLimit: 200000    // 200k requests per day
});

// Use in tool
server.addTool({
  name: 'list_workflows',
  description: 'List all workflows',
  schema: z.object({}),
  handler: async () => {
    return rateLimiter.execute(async () => {
      const accessToken = await oauthManager.getAccessToken();

      const response = await axios.get(
        'https://services.leadconnectorhq.com/workflows/',
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Version': '2021-04-15'
          }
        }
      );

      return {
        success: true,
        workflows: response.data.workflows
      };
    });
  }
});
```

---

## API Client Patterns

*Note: These patterns are for Story 3.4+. Story 3.1 does not require API calls.*

### Axios Request Pattern with Error Handling

```typescript
import axios from 'axios';
import { ErrorHandler } from '../utils/error-handler.js';
import { logger } from '../utils/logger.js';

async function makeGHLRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  endpoint: string,
  accessToken: string,
  data?: any
): Promise<T> {
  try {
    logger.debug(`GHL API ${method} ${endpoint}`);

    const response = await axios({
      method,
      url: `https://services.leadconnectorhq.com${endpoint}`,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Version': '2021-04-15',
        'Content-Type': 'application/json'
      },
      data
    });

    logger.debug(`GHL API ${method} ${endpoint} - Success`);
    return response.data;
  } catch (error) {
    logger.error(`GHL API ${method} ${endpoint} - Failed`, error);
    throw error;
  }
}
```

### Usage Example

```typescript
server.addTool({
  name: 'get_workflow',
  description: 'Get workflow by ID',
  schema: z.object({
    workflowId: z.string()
  }),
  handler: async (params) => {
    try {
      const accessToken = await oauthManager.getAccessToken();

      const workflow = await makeGHLRequest(
        'GET',
        `/workflows/${params.workflowId}`,
        accessToken
      );

      return {
        success: true,
        workflow
      };
    } catch (error) {
      const mcpError = ErrorHandler.handleError(error);
      return {
        success: false,
        error: ErrorHandler.formatForUser(mcpError)
      };
    }
  }
});
```

---

## Complete Server Template (Story 3.1)

**File:** `src/index.ts`

```typescript
import { FastMCP } from 'fastmcp';
import { z } from 'zod';
import { logger } from './utils/logger.js';
import { TestTools } from './tools/test.js';

// Initialize server
const server = new FastMCP({
  name: 'ghl-api',
  version: '1.0.0'
});

// Register tools
TestTools.register(server);

// Error handling
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection', { reason, promise });
  process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

// Start server
logger.info('Starting GHL API MCP Server...');
logger.info(`Server: ghl-api v1.0.0`);
logger.info(`Transport: stdio`);

server.start();

logger.info('Server started successfully');
```

---

## Best Practices Summary

1. **Always use `.js` extensions in imports** (even for `.ts` files)
2. **Use logger for all output** (not console.log)
3. **Wrap tool handlers in try/catch** with ErrorHandler
4. **Define Zod schemas separately** for complex types (reusability)
5. **Add descriptions to schema fields** (helps Claude understand parameters)
6. **Return consistent response format**: `{ success: boolean, ... }`
7. **Log at INFO level** for important operations
8. **Log at DEBUG level** for detailed debugging
9. **Log at ERROR level** with full error object

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Author:** Alex Kim (Solutions Architect)
