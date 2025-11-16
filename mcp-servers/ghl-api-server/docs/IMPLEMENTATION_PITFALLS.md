# Implementation Pitfalls and Solutions

This document identifies common pitfalls you may encounter during Story 3.1 implementation, with concrete solutions and prevention strategies.

**Target Audience:** James (Dev Agent)
**Last Updated:** 2025-10-26

---

## Table of Contents

1. [TypeScript & Module Issues](#typescript--module-issues)
2. [FastMCP Integration Issues](#fastmcp-integration-issues)
3. [Claude Desktop Configuration Issues](#claude-desktop-configuration-issues)
4. [Development Workflow Issues](#development-workflow-issues)
5. [Testing Issues](#testing-issues)
6. [Security Issues](#security-issues)
7. [Performance Issues](#performance-issues)

---

## TypeScript & Module Issues

### PITFALL 1: Missing `.js` Extension in Imports

**Severity:** HIGH - Blocks compilation

**Symptom:**
```
error TS2307: Cannot find module './utils/logger' or its corresponding type declarations.
```

**Root Cause:**
With ES Modules and NodeNext module resolution, TypeScript requires `.js` extensions in import statements (even though the source files are `.ts`).

**Incorrect Code:**
```typescript
import { logger } from './utils/logger';
import { ErrorHandler } from '../utils/error-handler';
```

**Correct Code:**
```typescript
import { logger } from './utils/logger.js';
import { ErrorHandler } from '../utils/error-handler.js';
```

**Why This Happens:**
TypeScript preserves import paths as-is in the compiled output. At runtime, Node.js needs the `.js` extension to resolve modules.

**Prevention:**
- Always include `.js` in imports
- Use TypeScript's path resolution to verify imports
- Run `tsc --noEmit` frequently to catch errors early

---

### PITFALL 2: Missing `"type": "module"` in package.json

**Severity:** HIGH - Blocks execution

**Symptom:**
```
SyntaxError: Cannot use import statement outside a module
```

**Root Cause:**
Node.js defaults to CommonJS unless `"type": "module"` is specified.

**Solution:**
Add to `package.json`:
```json
{
  "name": "ghl-api-server",
  "version": "1.0.0",
  "type": "module",  // <-- REQUIRED
  "scripts": { ... }
}
```

**Prevention:**
- Add `"type": "module"` immediately after initializing package.json
- Verify it's present before writing any TypeScript code

---

### PITFALL 3: Incorrect Module Resolution in tsconfig.json

**Severity:** MEDIUM - Causes import errors

**Symptom:**
TypeScript can't resolve modules, or modules resolve incorrectly at runtime.

**Root Cause:**
Using `"module": "CommonJS"` or `"moduleResolution": "node"` with ES Modules.

**Correct Configuration:**
```json
{
  "compilerOptions": {
    "module": "NodeNext",           // NOT "ES2022" or "CommonJS"
    "moduleResolution": "NodeNext", // NOT "node"
    "target": "ES2022"
  }
}
```

**Prevention:**
- Use the exact tsconfig.json from ARCHITECTURE_PATTERNS.md
- Don't mix module systems

---

### PITFALL 4: Importing package.json Without Assert

**Severity:** LOW - Causes warnings in Node.js 20+

**Symptom:**
```
(node:12345) ExperimentalWarning: Importing JSON modules is an experimental feature
```

**Root Cause:**
JSON imports require import assertions in ES Modules.

**Incorrect Code:**
```typescript
import pkg from '../package.json';
```

**Correct Code:**
```typescript
import pkg from '../package.json' assert { type: 'json' };
```

**Alternative (No Warnings):**
```typescript
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const pkg = JSON.parse(readFileSync(join(__dirname, '../package.json'), 'utf8'));
```

**Prevention:**
- Use import assertions for JSON
- Enable `resolveJsonModule: true` in tsconfig.json

---

## FastMCP Integration Issues

### PITFALL 5: Tool Registered After server.start()

**Severity:** HIGH - Tools won't appear in Claude

**Symptom:**
Server starts successfully, but no tools appear in Claude Desktop.

**Root Cause:**
Tools must be registered BEFORE calling `server.start()`.

**Incorrect Code:**
```typescript
const server = new FastMCP({ name: 'ghl-api', version: '1.0.0' });

server.start();  // ❌ Started too early

server.addTool({  // ❌ This tool will never register
  name: 'test_connection',
  // ...
});
```

**Correct Code:**
```typescript
const server = new FastMCP({ name: 'ghl-api', version: '1.0.0' });

server.addTool({  // ✅ Register first
  name: 'test_connection',
  // ...
});

server.start();  // ✅ Start after all tools registered
```

**Prevention:**
- Always register tools first
- Call `server.start()` at the very end of `src/index.ts`
- Add a comment: `// Start server (MUST be last)`

---

### PITFALL 6: Missing Tool Description

**Severity:** MEDIUM - Poor user experience

**Symptom:**
Tool appears in Claude but Claude doesn't know when to use it.

**Root Cause:**
Description is technically optional but critical for Claude to understand tool usage.

**Incorrect Code:**
```typescript
server.addTool({
  name: 'test_connection',
  description: '',  // ❌ Empty description
  schema: z.object({}),
  handler: async () => { /* ... */ }
});
```

**Correct Code:**
```typescript
server.addTool({
  name: 'test_connection',
  description: 'Test MCP server connection and verify server is running correctly',  // ✅ Clear, specific
  schema: z.object({}),
  handler: async () => { /* ... */ }
});
```

**Best Practices:**
- Describe what the tool does (not how)
- Mention when to use it
- Keep it concise (1-2 sentences)
- Include key parameters in description

---

### PITFALL 7: Schema Validation Errors Not Caught

**Severity:** MEDIUM - Runtime errors

**Symptom:**
Tool executes with invalid parameters, causing errors inside handler.

**Root Cause:**
Missing or incorrect Zod schema allows invalid data through.

**Example:**
```typescript
server.addTool({
  name: 'get_workflow',
  description: 'Get workflow by ID',
  schema: z.object({}),  // ❌ No validation!
  handler: async (params) => {
    // params.workflowId is undefined - crash!
    return fetchWorkflow(params.workflowId);
  }
});
```

**Correct Code:**
```typescript
server.addTool({
  name: 'get_workflow',
  description: 'Get workflow by ID',
  schema: z.object({
    workflowId: z.string().min(1).describe('The workflow ID to retrieve')
  }),  // ✅ Validates workflowId is present and non-empty
  handler: async (params) => {
    // params.workflowId is guaranteed to be a non-empty string
    return fetchWorkflow(params.workflowId);
  }
});
```

**Prevention:**
- Always define complete schemas
- Use `.describe()` on all parameters
- Test with invalid inputs

---

## Claude Desktop Configuration Issues

### PITFALL 8: Incorrect Path Separators in Windows

**Severity:** HIGH - Claude can't start server

**Symptom:**
Server shows "Failed" or "Disconnected" in Claude Desktop MCP panel.

**Root Cause:**
Windows paths with backslashes don't work in JSON config.

**Incorrect Code:**
```json
{
  "mcpServers": {
    "ghl-api": {
      "command": "node",
      "args": ["C:\\Users\\justi\\BroBro\\mcp-servers\\ghl-api-server\\dist\\index.js"]
    }
  }
}
```

**Correct Code:**
```json
{
  "mcpServers": {
    "ghl-api": {
      "command": "node",
      "args": ["C:/Users/justi/BroBro/mcp-servers/ghl-api-server/dist/index.js"]
    }
  }
}
```

**Prevention:**
- Always use forward slashes `/` in JSON configs
- Use absolute paths, not relative
- Double-check paths are correct

---

### PITFALL 9: Claude Desktop Config File Not Found

**Severity:** HIGH - Changes don't take effect

**Symptom:**
Modified config, restarted Claude, but server still not appearing.

**Root Cause:**
Editing wrong config file or file doesn't exist.

**Correct Location (Windows):**
```
C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json
```

**How to Find:**
1. Open Run dialog (Win+R)
2. Type: `%APPDATA%\Claude`
3. Create `claude_desktop_config.json` if it doesn't exist

**Prevention:**
- Bookmark the config file location
- Verify changes are saved before restarting Claude
- Check file timestamp to confirm it was modified

---

### PITFALL 10: Forgot to Restart Claude Desktop

**Severity:** MEDIUM - Wasted debugging time

**Symptom:**
Config changed, but server not appearing.

**Root Cause:**
Claude Desktop only reads config at startup.

**Solution:**
1. Quit Claude Desktop completely (not just close window)
2. Wait 5 seconds
3. Start Claude Desktop
4. Wait 10 seconds for MCP servers to initialize

**Prevention:**
- Always restart after config changes
- Check system tray to ensure Claude is fully closed

---

## Development Workflow Issues

### PITFALL 11: Forgot to Run Build Before Testing

**Severity:** MEDIUM - Testing old code

**Symptom:**
Code changes don't appear when testing with Claude Desktop.

**Root Cause:**
Claude Desktop runs compiled JS from `dist/`, not TypeScript from `src/`.

**Workflow:**
```bash
# Make changes to src/index.ts

# ❌ WRONG - Restart Claude Desktop immediately
# Old code still running!

# ✅ CORRECT - Build first
npm run build

# Then restart Claude Desktop
```

**Prevention:**
- Always run `npm run build` before testing
- Create a script: `"build-and-test": "npm run build && echo 'Now restart Claude Desktop'"`

---

### PITFALL 12: TypeScript Compiler Errors Ignored

**Severity:** HIGH - Runtime errors

**Symptom:**
`npm run build` shows errors, but dist/ files are created anyway (from previous build).

**Root Cause:**
TypeScript compiler creates output even with errors (by default).

**Solution:**
Check build output carefully:
```bash
npm run build

# Look for this:
# Found 3 errors. Watching for file changes.
# ❌ Don't proceed with errors!
```

**Prevention:**
- Add `"noEmitOnError": true` to tsconfig.json
- Always check build output for errors
- Use CI/CD to block merges with TypeScript errors

---

### PITFALL 13: Node Modules Not Installed

**Severity:** HIGH - Blocks development

**Symptom:**
```
Error: Cannot find module 'fastmcp'
```

**Root Cause:**
Forgot to run `npm install` after cloning or creating project.

**Solution:**
```bash
cd mcp-servers/ghl-api-server
npm install
```

**Prevention:**
- Run `npm install` immediately after project creation
- Verify `node_modules/` directory exists
- Check `package-lock.json` is created

---

## Testing Issues

### PITFALL 14: Tests Pass But Server Doesn't Work

**Severity:** MEDIUM - False confidence

**Symptom:**
Unit tests pass, but server fails in Claude Desktop.

**Root Cause:**
Unit tests don't test MCP protocol integration.

**Solution:**
- Run manual tests with Claude Desktop
- Use MCP Inspector for protocol testing
- Don't rely solely on unit tests

**Prevention:**
- Follow the complete testing checklist in TESTING_GUIDE.md
- Test both unit and integration layers

---

### PITFALL 15: Jest Configuration for ES Modules

**Severity:** MEDIUM - Tests fail to run

**Symptom:**
```
Jest encountered an unexpected token
SyntaxError: Cannot use import statement outside a module
```

**Root Cause:**
Default Jest configuration doesn't support ES Modules.

**Solution:**
Use the complete Jest config from TESTING_GUIDE.md:
```javascript
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { useESM: true }],
  }
};
```

**Prevention:**
- Copy complete config from TESTING_GUIDE.md
- Don't modify Jest config unless necessary

---

## Security Issues

### PITFALL 16: Committing .env File

**Severity:** CRITICAL - Security breach

**Symptom:**
`.env` file appears in git commits.

**Root Cause:**
`.env` not in `.gitignore`.

**Solution:**
Add to `.gitignore`:
```gitignore
.env
.env.local
.env.*.local
.tokens.enc
*.pem
*.key
```

**Verification:**
```bash
git status
# .env should NOT appear in untracked files
```

**Prevention:**
- Create `.gitignore` before creating `.env`
- Use `git status` before every commit
- Set up pre-commit hooks to block sensitive files

---

### PITFALL 17: Logging Sensitive Data

**Severity:** HIGH - Security risk

**Symptom:**
Access tokens or secrets appear in log files.

**Incorrect Code:**
```typescript
logger.info('OAuth token received', { accessToken, refreshToken });  // ❌ NEVER LOG TOKENS!
```

**Correct Code:**
```typescript
logger.info('OAuth token received', {
  tokenType: 'Bearer',
  expiresAt: expiresAt,
  // No actual token values
});
```

**Prevention:**
- Never log tokens, secrets, or passwords
- Redact sensitive data: `token: token.substring(0, 8) + '...'`
- Review all logger calls before committing

---

## Performance Issues

### PITFALL 18: Synchronous File Operations

**Severity:** LOW - Not a concern for Story 3.1, but important later

**Symptom:**
Server becomes unresponsive during file operations.

**Incorrect Code:**
```typescript
import { readFileSync } from 'fs';

const data = readFileSync('./.tokens.enc', 'utf8');  // ❌ Blocks event loop
```

**Correct Code:**
```typescript
import { readFile } from 'fs/promises';

const data = await readFile('./.tokens.enc', 'utf8');  // ✅ Non-blocking
```

**Prevention:**
- Always use async file operations (`fs/promises`)
- Never use `*Sync` methods in production code

---

### PITFALL 19: Memory Leaks from Event Listeners

**Severity:** MEDIUM - Gradual degradation

**Symptom:**
Server memory usage grows over time.

**Incorrect Code:**
```typescript
process.on('SIGINT', () => {
  logger.info('Shutting down...');
  // ❌ No cleanup - listeners accumulate
});
```

**Correct Code:**
```typescript
let shuttingDown = false;

process.on('SIGINT', () => {
  if (shuttingDown) return;  // ✅ Prevent duplicate handling
  shuttingDown = true;

  logger.info('Shutting down...');
  process.exit(0);
});
```

**Prevention:**
- Clean up listeners when done
- Use `once()` instead of `on()` for one-time events
- Track listener count during development

---

## General Best Practices to Avoid Pitfalls

### 1. Follow the Build-Test Cycle

```bash
# Make changes
# ↓
npm run build
# ↓
npm run test
# ↓
# Manual test with Claude Desktop
# ↓
git commit
```

### 2. Use the Checklist

Before marking a task complete:
- [ ] TypeScript compiles without errors
- [ ] All unit tests pass
- [ ] Manual testing with Claude Desktop succeeds
- [ ] No sensitive data in logs
- [ ] Changes documented
- [ ] Git status clean (no .env or secrets)

### 3. When Stuck

1. Check this pitfalls document
2. Review QUICKSTART.md
3. Check Claude Desktop logs
4. Ask for help with specific error messages

### 4. Prevention is Easier Than Debugging

- Set up `.gitignore` first
- Copy proven configs (don't modify)
- Test frequently (after every small change)
- Read error messages carefully

---

## Quick Troubleshooting Flowchart

```
Issue?
  │
  ├─ Build Error?
  │   ├─ Check .js extensions in imports
  │   ├─ Check "type": "module" in package.json
  │   └─ Check tsconfig.json module settings
  │
  ├─ Runtime Error?
  │   ├─ Check npm install was run
  │   ├─ Check dist/ files exist
  │   └─ Check paths in Claude config
  │
  ├─ Server Not Appearing in Claude?
  │   ├─ Check Claude Desktop config path
  │   ├─ Check forward slashes in paths
  │   ├─ Check build succeeded
  │   └─ Restart Claude Desktop
  │
  └─ Tool Not Working?
      ├─ Check tool registered before server.start()
      ├─ Check Zod schema is correct
      ├─ Check tool description exists
      └─ Check Claude Desktop logs
```

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Author:** Alex Kim (Solutions Architect)
