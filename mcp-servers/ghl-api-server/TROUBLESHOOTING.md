# GHL API MCP Server - Troubleshooting Guide

## Table of Contents
1. [Server Won't Start](#server-wont-start)
2. [Tools Not Appearing](#tools-not-appearing)
3. [OAuth Errors](#oauth-errors)
4. [Rate Limiting Issues](#rate-limiting-issues)
5. [Token Encryption Errors](#token-encryption-errors)
6. [GHL API Errors](#ghl-api-errors)
7. [Build Errors](#build-errors)
8. [Claude Code Integration Issues](#claude-code-integration-issues)

---

## Server Won't Start

### Symptom
Server doesn't appear in Claude Code MCP panel or shows "Failed" status.

### Common Causes & Solutions

#### 1. Missing Environment Variables

**Error in logs:**
```
Environment configuration warnings: GHL_CLIENT_ID not set
```

**Solution:**
```bash
# Verify environment variables are set
echo $GHL_CLIENT_ID        # Unix/macOS
echo %GHL_CLIENT_ID%       # Windows

# If empty, set them:
# See DEPLOYMENT.md "Step 2: Set Environment Variables"
```

#### 2. Invalid Encryption Key

**Error in logs:**
```
ENCRYPTION_KEY must be exactly 64 hex characters
```

**Solution:**
```bash
# Generate valid key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Update .env with new key
ENCRYPTION_KEY=<paste_new_key_here>

# Restart Claude Code
```

#### 3. Build Not Completed

**Error:**
```
Cannot find module './dist/index.js'
```

**Solution:**
```bash
cd mcp-servers/ghl-api-server
npm run build

# Verify dist/index.js exists
ls -l dist/index.js
```

#### 4. Node Version Too Old

**Error:**
```
SyntaxError: Unexpected token 'export'
```

**Solution:**
```bash
# Check Node version
node --version

# Should be v18 or higher
# Update Node.js if needed
```

#### 5. Permission Denied

**Error:**
```
EACCES: permission denied
```

**Solution (Unix/macOS):**
```bash
# Make index.js executable
chmod +x dist/index.js

# Or run with explicit node command (already configured)
node dist/index.js
```

---

## Tools Not Appearing

### Symptom
Server starts but tools don't show up in Claude Code.

### Solutions

#### 1. Server Not in .mcp.json

**Check:**
```bash
cat .mcp.json | grep ghl-api
```

**If missing, add:**
```json
{
  "mcpServers": {
    "ghl-api": {
      "command": "node",
      "args": ["./mcp-servers/ghl-api-server/dist/index.js"],
      "env": {
        "GHL_CLIENT_ID": "${env:GHL_CLIENT_ID}",
        "GHL_CLIENT_SECRET": "${env:GHL_CLIENT_SECRET}",
        "GHL_REDIRECT_URI": "${env:GHL_REDIRECT_URI}",
        "ENCRYPTION_KEY": "${env:ENCRYPTION_KEY}"
      }
    }
  }
}
```

#### 2. Server Path Incorrect

**Error in logs:**
```
Cannot find module './mcp-servers/ghl-api-server/dist/index.js'
```

**Solution:**
```bash
# Verify path is relative to project root
pwd  # Should be in project root

# Check path exists
ls -l mcp-servers/ghl-api-server/dist/index.js
```

#### 3. Cache Issue

**Solution:**
```bash
# Rebuild server
cd mcp-servers/ghl-api-server
npm run build

# Restart Claude Code completely
# (Close all windows, reopen)
```

---

## OAuth Errors

### Error 1: Invalid Redirect URI

**Symptom:**
```
redirect_uri mismatch
```

**Cause:** Redirect URI in GHL Marketplace app doesn't match `.env`

**Solution:**
1. Check `.env` file:
   ```
   GHL_REDIRECT_URI=http://localhost:3456/oauth/callback
   ```
2. Go to https://marketplace.gohighlevel.com/apps
3. Edit your app → OAuth tab
4. Set redirect URI to: `http://localhost:3456/oauth/callback`
5. Save changes
6. Try authentication again

### Error 2: Invalid Client Credentials

**Symptom:**
```
invalid_client: Client authentication failed
```

**Cause:** Wrong CLIENT_ID or CLIENT_SECRET

**Solution:**
1. Go to https://marketplace.gohighlevel.com/apps
2. Open your app
3. Navigate to OAuth tab
4. Copy CLIENT_ID and CLIENT_SECRET
5. Update `.env` with correct values
6. Restart Claude Code
7. Try authentication again

### Error 3: Port 3456 Already in Use

**Symptom:**
```
EADDRINUSE: address already in use :::3456
```

**Solution:**
```bash
# Find process using port 3456
# Windows:
netstat -ano | findstr :3456
taskkill /PID <PID> /F

# Unix/macOS:
lsof -ti:3456 | xargs kill -9

# Or use different port in .env:
GHL_REDIRECT_URI=http://localhost:8080/oauth/callback
# (Also update in GHL Marketplace app!)
```

### Error 4: Browser Doesn't Open

**Symptom:** OAuth flow starts but browser doesn't open

**Solution:**
- Manually open the URL shown in terminal/logs
- URL format: `https://marketplace.gohighlevel.com/oauth/chooselocation?...`
- Complete authorization in browser
- Return to Claude Code

### Error 5: Token Expired

**Symptom:**
```
401 Unauthorized: Token expired
```

**Solution:**
- Tokens auto-refresh automatically
- If refresh fails, re-authenticate:
  ```
  Use authenticate_ghl tool to re-authenticate
  ```

---

## Rate Limiting Issues

### Error 1: Burst Limit Exceeded

**Symptom:**
```
429 Too Many Requests: Burst limit exceeded (100 req/10s)
```

**Solution:**
- Requests are automatically queued
- Wait for queue to process (check logs)
- Check queue status:
  ```
  Use get_rate_limit_status tool
  ```

**Prevention:**
- Reduce frequency of API calls
- Batch operations when possible
- Add delays between requests

### Error 2: Daily Quota Exceeded

**Symptom:**
```
429 Too Many Requests: Daily quota exceeded (200,000 req/day)
```

**Solution:**
- Wait until UTC midnight for reset
- Check when reset occurs:
  ```
  Use get_rate_limit_status tool
  # Shows: "Daily reset in: XX hours"
  ```

**Prevention:**
- Monitor daily usage with `get_rate_limit_status`
- Optimize queries (use filters, pagination)
- Cache results when appropriate

### Error 3: Queue Timeout

**Symptom:**
```
Request timed out after 30 seconds in queue
```

**Solution:**
- System is overloaded with requests
- Reset rate limiter (development only):
  ```
  Use reset_rate_limits tool
  ```
- Wait for queue to clear before retrying

---

## Token Encryption Errors

### Error 1: Invalid Encryption Key Format

**Symptom:**
```
ENCRYPTION_KEY must contain only hexadecimal characters
```

**Solution:**
```bash
# Generate valid hex key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Update .env
ENCRYPTION_KEY=<64_character_hex_string>

# Restart Claude Code
```

### Error 2: Corrupted Token File

**Symptom:**
```
Failed to decrypt tokens: Invalid initialization vector
```

**Solution:**
```bash
# Delete corrupted token file
rm .tokens.enc

# Re-authenticate
# Use authenticate_ghl tool in Claude Code
```

### Error 3: Encryption Key Changed

**Symptom:**
```
Decryption failed: bad decrypt
```

**Cause:** ENCRYPTION_KEY changed after tokens were encrypted

**Solution:**
```bash
# Option 1: Restore old key (if known)
ENCRYPTION_KEY=<old_key>

# Option 2: Delete tokens and re-authenticate
rm .tokens.enc
# Then use authenticate_ghl tool
```

---

## GHL API Errors

### 401 Unauthorized

**Cause:** Invalid or expired access token

**Solution:**
- Token should auto-refresh
- If persists, re-authenticate:
  ```
  Use authenticate_ghl tool
  ```

### 403 Forbidden

**Cause:** Insufficient permissions/scopes

**Solution:**
1. Go to https://marketplace.gohighlevel.com/apps
2. Edit your app → OAuth tab
3. Ensure these scopes are enabled:
   - `contacts.readonly`, `contacts.write`
   - `workflows.readonly`, `workflows.write`
   - `calendars.readonly`, `calendars.write`
   - `forms.readonly`, `surveys.readonly`
   - `locations.readonly`
4. Save changes
5. Re-authenticate in Claude Code

### 404 Not Found

**Cause:** Resource doesn't exist (wrong ID or deleted)

**Solution:**
- Verify the ID is correct
- Use list/search tools to find valid IDs:
  ```
  list_workflows
  search_contacts
  list_funnels
  ```

### 422 Validation Error

**Cause:** Invalid data in request

**Example:**
```
Email format invalid
```

**Solution:**
- Review tool parameters
- Check required fields
- Validate data format (email, phone, dates)
- See error message for specific field issues

### 429 Rate Limit

**Cause:** Too many requests

**Solution:**
- See "Rate Limiting Issues" section above
- Use `get_rate_limit_status` tool

### 500 Internal Server Error

**Cause:** GHL API issue (not your fault)

**Solution:**
- Retry request after delay
- Check GHL status page: https://status.gohighlevel.com/
- If persists, contact GHL support

---

## Build Errors

### TypeScript Compilation Errors

**Symptom:**
```
error TS2xxx: <error message>
```

**Solution:**
```bash
# Clean build
rm -rf dist
npm run build

# If persists, check TypeScript version
npm list typescript

# Update if needed
npm install typescript@latest --save-dev
```

### Missing Dependencies

**Symptom:**
```
Cannot find module 'fastmcp'
```

**Solution:**
```bash
# Install dependencies
npm install

# If persists, clean install
rm -rf node_modules package-lock.json
npm install
```

---

## Claude Code Integration Issues

### Server Shows "Disconnected"

**Solution:**
1. Check MCP server logs in Claude Code panel
2. Look for error messages
3. Verify all environment variables set
4. Restart Claude Code completely

### Tools Execute But No Response

**Symptom:** Tool runs but hangs with no response

**Solution:**
1. Check rate limit status:
   ```
   get_rate_limit_status
   ```
2. Verify OAuth is authenticated:
   ```
   get_oauth_status
   ```
3. Check server logs for errors

### "Server Not Found" Error

**Solution:**
1. Verify `.mcp.json` exists in project root
2. Check server name matches: `ghl-api`
3. Restart Claude Code
4. Check server appears in MCP panel

---

## Common Solutions Summary

### Quick Fix Checklist

If server isn't working, try these in order:

1. **Rebuild:**
   ```bash
   cd mcp-servers/ghl-api-server
   npm run build
   ```

2. **Check Environment:**
   ```bash
   # Verify all 4 variables set
   echo $GHL_CLIENT_ID
   echo $GHL_CLIENT_SECRET
   echo $GHL_REDIRECT_URI
   echo $ENCRYPTION_KEY
   ```

3. **Restart Claude Code:**
   - Close all windows
   - Reopen project
   - Check MCP panel

4. **Verify Configuration:**
   ```bash
   # Check .mcp.json has ghl-api entry
   cat .mcp.json | grep -A 10 ghl-api
   ```

5. **Re-authenticate:**
   ```
   Use authenticate_ghl tool in Claude Code
   ```

6. **Check Logs:**
   - Open Claude Code MCP panel
   - View ghl-api server logs
   - Look for error messages

---

## Getting Help

If issues persist after trying these solutions:

1. **Check Logs:**
   - Server logs in Claude Code MCP panel
   - Look for specific error messages

2. **Review Documentation:**
   - DEPLOYMENT.md for setup steps
   - README.md for tool usage

3. **Verify Prerequisites:**
   - Node.js v18+
   - npm v9+
   - Valid GHL account
   - Correct OAuth credentials

4. **Report Issue:**
   - Include error message
   - Include relevant log excerpts
   - Describe steps to reproduce

---

## Debug Mode

Enable verbose logging for troubleshooting:

**In .env:**
```env
LOG_LEVEL=DEBUG
```

**Restart server** to see detailed debug logs including:
- All API requests/responses
- Token operations
- Rate limiting decisions
- OAuth flow details

**Remember to set back to INFO in production:**
```env
LOG_LEVEL=INFO
```

---

**Still having issues?** Check DEPLOYMENT.md for complete setup guide.
