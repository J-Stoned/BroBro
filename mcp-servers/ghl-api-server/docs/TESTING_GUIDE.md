# Testing Guide - GHL API MCP Server

This guide covers all testing approaches for the GHL API MCP Server, from unit tests to manual testing with Claude Desktop.

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Manual Testing with Claude Desktop](#manual-testing-with-claude-desktop)
5. [Debugging MCP Communication](#debugging-mcp-communication)
6. [Test Data and Fixtures](#test-data-and-fixtures)
7. [CI/CD Testing](#cicd-testing)

---

## Testing Philosophy

### Testing Pyramid for MCP Servers

```
        /\
       /  \      E2E Tests (Manual with Claude Desktop)
      /    \     - Test complete workflows
     /------\    - Test user experience
    /        \
   /   INT    \  Integration Tests
  /            \ - Test MCP protocol communication
 /              \- Test API interactions
/----------------\
    UNIT TESTS    Unit Tests
- Test individual  - Test business logic
  functions        - Test error handling
                   - Test utilities
```

**Story 3.1 Focus:**
- Unit tests for logger
- Manual testing with Claude Desktop
- No integration tests yet (no API calls in 3.1)

---

## Unit Testing

### Setup Jest for TypeScript

**Step 1: Install Jest and Dependencies**

```bash
npm install -D jest @types/jest ts-jest
```

**Step 2: Create Jest Configuration**

Create `jest.config.js`:

```javascript
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        useESM: true,
      },
    ],
  },
  testMatch: ['**/__tests__/**/*.test.ts', '**/?(*.)+(spec|test).ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**Step 3: Add Test Scripts to package.json**

```json
{
  "scripts": {
    "test": "node --experimental-vm-modules node_modules/jest/bin/jest.js",
    "test:watch": "npm run test -- --watch",
    "test:coverage": "npm run test -- --coverage"
  }
}
```

### Unit Test: Logger

**File:** `src/utils/__tests__/logger.test.ts`

```typescript
import { logger, LogLevel } from '../logger.js';

describe('Logger', () => {
  let consoleSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  test('should log INFO messages', () => {
    logger.info('Test message');

    expect(consoleSpy).toHaveBeenCalledTimes(1);
    const logOutput = consoleSpy.mock.calls[0][0];

    expect(logOutput).toContain('[INFO]');
    expect(logOutput).toContain('Test message');
  });

  test('should log DEBUG messages', () => {
    logger.debug('Debug message', { key: 'value' });

    expect(consoleSpy).toHaveBeenCalledTimes(1);
    const logOutput = consoleSpy.mock.calls[0][0];

    expect(logOutput).toContain('[DEBUG]');
    expect(logOutput).toContain('Debug message');
  });

  test('should log ERROR messages to console.error', () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation();

    logger.error('Error message');

    expect(errorSpy).toHaveBeenCalledTimes(1);
    const logOutput = errorSpy.mock.calls[0][0];

    expect(logOutput).toContain('[ERROR]');
    expect(logOutput).toContain('Error message');

    errorSpy.mockRestore();
  });

  test('should format timestamps correctly', () => {
    logger.info('Test');

    const logOutput = consoleSpy.mock.calls[0][0];
    const isoDateRegex = /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z/;

    expect(logOutput).toMatch(isoDateRegex);
  });

  test('should include additional arguments', () => {
    logger.info('Message', { data: 'test' }, 42);

    expect(consoleSpy).toHaveBeenCalledTimes(1);
    expect(consoleSpy.mock.calls[0][1]).toEqual({ data: 'test' });
    expect(consoleSpy.mock.calls[0][2]).toBe(42);
  });
});
```

### Running Unit Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test -- logger.test.ts
```

**Expected Output:**

```
PASS  src/utils/__tests__/logger.test.ts
  Logger
    ✓ should log INFO messages (5 ms)
    ✓ should log DEBUG messages (2 ms)
    ✓ should log ERROR messages to console.error (3 ms)
    ✓ should format timestamps correctly (2 ms)
    ✓ should include additional arguments (2 ms)

Test Suites: 1 passed, 1 total
Tests:       5 passed, 5 total
Snapshots:   0 total
Time:        2.345 s
```

---

## Integration Testing

*Note: Integration tests are for Stories 3.2+. Story 3.1 has no external integrations to test.*

### Integration Test: OAuth Flow (Story 3.2)

**File:** `src/auth/__tests__/oauth-manager.integration.test.ts`

```typescript
import { OAuthManager } from '../oauth-manager.js';
import dotenv from 'dotenv';

// Load .env.test for test credentials
dotenv.config({ path: '.env.test' });

describe('OAuthManager Integration', () => {
  let oauthManager: OAuthManager;

  beforeEach(() => {
    oauthManager = new OAuthManager();
  });

  test('should load encrypted tokens from file', async () => {
    // Assumes .tokens.enc exists from previous auth
    await oauthManager['loadTokens']();

    expect(oauthManager.isAuthenticated()).toBe(true);
    expect(oauthManager.getLocationId()).toBeDefined();
  });

  test('should refresh expired token', async () => {
    // This test requires a valid refresh token
    // Skip if no auth available
    if (!oauthManager.isAuthenticated()) {
      console.log('Skipping: No auth available');
      return;
    }

    const accessToken = await oauthManager.getAccessToken();
    expect(accessToken).toBeDefined();
    expect(typeof accessToken).toBe('string');
  });
});
```

### Integration Test: MCP Server (Story 3.1+)

**File:** `src/__tests__/server.integration.test.ts`

```typescript
import { spawn, ChildProcess } from 'child_process';

describe('MCP Server Integration', () => {
  let serverProcess: ChildProcess;

  beforeAll(() => {
    // Start the MCP server
    serverProcess = spawn('node', ['dist/index.js'], {
      stdio: 'pipe'
    });
  });

  afterAll(() => {
    serverProcess.kill();
  });

  test('should respond to MCP initialize request', (done) => {
    const initRequest = {
      jsonrpc: '2.0',
      method: 'initialize',
      params: {},
      id: 1
    };

    serverProcess.stdout?.on('data', (data) => {
      const response = JSON.parse(data.toString());

      expect(response.jsonrpc).toBe('2.0');
      expect(response.id).toBe(1);
      expect(response.result).toBeDefined();

      done();
    });

    serverProcess.stdin?.write(JSON.stringify(initRequest) + '\n');
  });

  test('should list available tools', (done) => {
    const toolsRequest = {
      jsonrpc: '2.0',
      method: 'tools/list',
      params: {},
      id: 2
    };

    serverProcess.stdout?.on('data', (data) => {
      const response = JSON.parse(data.toString());

      if (response.id === 2) {
        expect(response.result.tools).toBeDefined();
        expect(Array.isArray(response.result.tools)).toBe(true);
        expect(response.result.tools.length).toBeGreaterThan(0);

        done();
      }
    });

    serverProcess.stdin?.write(JSON.stringify(toolsRequest) + '\n');
  });
});
```

---

## Manual Testing with Claude Desktop

### Step 1: Build and Configure

```bash
# Build the project
npm run build

# Verify build succeeded
ls dist/index.js
```

Configure Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ghl-api": {
      "command": "node",
      "args": ["C:/Users/justi/BroBro/mcp-servers/ghl-api-server/dist/index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Step 2: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Start Claude Desktop
3. Wait 10 seconds for MCP servers to initialize

### Step 3: Verify Connection

**In Claude Desktop:**

1. Open the tools panel (hammer icon at bottom)
2. Look for "ghl-api" server
3. Verify status shows "Connected" (green indicator)
4. Check available tools list

**Expected Tools for Story 3.1:**
- `test_connection`

### Step 4: Test the Tool

**Test Script for Claude:**

```
Please use the test_connection tool to verify the GHL API MCP server is working correctly.
```

**Expected Response:**

```json
{
  "status": "connected",
  "server": "ghl-api",
  "version": "1.0.0",
  "timestamp": "2025-10-26T10:45:30.123Z"
}
```

### Step 5: Test Error Handling

**Test Script:**

```
Try to use a tool that doesn't exist: "nonexistent_tool"
```

**Expected Behavior:**
- Claude should report "Tool not found" error
- Server should remain stable (not crash)

### Manual Test Checklist (Story 3.1)

- [ ] Server appears in MCP panel
- [ ] Server status is "Connected"
- [ ] `test_connection` tool is listed
- [ ] `test_connection` returns correct response
- [ ] Response includes all expected fields (status, server, version, timestamp)
- [ ] Timestamp is valid ISO 8601 format
- [ ] Server remains stable after multiple invocations
- [ ] Error messages are user-friendly
- [ ] Server logs appear in terminal (if run manually)

---

## Debugging MCP Communication

### Method 1: Manual Server Test

```bash
# Start server manually
node dist/index.js

# In another terminal, send MCP request via stdin
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | node dist/index.js
```

### Method 2: MCP Inspector (Recommended)

Install MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Run inspector:

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

**Inspector Features:**
- Interactive MCP tool testing
- View request/response payloads
- Test tool schemas
- Debug Zod validation errors

### Method 3: Claude Desktop Logs

**Windows Log Location:**
```
C:\Users\<username>\AppData\Roaming\Claude\logs\
```

**View Recent Logs:**

```bash
# PowerShell
Get-Content "C:\Users\justi\AppData\Roaming\Claude\logs\mcp.log" -Tail 50

# View errors only
Get-Content "C:\Users\justi\AppData\Roaming\Claude\logs\mcp.log" | Select-String "ERROR"
```

**Common Log Patterns:**

```
# Successful connection
[INFO] Connected to MCP server: ghl-api

# Tool execution
[DEBUG] Invoking tool: test_connection

# Errors
[ERROR] MCP server failed to start: ghl-api
[ERROR] Tool execution failed: test_connection
```

### Method 4: Add Debug Logging

**Add to src/index.ts:**

```typescript
import { logger } from './utils/logger.js';

// Log all incoming requests
process.stdin.on('data', (data) => {
  logger.debug('MCP Request', data.toString());
});

// Log all outgoing responses
const originalWrite = process.stdout.write.bind(process.stdout);
process.stdout.write = (chunk: any, ...args: any[]) => {
  logger.debug('MCP Response', chunk.toString());
  return originalWrite(chunk, ...args);
};
```

---

## Test Data and Fixtures

### Creating Test Fixtures

**File:** `src/__tests__/fixtures/workflows.ts`

```typescript
export const mockWorkflow = {
  id: 'wf_test123',
  name: 'Test Workflow',
  locationId: 'loc_test456',
  status: 'active',
  trigger: {
    type: 'ContactCreated',
    filters: {}
  },
  actions: [
    {
      type: 'SendEmail',
      settings: {
        template: 'welcome'
      }
    }
  ]
};

export const mockContact = {
  id: 'con_test789',
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  phone: '+1234567890',
  tags: ['test'],
  customFields: {}
};
```

### Using Fixtures in Tests

```typescript
import { mockWorkflow } from './fixtures/workflows.js';

test('should process workflow correctly', () => {
  const result = processWorkflow(mockWorkflow);
  expect(result.success).toBe(true);
});
```

---

## CI/CD Testing

### GitHub Actions Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Test GHL API MCP Server

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: mcp-servers/ghl-api-server
        run: npm ci

      - name: Run TypeScript compiler
        working-directory: mcp-servers/ghl-api-server
        run: npm run build

      - name: Run unit tests
        working-directory: mcp-servers/ghl-api-server
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          directory: mcp-servers/ghl-api-server/coverage
```

### Pre-commit Checks

**File:** `.husky/pre-commit` (if using Husky)

```bash
#!/bin/sh
cd mcp-servers/ghl-api-server

# Run TypeScript compiler
npm run build || exit 1

# Run tests
npm run test || exit 1

echo "✅ All checks passed"
```

---

## Testing Best Practices

### 1. Test Naming Convention

```typescript
describe('ComponentName', () => {
  describe('methodName', () => {
    test('should do X when Y happens', () => {
      // Test implementation
    });
  });
});
```

### 2. AAA Pattern (Arrange, Act, Assert)

```typescript
test('should return success when connection is valid', () => {
  // Arrange
  const server = new FastMCP({ name: 'test', version: '1.0.0' });

  // Act
  const result = server.testConnection();

  // Assert
  expect(result.status).toBe('connected');
});
```

### 3. Test One Thing at a Time

```typescript
// ❌ BAD - Testing multiple things
test('should work correctly', () => {
  expect(result.success).toBe(true);
  expect(result.data).toBeDefined();
  expect(result.timestamp).toMatch(/\d{4}/);
});

// ✅ GOOD - One assertion per test
test('should return success', () => {
  expect(result.success).toBe(true);
});

test('should include data in response', () => {
  expect(result.data).toBeDefined();
});

test('should include valid timestamp', () => {
  expect(result.timestamp).toMatch(/\d{4}/);
});
```

### 4. Use Descriptive Test Names

```typescript
// ❌ BAD
test('test1', () => { /* ... */ });

// ✅ GOOD
test('should refresh token when expired and refresh token is valid', () => { /* ... */ });
```

---

## Story 3.1 Testing Checklist

### Unit Tests
- [ ] Logger tests passing
- [ ] Test connection tool returns correct schema
- [ ] All tests have 80%+ coverage

### Manual Tests
- [ ] Server builds without TypeScript errors
- [ ] Server starts successfully
- [ ] Server appears in Claude Desktop MCP panel
- [ ] Server shows "Connected" status
- [ ] `test_connection` tool is listed
- [ ] `test_connection` tool executes successfully
- [ ] Response format matches expected schema
- [ ] Server handles multiple tool invocations
- [ ] Server logs appear correctly

### Integration Tests
- [ ] MCP handshake succeeds
- [ ] Tools list request returns correct tools
- [ ] Tool invocation request/response cycle works

### Documentation
- [ ] Testing guide is complete
- [ ] Troubleshooting steps are documented
- [ ] Test coverage is reported

---

## Troubleshooting Test Failures

### Jest: "Cannot use import statement outside a module"

**Solution:**
```json
// package.json
{
  "type": "module"
}

// jest.config.js
{
  "preset": "ts-jest/presets/default-esm"
}
```

### Test: "Cannot find module './logger.js'"

**Solution:**
Add `.js` extension to all imports in test files:

```typescript
import { logger } from '../logger.js';  // ✅ CORRECT
import { logger } from '../logger';     // ❌ WRONG
```

### MCP: "Tool not found"

**Solution:**
1. Verify tool is registered before `server.start()`
2. Rebuild: `npm run build`
3. Restart Claude Desktop
4. Check Claude Desktop logs for errors

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Author:** Alex Kim (Solutions Architect)
