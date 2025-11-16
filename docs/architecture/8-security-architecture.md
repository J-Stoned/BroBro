# 8. Security Architecture

### 8.1 Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| **OAuth token leakage** | High | Encrypted storage, never in git, auto-rotation |
| **API key exposure** | High | Environment variables only, .env in .gitignore |
| **Man-in-the-middle attacks** | Medium | HTTPS for all external API calls (GHL, YouTube, Firecrawl) |
| **Unauthorized MCP access** | Low | Local-only MCP servers (stdio/localhost), no external exposure |
| **Malicious knowledge injection** | Medium | Curated sources only, manual review of YouTube channels |
| **Rate limit abuse** | Low | Built-in rate limiting, queue management |

### 8.2 Secrets Management

**OAuth Tokens:**

```typescript
// mcp-servers/ghl-api-server/src/auth/token-storage.ts

import crypto from 'crypto';
import fs from 'fs/promises';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY; // 32-byte key
const TOKEN_FILE = './.tokens.enc';

interface EncryptedTokens {
  iv: string;
  encryptedData: string;
}

async function saveTokens(tokens: TokenStore): Promise<void> {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', ENCRYPTION_KEY, iv);

  let encrypted = cipher.update(JSON.stringify(tokens), 'utf8', 'hex');
  encrypted += cipher.final('hex');

  await fs.writeFile(TOKEN_FILE, JSON.stringify({
    iv: iv.toString('hex'),
    encryptedData: encrypted
  }));
}

async function loadTokens(): Promise<TokenStore> {
  const data: EncryptedTokens = JSON.parse(await fs.readFile(TOKEN_FILE, 'utf8'));
  const decipher = crypto.createDecipheriv(
    'aes-256-cbc',
    ENCRYPTION_KEY,
    Buffer.from(data.iv, 'hex')
  );

  let decrypted = decipher.update(data.encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return JSON.parse(decrypted);
}
```

**`.gitignore` (Critical):**

```
.env
.tokens.enc
chroma_db/
kb/ghl-docs/raw/
kb/youtube-transcripts/by-creator/
node_modules/
dist/
*.log
```

### 8.3 API Security

**GHL API Calls:**

```typescript
// All API calls use HTTPS
const GHL_BASE_URL = 'https://services.leadconnectorhq.com';

// Headers for every request
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Version': '2021-04-15',  // Required by GHL API v2
  'Content-Type': 'application/json'
};

// Validate SSL certificates
const httpsAgent = new https.Agent({ rejectUnauthorized: true });
```

---
