# OAuth 2.0 Setup Guide for GHL Wiz

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create GHL Marketplace App](#step-1-create-ghl-marketplace-app)
4. [Step 2: Configure Environment Variables](#step-2-configure-environment-variables)
5. [Step 3: Generate Encryption Key](#step-3-generate-encryption-key)
6. [Step 4: Build and Start MCP Server](#step-4-build-and-start-mcp-server)
7. [Step 5: Complete OAuth Authorization](#step-5-complete-oauth-authorization)
8. [Step 6: Verify Authentication](#step-6-verify-authentication)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Overview

This guide walks you through setting up OAuth 2.0 authentication for the GHL Wiz MCP server. After completing these steps, you'll be able to:

- Authenticate with your GoHighLevel account
- Make API calls on behalf of your account
- Automatically refresh access tokens (no manual intervention needed)
- Securely store encrypted tokens locally

**Time required:** 10-15 minutes

---

## Prerequisites

Before starting, ensure you have:

- ✅ Node.js 20+ installed (`node --version` to check)
- ✅ A GoHighLevel account with admin access
- ✅ Access to GHL Marketplace (https://marketplace.gohighlevel.com)
- ✅ GHL Wiz MCP server installed (Story 3.1 complete)
- ✅ Claude Desktop or compatible MCP client

---

## Step 1: Create GHL Marketplace App

### 1.1 Access GHL Marketplace

1. Open your browser and navigate to: https://marketplace.gohighlevel.com
2. Sign in with your GoHighLevel credentials
3. Click on **"Apps"** in the top navigation
4. Click **"Create App"** button

### 1.2 Configure App Settings

**Basic Information:**
- **App Name:** `GHL Wiz MCP Server` (or your preferred name)
- **App Description:** `MCP server for AI-powered GoHighLevel workflows`
- **Category:** `Integrations` or `Automation`
- **App Type:** `Private` (for personal use)

**Developer Contact:**
- **Support Email:** Your email address
- **Website URL:** (optional) Your website or leave blank

Click **"Save"** to create the app.

### 1.3 Configure OAuth Settings

Navigate to the **OAuth** tab in your app settings:

1. **Redirect URIs:**
   - Add: `http://localhost:3456/oauth/callback`
   - Click **"Add"** to save
   - **IMPORTANT:** This must match exactly (including port 3456)

2. **Scopes:** Select the following scopes (required for GHL Wiz features):
   - ✅ `contacts.readonly` - Read contact information
   - ✅ `contacts.write` - Create and update contacts
   - ✅ `workflows.readonly` - Read workflow configurations
   - ✅ `workflows.write` - Create and manage workflows
   - ✅ `calendars.readonly` - Read calendar configurations
   - ✅ `calendars.write` - Create appointments
   - ✅ `opportunities.readonly` - Read pipeline data
   - ✅ `opportunities.write` - Manage opportunities
   - ✅ `locations.readonly` - Read location information
   - ✅ `forms.readonly` - Read forms
   - ✅ `surveys.readonly` - Read surveys

3. Click **"Save OAuth Settings"**

### 1.4 Copy Credentials

You'll need these values for the next step:

1. **Client ID:** Copy the value shown (looks like: `abc123xyz...`)
2. **Client Secret:** Click **"Show"** and copy the secret (looks like: `def456uvw...`)

**⚠️ SECURITY WARNING:** Never share your Client Secret or commit it to git!

---

## Step 2: Configure Environment Variables

### 2.1 Create .env File

Navigate to your MCP server directory:

```bash
cd "C:\Users\justi\BroBro\mcp-servers\ghl-api-server"
```

Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

Or on Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2.2 Add OAuth Credentials

Open `.env` in your text editor and update these values:

```bash
# Paste your Client ID from Step 1.4
GHL_CLIENT_ID=your_actual_client_id_here

# Paste your Client Secret from Step 1.4
GHL_CLIENT_SECRET=your_actual_client_secret_here

# Redirect URI (must match GHL Marketplace app exactly)
GHL_REDIRECT_URI=http://localhost:3456/oauth/callback
```

**Example (with fake credentials):**
```bash
GHL_CLIENT_ID=abc123xyz789def456ghi012jkl345mno678pqr901
GHL_CLIENT_SECRET=def456uvw123xyz789abc012ghi345jkl678mno901
GHL_REDIRECT_URI=http://localhost:3456/oauth/callback
```

---

## Step 3: Generate Encryption Key

### 3.1 Why Encryption Key?

The encryption key secures your OAuth tokens at rest. Tokens are encrypted with **AES-256-CBC** before saving to disk.

### 3.2 Generate Key

Run this command in your terminal:

**macOS/Linux/Git Bash:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Windows PowerShell:**
```powershell
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Windows Command Prompt:**
```cmd
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 3.3 Add Key to .env

Copy the generated key (should be 64 hexadecimal characters) and add to `.env`:

```bash
# Example: abc123...xyz789 (64 characters)
ENCRYPTION_KEY=your_generated_64_character_hex_key_here
```

**⚠️ IMPORTANT:**
- The key must be exactly 64 hexadecimal characters (0-9, a-f)
- Never change this key after creating tokens (you won't be able to decrypt them)
- Backup this key somewhere safe (password manager, encrypted file)

---

## Step 4: Build and Start MCP Server

### 4.1 Install Dependencies

If you haven't already:

```bash
cd "C:\Users\justi\BroBro\mcp-servers\ghl-api-server"
npm install
```

### 4.2 Build TypeScript

```bash
npm run build
```

Expected output:
```
> ghl-api-server@1.0.0 build
> tsc

(No errors = success)
```

### 4.3 Verify Build

Check that OAuth files were compiled:

```bash
ls dist/auth/
```

You should see:
- `oauth-manager.js`
- `callback-server.js`
- `token-store.js`

---

## Step 5: Complete OAuth Authorization

### 5.1 Start Server (if not already running)

If the MCP server is not already running via Claude Desktop, you can test it manually:

```bash
node dist/index.js
```

Or start it through Claude Desktop (recommended).

### 5.2 Run authenticate_ghl Tool

**In Claude Desktop:**

1. Open Claude Desktop
2. Ensure the GHL Wiz MCP server is configured in settings
3. Send this message to Claude:

```
Please run the authenticate_ghl tool to connect to my GoHighLevel account.
```

**What happens:**
1. Claude calls the `authenticate_ghl` MCP tool
2. A local callback server starts on port 3456
3. Your default browser opens to GHL authorization page
4. You'll see GHL location selection and permission request

### 5.3 Grant Permissions in Browser

1. **Select Location:** Choose the GHL location you want to connect
2. **Review Permissions:** Ensure all required scopes are listed
3. **Click "Authorize"** to grant access

### 5.4 Authorization Complete

After clicking "Authorize":

1. Browser redirects to `http://localhost:3456/oauth/callback`
2. You'll see a success page: **"Authentication Successful!"**
3. Page auto-closes after 2 seconds
4. Tokens are encrypted and saved to `.tokens.enc`
5. Callback server automatically shuts down

**Success indicators:**
- ✅ Green checkmark on success page
- ✅ `.tokens.enc` file created in project root
- ✅ Server logs show "OAuth tokens obtained and saved successfully"

---

## Step 6: Verify Authentication

### 6.1 Run test_oauth Tool

**In Claude Desktop:**

```
Please run the test_oauth tool to verify my GoHighLevel authentication.
```

**Expected successful response:**

```json
{
  "authenticated": true,
  "locationId": "abc123...",
  "companyId": "xyz789...",
  "expiresAt": "2025-10-27T18:30:00.000Z",
  "expiresIn": "23 hours 55 minutes",
  "willRefresh": false,
  "scopes": [
    "contacts.readonly",
    "contacts.write",
    ...
  ],
  "message": "OAuth authentication is valid and working correctly. Token expires in 23 hours 55 minutes. Token is fresh, no refresh needed yet."
}
```

### 6.2 Check OAuth Status (Advanced)

For detailed diagnostics:

```
Please run the get_oauth_status tool to check my OAuth configuration.
```

This shows:
- ✅ Environment variables status
- ✅ Encryption key validity
- ✅ Token file existence
- ✅ Authentication status
- ⚠️ Any configuration issues
- 💡 Recommendations for fixing problems

---

## Troubleshooting

### Issue: "Port 3456 is already in use"

**Symptoms:**
- Error when running `authenticate_ghl`
- Message: "Failed to start OAuth callback server"

**Solutions:**

1. **Check if port is in use:**
   ```bash
   # Windows
   netstat -ano | findstr :3456

   # macOS/Linux
   lsof -i :3456
   ```

2. **Kill process using port 3456:**
   ```bash
   # Windows (if PID is 1234)
   taskkill /PID 1234 /F

   # macOS/Linux
   kill -9 <PID>
   ```

3. **Alternative:** Change redirect URI in both `.env` and GHL Marketplace app to use different port (e.g., 3457)

---

### Issue: "Invalid OAuth credentials"

**Symptoms:**
- Error: "Invalid client credentials"
- 401 Unauthorized from GHL API

**Solutions:**

1. **Verify credentials in .env:**
   - Check `GHL_CLIENT_ID` matches Marketplace app exactly
   - Check `GHL_CLIENT_SECRET` matches (no extra spaces)
   - No quotes around values in .env

2. **Check Marketplace app status:**
   - App must be in "Active" status
   - OAuth settings must be saved

3. **Regenerate credentials:**
   - Go to GHL Marketplace app
   - Click "Regenerate Client Secret"
   - Update .env with new secret
   - Try authentication again

---

### Issue: "ENCRYPTION_KEY must be 64 hex characters"

**Symptoms:**
- Server fails to start
- Error about encryption key length or format

**Solutions:**

1. **Regenerate key:**
   ```bash
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

2. **Verify in .env:**
   - Exactly 64 characters
   - Only hexadecimal (0-9, a-f, A-F)
   - No spaces or quotes

---

### Issue: "Authorization code expired"

**Symptoms:**
- Error after clicking "Authorize" in browser
- Message: "Authorization code expired or already used"

**Solutions:**

1. **Complete flow faster:**
   - Authorization codes expire in ~60 seconds
   - Don't refresh the callback page
   - Complete authorization quickly after browser opens

2. **Restart authentication:**
   - Run `authenticate_ghl` tool again
   - New authorization URL will be generated

---

### Issue: "Token decryption failed"

**Symptoms:**
- Error: "Token decryption failed"
- "bad decrypt" error

**Causes & Solutions:**

1. **Encryption key changed:**
   - Cannot decrypt tokens with different key
   - **Solution:** Delete `.tokens.enc` and re-authenticate

2. **Token file corrupted:**
   - File may have been edited manually
   - **Solution:** Delete `.tokens.enc` and re-authenticate

3. **Delete tokens and re-auth:**
   ```bash
   cd "C:\Users\justi\BroBro\mcp-servers\ghl-api-server"
   rm .tokens.enc
   # Then run authenticate_ghl tool again
   ```

---

### Issue: "Refresh token expired"

**Symptoms:**
- Error after 60 days of inactivity
- Message: "Refresh token expired"

**Solution:**

1. **Re-authenticate:**
   - Run `authenticate_ghl` tool again
   - Complete OAuth flow in browser
   - New refresh token will be issued

2. **Prevention:**
   - Use GHL Wiz at least once every 60 days
   - Tokens auto-refresh when used, resetting the 60-day timer

---

### Issue: "Redirect URI mismatch"

**Symptoms:**
- Error in browser after clicking "Authorize"
- GHL shows: "redirect_uri_mismatch"

**Solutions:**

1. **Check exact match:**
   - `.env`: `GHL_REDIRECT_URI=http://localhost:3456/oauth/callback`
   - GHL Marketplace: Must have exactly `http://localhost:3456/oauth/callback`

2. **Common mistakes:**
   - ❌ `https` instead of `http`
   - ❌ Wrong port number
   - ❌ Trailing slash: `http://localhost:3456/oauth/callback/`
   - ❌ Missing `/oauth/callback` path

3. **Fix in Marketplace:**
   - Go to app OAuth settings
   - Delete incorrect URI
   - Add correct URI: `http://localhost:3456/oauth/callback`
   - Save settings

---

## Security Best Practices

### ✅ DO

1. **Use strong encryption key:**
   - Generate with `crypto.randomBytes(32)`
   - Store in password manager
   - Never share or commit to git

2. **Keep credentials secret:**
   - `.env` file in `.gitignore` (already configured)
   - Never commit `.env` to version control
   - Don't share Client Secret

3. **Backup encryption key:**
   - If you lose the key, you must re-authenticate
   - Store in secure password manager
   - Don't store in plain text files

4. **Use private GHL app:**
   - Set app type to "Private" if for personal use
   - Only grant required scopes (don't request unnecessary permissions)

5. **Monitor token usage:**
   - Run `test_oauth` periodically to check status
   - Review GHL audit logs for API activity

### ❌ DON'T

1. **Don't commit secrets:**
   - ❌ Never commit `.env` to git
   - ❌ Never commit `.tokens.enc` to git
   - ❌ Never hardcode credentials in code

2. **Don't share tokens:**
   - ❌ Don't send `.tokens.enc` to others
   - ❌ Don't share access tokens in logs or messages
   - ❌ Don't expose encryption key

3. **Don't modify encrypted files:**
   - ❌ Don't edit `.tokens.enc` manually
   - ❌ Don't copy `.tokens.enc` between machines (different encryption keys)

4. **Don't disable security features:**
   - ❌ Don't skip encryption
   - ❌ Don't use weak encryption keys (e.g., "password123")
   - ❌ Don't store tokens in plaintext

---

## Token Lifecycle

### Access Token

- **Expiry:** 24 hours after issuance
- **Auto-refresh:** Yes (5-minute buffer before expiry)
- **Refresh trigger:** Any API call when token is expiring soon
- **Storage:** Encrypted in `.tokens.enc`

### Refresh Token

- **Expiry:** 60 days after issuance (or last use)
- **Auto-refresh:** Yes (when used to get new access token)
- **Extends on use:** Each access token refresh resets the 60-day timer
- **Storage:** Encrypted in `.tokens.enc`

### Token Refresh Flow

```
User makes API call
  ↓
Check if access token expires within 5 minutes
  ↓
  If YES:
    1. Use refresh token to get new access token
    2. Update .tokens.enc with new tokens
    3. Reset 60-day refresh token expiry
    4. Proceed with API call
  ↓
  If NO:
    Proceed with API call (token is still valid)
```

---

## Next Steps

After completing OAuth setup, you can:

1. **Use GHL API Tools:**
   - Create workflows
   - Manage contacts
   - Set up calendars
   - Query pipelines

2. **Explore MCP Features:**
   - Ask Claude to create workflows for you
   - Let AI analyze your GHL data
   - Automate repetitive tasks

3. **Monitor Authentication:**
   - Run `test_oauth` to check status
   - Review token expiry times
   - Watch for auto-refresh logs

---

## Support

### Resources

- **GHL API Documentation:** https://highlevel.stoplight.io/
- **GHL Marketplace:** https://marketplace.gohighlevel.com
- **GHL Wiz GitHub:** (Your repo URL)
- **MCP Documentation:** https://modelcontextprotocol.io

### Getting Help

If you encounter issues not covered in this guide:

1. Check server logs for detailed error messages
2. Run `get_oauth_status` tool for diagnostics
3. Review Story 3.2 troubleshooting guide
4. Check GHL API status page

---

**Document Version:** 1.0
**Last Updated:** 2025-10-26
**Story:** 3.2 - OAuth 2.0 Authentication Implementation
**Author:** James Rodriguez (Senior Developer)
