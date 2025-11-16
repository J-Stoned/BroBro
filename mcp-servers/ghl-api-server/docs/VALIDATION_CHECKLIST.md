# Story 3.1 Validation Checklist

This comprehensive checklist validates that Story 3.1 implementation meets all acceptance criteria and quality standards.

**Story:** 3.1 - GHL API MCP Server Foundation
**Developer:** James (Dev Agent)
**Reviewer:** Alex Kim (Solutions Architect) & QA Agent

---

## How to Use This Checklist

1. **During Development:** Check off items as you complete them
2. **Before Story Completion:** Ensure ALL items are checked
3. **For Code Review:** Reviewer verifies all items independently
4. **For QA:** QA agent uses this for acceptance testing

**Status Indicators:**
- ✅ = Complete and verified
- ⚠️ = Partially complete (needs attention)
- ❌ = Not complete
- N/A = Not applicable

---

## Section 1: Project Structure

### 1.1 Directory Structure

- [ ] `mcp-servers/ghl-api-server/` directory created
- [ ] `src/` directory exists
- [ ] `src/auth/` directory exists (empty for Story 3.1)
- [ ] `src/tools/` directory exists
- [ ] `src/utils/` directory exists
- [ ] `dist/` directory exists (created by build)
- [ ] `tests/` directory exists
- [ ] `docs/` directory exists with support documents

**Verification Command:**
```bash
cd "c:\Users\justi\BroBro\mcp-servers\ghl-api-server"
dir src\auth src\tools src\utils dist tests docs
```

---

### 1.2 Configuration Files

- [ ] `package.json` exists with correct metadata
- [ ] `package-lock.json` exists (dependencies locked)
- [ ] `tsconfig.json` exists with correct settings
- [ ] `.gitignore` exists with all sensitive patterns
- [ ] `.env.example` exists with template variables
- [ ] `README.md` exists with project documentation

**Verification:**
```bash
ls package.json package-lock.json tsconfig.json .gitignore .env.example README.md
```

---

## Section 2: Dependencies

### 2.1 Core Dependencies Installed

- [ ] `fastmcp` installed
- [ ] `@gohighlevel/api-client@2.2.1` installed (exact version)
- [ ] `zod` installed
- [ ] All dependencies in `package.json` → `dependencies` section

**Verification:**
```bash
npm list fastmcp @gohighlevel/api-client zod
```

Expected output shows installed versions.

---

### 2.2 Dev Dependencies Installed

- [ ] `typescript@^5.x` installed
- [ ] `@types/node@^20.x` installed
- [ ] `ts-node` installed
- [ ] Optional: `jest`, `@types/jest`, `ts-jest` if testing implemented

**Verification:**
```bash
npm list typescript @types/node ts-node
```

---

### 2.3 Package.json Configuration

- [ ] `"type": "module"` is set
- [ ] `"name": "ghl-api-server"` or similar
- [ ] `"version": "1.0.0"` or appropriate version
- [ ] `"main": "dist/index.js"` is set
- [ ] Scripts include: `build`, `dev`, `start`, `clean`

**Verification:**
```bash
cat package.json | grep -E '"type"|"name"|"version"|"main"|"scripts"'
```

---

## Section 3: TypeScript Configuration

### 3.1 tsconfig.json Settings

- [ ] `"target": "ES2022"`
- [ ] `"module": "NodeNext"`
- [ ] `"moduleResolution": "NodeNext"`
- [ ] `"outDir": "./dist"`
- [ ] `"rootDir": "./src"`
- [ ] `"strict": true`
- [ ] `"esModuleInterop": true`
- [ ] `"skipLibCheck": true`
- [ ] `"resolveJsonModule": true`
- [ ] `"declaration": true`
- [ ] `"sourceMap": true`

**Verification:**
```bash
cat tsconfig.json
```

Compare against template in ARCHITECTURE_PATTERNS.md.

---

### 3.2 TypeScript Compilation

- [ ] `npm run build` succeeds without errors
- [ ] `dist/` directory contains compiled `.js` files
- [ ] `dist/` contains `.d.ts` declaration files
- [ ] `dist/` contains `.js.map` source map files
- [ ] No TypeScript errors in output

**Verification:**
```bash
npm run build
ls dist/
```

Expected output: Zero errors, `dist/index.js` exists.

---

## Section 4: Source Code Implementation

### 4.1 Logger Utility (src/utils/logger.ts)

- [ ] File exists: `src/utils/logger.ts`
- [ ] Exports `LogLevel` enum (DEBUG, INFO, WARN, ERROR)
- [ ] Exports `logger` singleton instance
- [ ] Implements `debug()`, `info()`, `warn()`, `error()` methods
- [ ] Formats timestamps as ISO 8601
- [ ] Formats messages as `[timestamp] [level] message`
- [ ] Uses `console.log`, `console.warn`, `console.error` appropriately

**Verification:**
```bash
cat src/utils/logger.ts | grep -E "export|LogLevel|logger"
```

---

### 4.2 Test Tools (src/tools/test.ts)

- [ ] File exists: `src/tools/test.ts`
- [ ] Exports `TestTools` class
- [ ] Implements `static register(server: FastMCP)` method
- [ ] Registers `test_connection` tool
- [ ] Tool has name: `"test_connection"`
- [ ] Tool has description (non-empty, clear)
- [ ] Tool schema is `z.object({})`
- [ ] Tool handler returns correct structure:
  - `status: 'connected'`
  - `server: 'ghl-api'`
  - `version: <package version>`
  - `timestamp: <ISO 8601 timestamp>`

**Verification:**
```bash
cat src/tools/test.ts | grep -E "export|TestTools|test_connection"
```

---

### 4.3 Main Server (src/index.ts)

- [ ] File exists: `src/index.ts`
- [ ] Imports `FastMCP` from `fastmcp`
- [ ] Imports `logger` from `./utils/logger.js`
- [ ] Imports `TestTools` from `./tools/test.js`
- [ ] Creates `FastMCP` instance with name and version
- [ ] Registers `TestTools.register(server)` BEFORE `server.start()`
- [ ] Calls `server.start()` at end
- [ ] Implements error handlers:
  - `uncaughtException`
  - `unhandledRejection`
  - `SIGINT`
  - `SIGTERM`
- [ ] Logs startup messages

**Verification:**
```bash
cat src/index.ts
```

Check order: imports → create server → register tools → error handlers → start server.

---

### 4.4 Import Statements

- [ ] All imports use `.js` extension (even for `.ts` files)
- [ ] Example: `import { logger } from './utils/logger.js'`
- [ ] No imports without extension (would fail)

**Verification:**
```bash
grep -r "from '\." src/ --include="*.ts" | grep -v ".js'"
```

Expected output: Empty (all imports have `.js`).

---

## Section 5: Build and Execution

### 5.1 Build Process

- [ ] `npm run build` completes without errors
- [ ] `npm run build` output shows "0 errors"
- [ ] `dist/index.js` exists and is executable
- [ ] `dist/index.js` is not empty

**Verification:**
```bash
npm run build
cat dist/index.js | head -n 10
```

---

### 5.2 Server Startup

- [ ] `npm run start` starts server without crashing
- [ ] Startup logs appear:
  - "Starting GHL API MCP Server..."
  - "Server started successfully"
- [ ] Server continues running (doesn't exit immediately)
- [ ] No error messages in logs

**Verification:**
```bash
npm run start
# Press Ctrl+C after 5 seconds
```

Expected: Logs appear, server runs until interrupted.

---

### 5.3 MCP Protocol Handshake

- [ ] Server responds to MCP `initialize` request
- [ ] Server responds to `tools/list` request
- [ ] `test_connection` tool appears in tools list

**Verification (Manual):**
```bash
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | npm run start
```

Expected: JSON response with tools array containing `test_connection`.

---

## Section 6: Claude Desktop Integration

### 6.1 Configuration

- [ ] `claude_desktop_config.json` exists in correct location:
  - Windows: `C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json`
- [ ] Config contains `ghl-api` server entry
- [ ] `command` is `"node"`
- [ ] `args` array contains absolute path to `dist/index.js`
- [ ] Path uses forward slashes `/` (not backslashes `\`)
- [ ] Path is absolute (not relative)

**Verification:**
```bash
cat "C:\Users\justi\AppData\Roaming\Claude\claude_desktop_config.json"
```

---

### 6.2 Connection Status

- [ ] Claude Desktop restarted after config change
- [ ] MCP panel shows "ghl-api" server
- [ ] Server status is "Connected" (green indicator)
- [ ] No error messages in Claude Desktop UI

**Verification:**
Open Claude Desktop → Tools panel → Check "ghl-api" status.

---

### 6.3 Tool Availability

- [ ] `test_connection` tool appears in tools list
- [ ] Tool description is visible
- [ ] Tool is selectable/invokable

**Verification:**
Open Claude Desktop → Tools panel → Expand "ghl-api" → Check tools.

---

### 6.4 Tool Execution

- [ ] `test_connection` tool executes successfully
- [ ] Returns expected response structure:
  ```json
  {
    "status": "connected",
    "server": "ghl-api",
    "version": "1.0.0",
    "timestamp": "<valid ISO 8601>"
  }
  ```
- [ ] Timestamp is valid ISO 8601 format
- [ ] No errors during execution
- [ ] Tool can be executed multiple times

**Verification:**
In Claude Desktop chat:
```
Use the test_connection tool.
```

---

## Section 7: Code Quality

### 7.1 Code Style

- [ ] Consistent indentation (2 or 4 spaces)
- [ ] No unused imports
- [ ] No `console.log` statements (use `logger` instead)
- [ ] No commented-out code
- [ ] Clear variable names
- [ ] Functions have clear purpose

**Verification:**
```bash
grep -r "console.log" src/ --include="*.ts" | grep -v "logger"
```

Expected: Only logger implementation has console calls.

---

### 7.2 TypeScript Best Practices

- [ ] No `any` types (use specific types or `unknown`)
- [ ] All functions have return type annotations
- [ ] Async functions return `Promise<T>`
- [ ] No TypeScript `@ts-ignore` comments
- [ ] Strict null checks pass

**Verification:**
```bash
npm run build -- --noEmit --strict
```

---

### 7.3 Error Handling

- [ ] Process error handlers implemented
- [ ] Graceful shutdown on SIGINT/SIGTERM
- [ ] Error messages are user-friendly
- [ ] No stack traces exposed to users
- [ ] All errors logged with `logger.error()`

**Verification:**
Review `src/index.ts` for error handlers.

---

## Section 8: Security

### 8.1 Sensitive Data Protection

- [ ] `.env` file is in `.gitignore`
- [ ] `.tokens.enc` file is in `.gitignore` (future-proofing)
- [ ] No hardcoded credentials in code
- [ ] No secrets in log messages
- [ ] No API keys in source files

**Verification:**
```bash
cat .gitignore | grep -E ".env|.tokens.enc"
grep -r "API_KEY\|SECRET\|PASSWORD" src/ --include="*.ts"
```

Expected: .gitignore contains patterns, no secrets in code.

---

### 8.2 Git Repository

- [ ] `.env` is NOT in git history
- [ ] `.tokens.enc` is NOT in git history
- [ ] `node_modules/` is NOT in git
- [ ] `dist/` is NOT in git

**Verification:**
```bash
git status
git log --all --full-history -- .env .tokens.enc
```

Expected: No .env or .tokens.enc in git history.

---

## Section 9: Documentation

### 9.1 Support Documents

- [ ] `docs/QUICKSTART.md` exists and is complete
- [ ] `docs/ARCHITECTURE_PATTERNS.md` exists and is complete
- [ ] `docs/TESTING_GUIDE.md` exists and is complete
- [ ] `docs/DECISIONS.md` exists and is ready for use
- [ ] `docs/IMPLEMENTATION_PITFALLS.md` exists
- [ ] `docs/VALIDATION_CHECKLIST.md` exists (this file)

**Verification:**
```bash
ls docs/
```

---

### 9.2 README.md

- [ ] `README.md` exists at project root
- [ ] Contains project description
- [ ] Contains setup instructions
- [ ] Contains build instructions
- [ ] Contains testing instructions
- [ ] Links to architecture documentation

**Verification:**
```bash
cat README.md
```

---

### 9.3 Code Comments

- [ ] Complex logic has explanatory comments
- [ ] File headers (if applicable)
- [ ] Function doc comments (for public APIs)
- [ ] No misleading comments

**Verification:**
Manual review of source files.

---

## Section 10: Testing

### 10.1 Unit Tests (Optional for Story 3.1)

If implemented:
- [ ] Test files in `src/__tests__/` or `tests/`
- [ ] Logger tests exist and pass
- [ ] `npm run test` succeeds
- [ ] Test coverage >= 80% (if coverage enabled)

**Verification:**
```bash
npm run test
npm run test:coverage
```

---

### 10.2 Manual Testing

- [ ] All items in TESTING_GUIDE.md → Manual Testing Checklist completed
- [ ] Server starts successfully
- [ ] Server connects to Claude Desktop
- [ ] `test_connection` tool executes
- [ ] Server handles multiple invocations
- [ ] Server shuts down gracefully (Ctrl+C)

**Verification:**
Follow TESTING_GUIDE.md manual testing section.

---

## Section 11: Story 3.1 Acceptance Criteria

### AC 1: Project Structure
- [ ] `mcp-servers/ghl-api-server/` directory created with TypeScript project structure

### AC 2: Dependencies
- [ ] `package.json` includes FastMCP, @gohighlevel/api-client v2.2.1, Zod for validation

### AC 3: TypeScript Configuration
- [ ] `tsconfig.json` configured for ES2022, strict type checking, NodeNext module resolution

### AC 4: Server Entry Point
- [ ] `src/index.ts` created with FastMCP server initialization and proper error handling

### AC 5: Transport Configuration
- [ ] Server supports stdio transport (dev) with HTTP transport scaffolded for future use

### AC 6: Build Script
- [ ] Build script compiles TypeScript to `dist/` without errors

### AC 7: Server Startup
- [ ] Server starts successfully and responds to MCP handshake

### AC 8: Test Connection Tool
- [ ] `test_connection` tool implemented to verify server functionality

### AC 9: Logging Utility
- [ ] Logging utility created with timestamp and severity levels

### AC 10: Dependencies Locked
- [ ] All dependencies installed and version locked in package-lock.json

**Verification:**
All 10 acceptance criteria checked above.

---

## Section 12: Pre-Merge Checklist

Before merging to main branch:

- [ ] All acceptance criteria met
- [ ] All checklist items above are ✅
- [ ] Code builds without errors
- [ ] Code tested manually with Claude Desktop
- [ ] Documentation is complete and accurate
- [ ] No secrets or sensitive data in commits
- [ ] Git status is clean
- [ ] Ready for code review

---

## Section 13: Known Issues / Technical Debt

Document any issues or technical debt incurred during implementation:

**Issue 1:**
- **Description:**
- **Impact:**
- **Plan:**

**Issue 2:**
- **Description:**
- **Impact:**
- **Plan:**

---

## Final Sign-Off

### Developer (James)
- [ ] All checklist items completed
- [ ] Code is ready for review
- [ ] Documentation updated
- **Date:** __________
- **Notes:**

### Solutions Architect (Alex Kim)
- [ ] Architecture alignment verified
- [ ] Code quality acceptable
- [ ] Security requirements met
- **Date:** __________
- **Notes:**

### QA Agent
- [ ] Manual testing completed
- [ ] Acceptance criteria validated
- [ ] Story ready for acceptance
- **Date:** __________
- **Notes:**

---

## Appendix: Quick Verification Script

Save this as `verify-story-3.1.sh` for automated checks:

```bash
#!/bin/bash
echo "Story 3.1 Verification Script"
echo "=============================="

# Check directory structure
echo "✓ Checking directory structure..."
[ -d "src/auth" ] && echo "  ✅ src/auth exists" || echo "  ❌ src/auth missing"
[ -d "src/tools" ] && echo "  ✅ src/tools exists" || echo "  ❌ src/tools missing"
[ -d "src/utils" ] && echo "  ✅ src/utils exists" || echo "  ❌ src/utils missing"

# Check config files
echo "✓ Checking configuration files..."
[ -f "package.json" ] && echo "  ✅ package.json exists" || echo "  ❌ package.json missing"
[ -f "tsconfig.json" ] && echo "  ✅ tsconfig.json exists" || echo "  ❌ tsconfig.json missing"
[ -f ".gitignore" ] && echo "  ✅ .gitignore exists" || echo "  ❌ .gitignore missing"

# Check TypeScript compilation
echo "✓ Running TypeScript compilation..."
npm run build && echo "  ✅ Build succeeded" || echo "  ❌ Build failed"

# Check dist output
echo "✓ Checking build output..."
[ -f "dist/index.js" ] && echo "  ✅ dist/index.js exists" || echo "  ❌ dist/index.js missing"

echo ""
echo "Verification complete!"
```

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Author:** Alex Kim (Solutions Architect)
