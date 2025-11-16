# GHL API MCP Server - Quick Start Guide

## Overview

This guide will walk you through setting up the GHL API MCP Server from scratch, running it locally, testing with Claude Desktop, and troubleshooting common issues.

**Time to complete:** 30-45 minutes
**Prerequisites:** Node.js 20+ LTS, npm, Claude Desktop installed

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Development Workflow](#development-workflow)
3. [Testing with Claude Desktop](#testing-with-claude-desktop)
4. [Common Troubleshooting](#common-troubleshooting)
5. [Next Steps](#next-steps)

---

## Initial Setup

### Step 1: Verify Prerequisites

```bash
# Check Node.js version (must be 20+ LTS)
node --version
# Should output: v20.x.x or higher

# Check npm version
npm --version
# Should output: 9.x.x or higher

# Verify Claude Desktop is installed
# Check: C:\Users\<username>\AppData\Local\AnthropicClaude\
```

### Step 2: Navigate to Project Directory

```bash
cd "c:\Users\justi\BroBro\mcp-servers\ghl-api-server"
```

### Step 3: Initialize the TypeScript Project

```bash
# Initialize npm project
npm init -y

# Install core dependencies
npm install fastmcp @gohighlevel/api-client@2.2.1 zod

# Install development dependencies
npm install -D typescript @types/node ts-node

# Install additional dependencies for OAuth
npm install axios express dotenv open

# Install additional type definitions
npm install -D @types/express
```

### Step 4: Create TypeScript Configuration

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### Step 5: Update package.json

Add the following to your `package.json`:

```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "ts-node src/index.ts",
    "start": "node dist/index.js",
    "clean": "rm -rf dist"
  }
}
```

### Step 6: Create Directory Structure

```bash
# Create source directories
mkdir -p src\auth
mkdir -p src\tools
mkdir -p src\utils
mkdir -p dist
mkdir -p tests

# Create .gitignore
```

Create `.gitignore`:

```gitignore
# Dependencies
node_modules/

# Build outputs
dist/
*.js
*.js.map
*.d.ts
*.d.ts.map

# Environment and secrets
.env
.env.local
.tokens.enc
*.pem
*.key

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Step 7: Create Environment File Template

Create `.env.example`:

```bash
# GoHighLevel OAuth Credentials
# Get these from https://marketplace.gohighlevel.com/apps
GHL_CLIENT_ID=your_client_id_here
GHL_CLIENT_SECRET=your_client_secret_here
GHL_REDIRECT_URI=http://localhost:3456/oauth/callback

# Token Encryption
# Generate with: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
ENCRYPTION_KEY=your_64_char_hex_key_here

# Chroma Configuration (optional)
CHROMA_URL=http://localhost:8000

# Rate Limiting (optional, uses GHL defaults)
RATE_LIMIT_BURST=100
RATE_LIMIT_DAILY=200000
```

---

## Development Workflow

### Step 1: Create Logger Utility

Create `src/utils/logger.ts` (see ARCHITECTURE_PATTERNS.md for full implementation)

### Step 2: Create Basic Server

Create `src/index.ts` (see ARCHITECTURE_PATTERNS.md for full implementation)

### Step 3: Build the Project

```bash
npm run build
```

Expected output:
```
# No errors
# dist/ directory created with compiled .js files
```

### Step 4: Run the Server Locally

```bash
npm run start
```

Expected output:
```
[2025-10-26T10:30:00.000Z] [INFO] Starting GHL API MCP Server...
[2025-10-26T10:30:00.100Z] [INFO] Server started successfully on stdio transport
```

### Step 5: Test the Server (Without Claude)

In a new terminal:

```bash
# Send MCP handshake via stdin (manual test)
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | npm run start
```

You should see a JSON response with server capabilities.

---

## Testing with Claude Desktop

### Step 1: Configure Claude Desktop

1. Locate Claude Desktop config file:
   - Windows: `C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json`

2. Add the MCP server configuration:

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

**IMPORTANT:** Use forward slashes `/` in the path, even on Windows.

### Step 2: Restart Claude Desktop

1. Completely quit Claude Desktop (not just close window)
2. Start Claude Desktop again
3. Look for MCP server icon in the bottom toolbar

### Step 3: Verify Connection

In Claude Desktop, check the MCP panel:

1. Click the tools icon (bottom of chat interface)
2. Look for "ghl-api" server in the list
3. Verify it shows "Connected" status
4. Check available tools - should see `test_connection`

### Step 4: Test the Tool

In a Claude chat:

```
Use the test_connection tool to verify the GHL API MCP server is working.
```

Expected response:
```json
{
  "status": "connected",
  "server": "ghl-api",
  "version": "1.0.0",
  "timestamp": "2025-10-26T10:35:00.000Z"
}
```

---

## Common Troubleshooting

### Issue 1: "Cannot find module 'fastmcp'"

**Symptoms:**
```
Error: Cannot find module 'fastmcp'
```

**Solution:**
```bash
# Ensure all dependencies are installed
npm install

# Verify package-lock.json exists
ls package-lock.json

# If not, regenerate it
rm -rf node_modules package-lock.json
npm install
```

---

### Issue 2: "Module resolution errors" or "Unexpected token 'export'"

**Symptoms:**
```
SyntaxError: Unexpected token 'export'
```

**Root Cause:** Missing `"type": "module"` in package.json

**Solution:**

1. Open `package.json`
2. Add `"type": "module"` at the top level:

```json
{
  "name": "ghl-api-server",
  "version": "1.0.0",
  "type": "module",  // <-- ADD THIS LINE
  "scripts": { ... }
}
```

3. Rebuild:
```bash
npm run clean
npm run build
```

---

### Issue 3: TypeScript Compilation Errors

**Symptoms:**
```
error TS2307: Cannot find module './utils/logger.js'
```

**Root Cause:** Import statements must include `.js` extension for ES modules

**Solution:**

All imports in TypeScript must use `.js` extension:

```typescript
// ❌ WRONG
import { logger } from './utils/logger';

// ✅ CORRECT
import { logger } from './utils/logger.js';
```

---

### Issue 4: Claude Desktop Can't Connect to Server

**Symptoms:**
- Server shows "Disconnected" in MCP panel
- No tools visible in Claude

**Solution Checklist:**

1. **Verify path is correct:**
   ```json
   "args": ["C:/Users/justi/BroBro/mcp-servers/ghl-api-server/dist/index.js"]
   ```
   - Use forward slashes `/` even on Windows
   - Path must be absolute, not relative

2. **Verify the build succeeded:**
   ```bash
   ls dist/index.js
   # Should exist
   ```

3. **Test server manually:**
   ```bash
   node dist/index.js
   # Should start without errors
   ```

4. **Check Claude Desktop logs:**
   - Windows: `C:\Users\<username>\AppData\Roaming\Claude\logs\`
   - Look for MCP connection errors

5. **Restart Claude Desktop:**
   - Fully quit Claude Desktop
   - Start it again
   - Wait 10 seconds for MCP servers to initialize

---

### Issue 5: Server Starts But No Tools Appear

**Symptoms:**
- Server shows "Connected" in MCP panel
- No tools listed

**Solution:**

1. **Verify tool registration in src/index.ts:**

```typescript
// Ensure tool is registered BEFORE server.start()
server.addTool({
  name: 'test_connection',
  description: 'Test MCP server connection',
  schema: z.object({}),
  handler: async () => { /* ... */ }
});

// THEN start server
server.start();
```

2. **Rebuild and restart:**
```bash
npm run build
# Restart Claude Desktop
```

---

### Issue 6: "Port 3456 already in use" (Future OAuth Stories)

**Symptoms:**
```
Error: listen EADDRINUSE: address already in use :::3456
```

**Solution:**

```bash
# Windows - Find and kill process on port 3456
netstat -ano | findstr :3456
taskkill /PID <PID> /F

# Or change the port in .env
GHL_REDIRECT_URI=http://localhost:3457/oauth/callback
```

---

## Next Steps

### After Story 3.1 is Complete:

1. **Story 3.2: OAuth Implementation**
   - Register GHL Marketplace app
   - Implement OAuth flow
   - Test authentication

2. **Story 3.3: Rate Limiting**
   - Implement rate limiter utility
   - Add burst and daily limits
   - Test rate limit enforcement

3. **Story 3.4: Workflow Tools**
   - Implement workflow CRUD operations
   - Test with real GHL account

### Resources

- **Architecture Doc:** `docs/architecture/13-mcp-server-architecture.md`
- **Story 3.1:** `docs/stories/3.1.story.md`
- **Architecture Patterns:** `docs/ARCHITECTURE_PATTERNS.md`
- **Testing Guide:** `docs/TESTING_GUIDE.md`

---

## Quick Command Reference

```bash
# Development
npm run dev          # Run with ts-node (development)
npm run build        # Compile TypeScript
npm run start        # Run compiled JS (production)
npm run clean        # Remove dist/ directory

# Testing
node dist/index.js   # Manual server test
npm run build && npm run start  # Full build + run

# Environment
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"  # Generate encryption key
```

---

## Getting Help

**Issue tracking:**
- Check `docs/stories/3.1.story.md` for known issues
- Review architecture doc for design decisions

**Ask Alex (Solutions Architect):**
- Architectural questions
- Design pattern clarifications
- Security best practices

**Ask Bob (Scrum Master):**
- Story requirements
- Acceptance criteria
- Task prioritization

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Author:** Alex Kim (Solutions Architect)
