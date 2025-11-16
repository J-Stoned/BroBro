# GHL API MCP Server - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Claude Code Integration](#claude-code-integration)
4. [GHL Marketplace App Setup](#ghl-marketplace-app-setup)
5. [OAuth Authentication](#oauth-authentication)
6. [Testing the Installation](#testing-the-installation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Node.js**: v18 or higher
- **npm**: v9 or higher
- **Claude Code**: Latest version
- **GoHighLevel Account**: Agency or Sub-account with API access

### Verify Prerequisites
```bash
node --version  # Should be v18+
npm --version   # Should be v9+
```

---

## Environment Setup

### Step 1: Generate Encryption Key

The server uses AES-256-CBC encryption for storing OAuth tokens securely.

```bash
# Generate a secure 32-byte hex key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Copy the output** - you'll need this for your `.env` file.

### Step 2: Create .env File

Navigate to the server directory:
```bash
cd mcp-servers/ghl-api-server
```

Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# GoHighLevel OAuth Credentials
GHL_CLIENT_ID=your_client_id_here
GHL_CLIENT_SECRET=your_client_secret_here
GHL_REDIRECT_URI=http://localhost:3456/oauth/callback

# Token Encryption (paste the key from Step 1)
ENCRYPTION_KEY=your_64_character_hex_key_here

# Optional Configuration
LOG_LEVEL=INFO
RATE_LIMIT_BURST=100
RATE_LIMIT_DAILY=200000
```

**IMPORTANT**: Never commit your `.env` file to git!

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Build the Server

```bash
npm run build
```

Verify build success:
```bash
# Should see dist/index.js
ls -l dist/index.js
```

---

## Claude Code Integration

### Step 1: Add MCP Server Configuration

The GHL API server is already configured in `.mcp.json` at the project root:

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
      },
      "description": "GoHighLevel API MCP Server"
    }
  }
}
```

### Step 2: Set Environment Variables

**Option A: System Environment Variables** (Recommended)

**Windows:**
```cmd
setx GHL_CLIENT_ID "your_client_id"
setx GHL_CLIENT_SECRET "your_client_secret"
setx GHL_REDIRECT_URI "http://localhost:3456/oauth/callback"
setx ENCRYPTION_KEY "your_encryption_key"
```

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export GHL_CLIENT_ID="your_client_id"
export GHL_CLIENT_SECRET="your_client_secret"
export GHL_REDIRECT_URI="http://localhost:3456/oauth/callback"
export ENCRYPTION_KEY="your_encryption_key"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

**Option B: Claude Code Settings**

Add to `.claude/settings.local.json`:
```json
{
  "env": {
    "GHL_CLIENT_ID": "your_client_id",
    "GHL_CLIENT_SECRET": "your_client_secret",
    "GHL_REDIRECT_URI": "http://localhost:3456/oauth/callback",
    "ENCRYPTION_KEY": "your_encryption_key"
  }
}
```

### Step 3: Restart Claude Code

1. Close Claude Code completely
2. Reopen the project
3. Check the MCP server panel (status bar or command palette)
4. Verify "ghl-api" server appears and status is "Running"

---

## GHL Marketplace App Setup

### Step 1: Create Marketplace App

1. Go to https://marketplace.gohighlevel.com/apps
2. Click "Create App"
3. Fill in app details:
   - **Name**: Your App Name (e.g., "My GHL Integration")
   - **Description**: Brief description of your integration
   - **Category**: Choose appropriate category

### Step 2: Configure OAuth Settings

1. Navigate to **OAuth** tab in your app settings
2. Set **Redirect URI**:
   ```
   http://localhost:3456/oauth/callback
   ```
3. Configure **Scopes** (select all that apply):
   - `contacts.readonly` - Read contact information
   - `contacts.write` - Create and update contacts
   - `workflows.readonly` - View workflows
   - `workflows.write` - Create and manage workflows
   - `calendars.readonly` - View calendars
   - `calendars.write` - Create appointments
   - `opportunities.readonly` - View opportunities
   - `opportunities.write` - Manage opportunities
   - `locations.readonly` - View location information
   - `forms.readonly` - View forms
   - `surveys.readonly` - View survey responses

### Step 3: Get Credentials

1. After saving OAuth settings, you'll see:
   - **Client ID** - Copy this
   - **Client Secret** - Copy this (shown once)
2. Paste these values into your `.env` file

### Step 4: Approve App for Your Location

1. Go to your GHL location settings
2. Navigate to **Apps & Integrations**
3. Find your app and click "Install"
4. This authorizes the app for your location

---

## OAuth Authentication

### Step 1: Check OAuth Status

In Claude Code, ask:
```
Can you check my OAuth status using get_oauth_status?
```

Expected response if not authenticated:
```json
{
  "authenticated": false,
  "message": "No tokens found. Please authenticate first."
}
```

### Step 2: Initiate OAuth Flow

Ask Claude Code:
```
Please authenticate with GoHighLevel using authenticate_ghl
```

This will:
1. Start a local OAuth server on port 3456
2. Open your browser to GHL authorization page
3. Prompt you to select a location and authorize

### Step 3: Complete Authorization

1. **Browser opens** to GHL authorization page
2. **Select location** from dropdown
3. **Review permissions** being requested
4. **Click "Authorize"**
5. Browser redirects to `http://localhost:3456/oauth/callback`
6. You'll see: "Authorization successful! You can close this window."

### Step 4: Verify Authentication

Ask Claude Code:
```
Check OAuth status again using get_oauth_status
```

Expected response after successful auth:
```json
{
  "authenticated": true,
  "locationId": "your_location_id",
  "expiresIn": "23 hours 59 minutes"
}
```

### Token Storage

- Tokens are encrypted using AES-256-CBC
- Stored in `.tokens.enc` file (git-ignored)
- Automatically refreshed when expired
- No manual token management needed

---

## Testing the Installation

### Test 1: Connection Test
```
Use the test_connection tool
```

Expected: Success message with server info

### Test 2: Rate Limiting Status
```
Check rate limit status using get_rate_limit_status
```

Expected: Shows available burst tokens and daily quota

### Test 3: List Workflows
```
List workflows for my location using list_workflows
```

Expected: Array of workflows (or empty array if none exist)

### Test 4: Search Contacts
```
Search for contacts in my location using search_contacts
```

Expected: Array of contacts (or empty array if none exist)

### Test 5: List Calendars
```
List calendars using list_calendars
```

Expected: Array of calendars with availability info

---

## Available Tools (25 Total)

### Test & Diagnostics (1)
- `test_connection` - Verify server is running

### OAuth & Authentication (3)
- `authenticate_ghl` - Initiate OAuth flow
- `test_oauth` - Verify authentication status
- `get_oauth_status` - Get detailed OAuth information

### Rate Limiting (2)
- `get_rate_limit_status` - Check rate limit status
- `reset_rate_limits` - Reset counters (testing only)

### Workflow Management (5)
- `create_workflow` - Create new workflow
- `list_workflows` - List all workflows
- `get_workflow` - Get workflow details
- `update_workflow` - Update workflow configuration
- `delete_workflow` - Delete workflow

### Contact Management (4)
- `create_contact` - Create new contact
- `search_contacts` - Search contacts with filters
- `get_contact` - Get contact details
- `update_contact` - Update contact information

### Funnel Management (3)
- `list_funnels` - List all funnels
- `get_funnel_pages` - Get pages for a funnel
- `create_funnel` - Create new funnel with pages

### Form Management (2)
- `list_forms` - List all forms
- `get_form_submissions` - Get form submissions

### Calendar Management (2)
- `list_calendars` - List all calendars
- `create_appointment` - Create appointment

---

## Deployment Checklist

Before going to production, verify:

- [ ] **Environment Variables**: All 4 variables set (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ENCRYPTION_KEY)
- [ ] **Build Success**: `npm run build` completes with 0 errors
- [ ] **File Exists**: `dist/index.js` is present
- [ ] **Claude Code Config**: `.mcp.json` has ghl-api server entry
- [ ] **Claude Code Restart**: Server appears in MCP panel as "Running"
- [ ] **GHL Marketplace App**: Created with correct redirect URI
- [ ] **OAuth Scopes**: All required scopes configured
- [ ] **OAuth Flow**: Successfully authenticated and received tokens
- [ ] **Token Storage**: `.tokens.enc` file exists and is git-ignored
- [ ] **Test Tools**: All 5 test scenarios pass
- [ ] **Rate Limiting**: Status check shows correct limits
- [ ] **Logs**: Server logs visible in Claude Code MCP panel

---

## Security Best Practices

### 1. Never Commit Secrets
```bash
# Verify .gitignore includes:
.env
.env.local
.tokens.enc
```

### 2. Rotate Encryption Key Periodically
```bash
# Generate new key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Update .env with new key
# Re-authenticate (tokens will be re-encrypted)
```

### 3. Use Environment-Specific Credentials
- **Development**: Use test GHL location
- **Staging**: Use staging location with limited data
- **Production**: Use production location with full data

### 4. Monitor Rate Limits
```bash
# Check rate limit status regularly
get_rate_limit_status
```

### 5. Review OAuth Scopes
- Only request scopes your application needs
- Remove unused scopes from Marketplace app settings

---

## Next Steps

1. **Read TROUBLESHOOTING.md** for common issues
2. **Review tool documentation** in README.md
3. **Test each tool** to familiarize yourself with functionality
4. **Build your integration** using the 25 available tools

---

## Support

- **Documentation**: See README.md for tool details
- **Troubleshooting**: See TROUBLESHOOTING.md
- **Issues**: Report bugs in project repository
- **GHL API Docs**: https://highlevel.stoplight.io/docs/integrations/

---

**Deployment Complete!** 🎉

Your GHL API MCP Server is now ready to use with Claude Code.
