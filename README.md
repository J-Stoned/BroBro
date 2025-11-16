# BroBro - GoHighLevel AI Assistant

A comprehensive AI assistant for GoHighLevel with a cloud-based knowledge base powered by Google File Search, supporting dual AI backends (Claude + Gemini).

## Overview

BroBro helps you build systems inside GoHighLevel by providing:
- **275 Specialized Commands:** Complete automation library with Josh Wash business architecture
- **AI-Powered Semantic Search:** Find commands using natural language (<1s response time)
- **Local Knowledge Base:** Trained on official GHL docs, expert YouTube tutorials, and curated best practices
- **Josh Wash Workflows:** 4 proven patterns with validated success metrics (85%+ performance)
- **Interactive CLI Tool:** 7-step workflow execution from concept to deployment
- **Comprehensive Help System:** Fuzzy matching, onboarding guide, and complete command reference

## Quick Start

### 🌐 **Web UI (Recommended - New!)**

Start the modern web interface with dual AI backends:

```bash
# Windows
start-servers.bat

# Mac/Linux
./start-servers.sh
```

Then open: **http://localhost:5173**

📖 See [WEB_UI_SETUP_GUIDE.md](WEB_UI_SETUP_GUIDE.md) for detailed instructions

### 💻 **CLI Tool**

**New to BroBro?** Start here:

1. **[Getting Started Guide](docs/ONBOARDING.md)** - 5-minute quickstart
2. **[Command Reference](docs/COMMAND_REFERENCE.md)** - All 275 commands
3. **[CLI Documentation](.claude/commands/cli/README.md)** - CLI tool usage

**Your first command**:
```bash
python .claude/commands/cli/ghl-cli.py appointment-reminder "setup 24-hour reminder"
```

## Prerequisites

Before you begin, ensure you have:

- **Node.js 20+** (LTS version) - [Download](https://nodejs.org/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Claude Code** - AI development environment
- **Git** - Version control

### Verify Prerequisites

```bash
node --version  # Should be v20.0.0 or higher
docker --version  # Should be installed and running
```

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd brobro
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

- **GHL_CLIENT_ID** & **GHL_CLIENT_SECRET:** Get from [GHL Marketplace](https://marketplace.gohighlevel.com/)
- **FIRECRAWL_API_KEY:** Get free key at [Firecrawl.dev](https://www.firecrawl.dev/)
- **ENCRYPTION_KEY:** Generate with `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`

### 4. Configure API Keys

Update your `.env` file with:
- **ANTHROPIC_API_KEY**: Get from [Anthropic Console](https://console.anthropic.com/account/keys)
- **GOOGLE_API_KEY**: Get from [Google AI Studio](https://aistudio.google.com/apikey)
- **GEMINI_FILE_SEARCH_STORE_ID**: Your knowledge base store ID

**Note:** No Docker required - knowledge base is cloud-hosted via Gemini File Search!

### 5. Start Backend Server

Launch the FastAPI backend:

```bash
cd web/backend
python -m uvicorn main:app --reload
```

Backend available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs` (Swagger UI)

### 6. Verify Installation

Test that everything is working:

```bash
curl http://localhost:8000/api/health
```

Should return: `{"status": "healthy", ...}`

### 7. Configure MCP Servers in Claude Code

Add the following to your `.claude/settings.local.json`:

```json
{
  "mcp": {
    "servers": {
      "ghl-api": {
        "command": "node",
        "args": ["./mcp-servers/ghl-api-server/dist/index.js"],
        "env": {
          "GHL_CLIENT_ID": "${GHL_CLIENT_ID}",
          "GHL_CLIENT_SECRET": "${GHL_CLIENT_SECRET}",
          "ENCRYPTION_KEY": "${ENCRYPTION_KEY}"
        }
      },
      "firecrawl": {
        "command": "npx",
        "args": ["-y", "@mendable/firecrawl-mcp"],
        "env": {
          "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
        }
      },
      "youtube-transcript-pro": {
        "command": "npx",
        "args": ["-y", "youtube-transcript-pro-mcp"]
      },
      "youtube-intelligence": {
        "command": "npx",
        "args": ["-y", "youtube-intelligence-suite-mcp"]
      }
    }
  }
}
```

**Note:** Restart Claude Code after updating MCP server configuration.

## Project Structure

```
ghl-wiz/
├── mcp-servers/          # Custom MCP servers
│   └── ghl-api-server/  # GoHighLevel API MCP
├── scripts/              # Knowledge base pipeline
│   ├── scrape-ghl-docs.js
│   ├── extract-yt-transcripts.js
│   ├── chunk-documents.js
│   ├── embed-content.js
│   └── build-knowledge-base.js
├── kb/                   # Knowledge base content
│   ├── ghl-docs/        # GHL documentation
│   ├── youtube-transcripts/ # Tutorial transcripts
│   ├── best-practices/  # Curated guides
│   └── youtube-sources.json # Video sources config
├── config/               # Configuration files
├── tests/                # Test suite
└── docs/                 # Documentation
```

## Usage

### Knowledge Base Management

BroBro's knowledge base is managed through **Gemini File Search**. Content is indexed in a cloud-hosted store.

For detailed configuration and management, see:
- [Knowledge Base Setup Guide](KNOWLEDGE_BASE_SETUP.md)
- [YouTube Content Management](HOW_TO_ADD_YOUTUBE_CONTENT.md)

### Development

```bash
npm run build-ghl-mcp    # Build GHL API MCP server
npm run dev-ghl-mcp      # Run MCP server in dev mode
npm run test-mcp         # Test MCP servers
npm run test-kb          # Test knowledge base
npm test                 # Run all tests
```

## Knowledge Base - Gemini File Search

BroBro uses **Google Gemini File Search** for cloud-hosted semantic search of your knowledge base.

### Setup

No infrastructure setup needed! Gemini File Search is cloud-hosted and requires only:

1. **Google API Key** - Get from [Google AI Studio](https://aistudio.google.com/apikey)
2. **Gemini File Search Store ID** - Your knowledge base store ID
3. Environment variables configured in `.env`

### Testing the Knowledge Base

```bash
# Test Gemini File Search connection
curl "http://localhost:8000/api/search?q=your_search_query"

# Expected response includes:
# - Relevant search results
# - Source attribution
# - Confidence scores
```

### Knowledge Base Content

The knowledge base includes:
- **GHL Documentation:** Official GoHighLevel help articles
- **YouTube Tutorials:** GHL expert tutorials and walkthroughs
- **Best Practices:** Curated workflow strategies and optimization guides
- **Indexed Items:** 1,235+ searchable knowledge base entries

### Adding Content

Content can be added to Gemini File Search through:
1. **Batch uploads** - Add multiple files at once
2. **API integration** - Programmatic content addition
3. **Direct management** - Via Google AI Studio interface

Refer to `.env.example` for configuration details.

## Content Acquisition MCP Servers

GHL Wiz uses three MCP servers to acquire content for the knowledge base:

### Firecrawl (Documentation Scraping)

**Purpose:** Scrape GHL documentation from help.gohighlevel.com

**Setup:**
1. Get free API key at [Firecrawl.dev](https://www.firecrawl.dev/)
2. Add to `.env`: `FIRECRAWL_API_KEY=your_key_here`
3. Server is auto-configured in `.mcp.json`

**Tools Provided:**
- **scrape** - Single page scraping with Markdown output
- **crawl** - Multi-page crawling with sitemap support

**Features:**
- Handles single-page applications (SPAs)
- Respects robots.txt and rate limits
- Built-in retry logic for transient failures
- Clean Markdown conversion

**Usage:**
```bash
# Test Firecrawl configuration
npm run test:firecrawl
```

**Expected Content:**
- ~500 pages from help.gohighlevel.com
- API documentation from marketplace
- Feature guides and tutorials

### YouTube Transcript Pro (Primary)

**Purpose:** Extract transcripts from GHL tutorial videos

**Setup:**
- No API key required
- Auto-configured in `.mcp.json`
- Uses npx to run on-demand

**Tools Provided:**
- **get_transcript** - Plain text transcript extraction
- **get_timed_transcript** - Transcript with timestamps
- **get_video_info** - Video metadata (title, creator, duration)
- **search_videos** - Search for videos by query

**Features:**
- Production-ready with hybrid architecture
- Reliable transcript extraction
- Supports multiple languages (default: English)
- No rate limiting (uses public YouTube data)

**Usage:**
```bash
# Test YouTube Transcript Pro
npm run test:youtube
```

**Target Content Sources:**
- **Robb Bailey** - GHL workflows, automation, expert tutorials
- **Shaun Clark** - GHL setup, best practices, agency workflows
- **GoHighLevel Official** - Product updates, feature announcements

### YouTube Intelligence Suite (Fallback)

**Purpose:** Advanced YouTube features and fallback for Transcript Pro

**Setup:**
- No API key required
- Auto-configured in `.mcp.json`
- Used when Transcript Pro fails or for advanced features

**Tools Provided (8 total):**
- **get_transcript** - Transcript with smart format handling
- **get_video_info** - Detailed video metadata
- **search_videos** - Advanced search with filters
- **get_channel_info** - Channel metadata and statistics
- **get_comments** - Extract video comments
- **analyze_sentiment** - Sentiment analysis of transcript
- **extract_topics** - Topic extraction from content
- **summarize** - AI-powered video summarization

**When to Use:**
- Transcript Pro fails or times out
- Need advanced features (sentiment, topics, summarization)
- Need channel info or comments
- Exploratory data analysis

### Fallback Strategy

**Primary:** YouTube Transcript Pro (reliable, production-ready)
**Fallback:** YouTube Intelligence Suite (more features, use if primary fails)

### Testing Content Acquisition

```bash
# Test Firecrawl configuration
npm run test:firecrawl

# Test YouTube servers
npm run test:youtube

# Test all content acquisition servers
npm run test:content-acquisition
```

### Content Sources Configuration

YouTube video sources are configured in `kb/youtube-sources.json`:

```json
{
  "creators": [
    {
      "name": "Robb Bailey",
      "searchQueries": ["gohighlevel workflow", "ghl automation"],
      "maxVideos": 50
    },
    {
      "name": "Shaun Clark",
      "searchQueries": ["gohighlevel tutorial", "ghl setup"],
      "maxVideos": 40
    },
    {
      "name": "GoHighLevel Official",
      "searchQueries": ["gohighlevel", "ghl features"],
      "maxVideos": 60
    }
  ]
}
```

**Estimated Total Content:**
- **Documentation:** ~500 pages
- **YouTube Tutorials:** ~150 videos (90-150 relevant videos)
- **Total Knowledge Base:** ~7,700 vectors (~11 MB)

## YouTube Sources Configuration

GHL Wiz uses a configuration file to manage YouTube content sources for the knowledge base.

### Configuration File

**Location:** `kb/youtube-sources.json`

This file defines:
- **Creators** - YouTube channels to scrape (Robb Bailey, Shaun Clark, GHL Official)
- **Specific Videos** - Individual high-value videos
- **Playlists** - Curated playlists on specific topics
- **Extraction Settings** - Language, date filters, video duration limits
- **Topic Categories** - Standardized categorization system

### Pre-configured Creators

The configuration includes these GHL experts by default:

1. **Robb Bailey** (@GoHighLevelwithRobbBailey)
   - Focus: Workflows, automation, platform features
   - Max videos: 30
   - Priority: High

2. **Shaun Clark** (@GoHighLevelCEO)
   - Focus: Strategy, product updates, vision
   - Max videos: 20
   - Priority: High

3. **GoHighLevel Official** (@GoHighLevel)
   - Focus: Product updates, features, tutorials
   - Max videos: 50
   - Priority: Medium

### Adding New Sources

**Add a YouTube Channel:**
```json
{
  "name": "Creator Name",
  "channelId": "@ChannelHandle",
  "channelUrl": "https://www.youtube.com/@ChannelHandle",
  "description": "What this creator specializes in",
  "maxVideos": 30,
  "topics": ["workflows", "api", "best-practices"],
  "priority": "high",
  "enabled": true,
  "notes": "Any special instructions"
}
```

**Add a Specific Video:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "title": "Video Title",
  "creator": "Creator Name",
  "category": "must-have",
  "topics": ["workflows"],
  "priority": "high",
  "enabled": true,
  "notes": "Why this video is valuable"
}
```

**Add a Playlist:**
```json
{
  "url": "https://www.youtube.com/playlist?list=PLAYLIST_ID",
  "name": "Playlist Name",
  "creator": "Creator Name",
  "description": "What this playlist covers",
  "topics": ["api", "integration"],
  "priority": "high",
  "enabled": true,
  "maxVideosFromPlaylist": 20,
  "notes": "Special focus areas"
}
```

### Topic Categories

Use these standardized topics for consistency:

- **workflows** - Workflow automation and triggers
- **automation** - Marketing automation and sequences
- **funnels** - Funnel building and optimization
- **forms** - Form creation and conversion optimization
- **saas-mode** - SaaS mode configuration and white-labeling
- **api** - API integration and development
- **best-practices** - Proven strategies and optimization techniques
- **product-updates** - New features and platform updates
- **integrations** - Third-party integrations (Stripe, Twilio, etc.)
- **calendars** - Calendar and appointment management
- **snapshots** - Snapshot marketplace and usage
- **strategy** - Business strategy and use cases

### Priority Levels

- **high** - Extract first, most valuable content
- **medium** - Extract after high priority
- **low** - Extract if capacity allows

### Extraction Settings

The configuration includes smart filters:
- **Date Filter** - Focus on content after 2024-01-01 for latest features
- **Duration Limits** - Minimum 3 minutes, maximum 2 hours
- **Skip Shorts** - Exclude YouTube Shorts (too brief)
- **Language** - Prefer English with fallback to en-US, en-GB
- **Auto-generated Transcripts** - Include if manual transcripts unavailable

### Running Extraction

```bash
# Extract based on youtube-sources.json configuration
npm run extract-yt

# Or run directly with custom config
node scripts/extract-yt-transcripts.js --source-config kb/youtube-sources.json --limit 100
```

### Output Structure

Extracted transcripts are saved to:
```
kb/youtube-transcripts/
├── by-creator/
│   ├── robb-bailey/
│   ├── shaun-clark/
│   └── gohighlevel-official/
├── by-topic/
│   ├── workflows/
│   ├── api/
│   └── ...
└── index.json (metadata index)
```

### Finding YouTube IDs

**Channel Handle:**
- Visible in URL: youtube.com/@ChannelHandle
- Modern format using @ symbol

**Video ID:**
- Found in URL: youtube.com/watch?v=VIDEO_ID
- 11-character alphanumeric string

**Playlist ID:**
- Found in URL: youtube.com/playlist?list=PLAYLIST_ID
- Typically starts with PL

## NPM Scripts Reference

| Script | Description |
|--------|-------------|
| `npm run test:firecrawl` | Test Firecrawl MCP server configuration |
| `npm run test:youtube` | Test YouTube MCP servers |
| `npm run test:content-acquisition` | Test all content acquisition servers |
| `npm run build-ghl-mcp` | Build GHL API MCP server |
| `npm run dev-ghl-mcp` | Run GHL MCP in dev mode |
| `npm run test-mcp` | Test MCP servers |
| `npm run test-kb` | Test knowledge base |
| `npm test` | Run all tests |

## Troubleshooting

### Backend Connection Issues

**Problem:** Cannot connect to backend at `http://localhost:8000`

**Solutions:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check backend logs for errors
# Review the terminal where FastAPI is running

# 3. Ensure environment variables are set
# Check .env file has GOOGLE_API_KEY and GEMINI_FILE_SEARCH_STORE_ID
```

### Knowledge Base Not Returning Results

**Problem:** Search queries return no results

**Solutions:**
- Verify `GEMINI_FILE_SEARCH_STORE_ID` is correct in `.env`
- Verify `GOOGLE_API_KEY` is valid and has proper permissions
- Check that content has been indexed in Gemini File Search
- Test with simple search queries first

### MCP Server Not Loading

**Problem:** MCP servers don't appear in Claude Code

**Solutions:**
- Verify `.claude/settings.local.json` syntax is valid JSON
- Check MCP server paths are correct
- Restart Claude Code
- Review Claude Code logs for errors

### Node.js Version Issues

**Problem:** `npm install` fails with version errors

**Solutions:**
- Verify Node.js version: `node --version` (must be 20+)
- Use nvm to switch versions: `nvm use 20`
- Delete `node_modules/` and `package-lock.json`, then `npm install`

### Docker Issues on Windows

**Problem:** Docker commands fail or Chroma won't start

**Solutions:**
- Ensure Docker Desktop is running
- Enable WSL 2 backend in Docker Desktop settings
- Allocate at least 4GB memory to Docker
- Check Windows Firewall isn't blocking Docker

### Environment Variables Not Loading

**Problem:** App can't find environment variables

**Solutions:**
- Ensure `.env` file exists (copy from `.env.example`)
- Check `.env` is in project root
- Verify variable names match exactly
- Restart application after changing `.env`

## Documentation

- **[PRD](docs/prd.md)** - Product Requirements Document
- **[Architecture](docs/architecture.md)** - Technical Architecture
- **[Stories](docs/stories/)** - User Stories
- **[Knowledge Base Guide](kb/README.md)** - KB usage and management

## Technology Stack

- **Runtime:** Node.js 20+ LTS
- **Backend:** Python 3.9+, FastAPI
- **Frontend:** React 18, Vite, TypeScript 5.x
- **Languages:** Python, TypeScript 5.x, JavaScript ES2022
- **MCP Framework:** FastMCP, @modelcontextprotocol/sdk
- **Knowledge Base:** Google Gemini File Search (cloud-hosted)
- **AI Backends:** Claude (Anthropic), Gemini (Google)
- **Testing:** Jest, pytest
- **Code Quality:** ESLint, Prettier

## Development

### Code Quality Tools

GHL Wiz uses ESLint, Prettier, and Jest to maintain high code quality and consistency.

**Linting:**
```bash
# Run ESLint
npm run lint

# Auto-fix linting issues
npm run lint:fix
```

**Formatting:**
```bash
# Format all files
npm run format

# Check formatting without changing files
npm run format:check
```

**Testing:**
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

### Pre-commit Hooks

The project uses Husky and lint-staged to automatically lint and format code before commits.

**What happens on commit:**
1. Staged `.ts` and `.js` files are linted with ESLint (auto-fixed if possible)
2. Staged `.ts`, `.js`, `.json`, and `.md` files are formatted with Prettier
3. If linting fails, the commit is blocked
4. If linting succeeds, files are auto-formatted and staged

**Setup:**
```bash
# Install dependencies (runs automatically after npm install)
npm run prepare

# This creates .husky/ directory and sets up git hooks
```

### VS Code Integration

The project includes VS Code settings for seamless development:

**Features:**
- Format on save (using Prettier)
- Auto-fix ESLint issues on save
- Recommended extensions prompt on first open
- Proper TypeScript workspace configuration

**Recommended Extensions:**
- ESLint (`dbaeumer.vscode-eslint`)
- Prettier (`esbenp.prettier-vscode`)
- TypeScript (`ms-vscode.vscode-typescript-next`)
- Jest (`orta.vscode-jest`)

### Configuration Files

- **`.eslintrc.json`** - ESLint rules (strict TypeScript, code style)
- **`.prettierrc.json`** - Prettier formatting rules
- **`jest.config.js`** - Jest testing configuration (80% coverage threshold)
- **`.husky/pre-commit`** - Pre-commit hook script
- **`.vscode/settings.json`** - VS Code workspace settings
- **`.vscode/extensions.json`** - Recommended extensions

### Coding Standards

**Naming Conventions:**
- Classes: `PascalCase`
- Functions/Methods: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Variables: `camelCase`
- Files: `kebab-case.ts` or `kebab-case.js`

**TypeScript Rules:**
- No explicit `any` type (use `unknown` or proper types)
- Strict mode enabled
- Explicit function return types encouraged
- Prefer `const` over `let`, never use `var`

**Code Organization:**
- One class/interface per file
- Group related functionality in modules
- Use barrel exports (`index.ts`) for clean imports
- Keep functions small and focused (single responsibility)

**Error Handling:**
- Always use try-catch for async operations
- Provide meaningful error messages
- Log errors with context
- Never swallow errors silently

### Testing Strategy

**Unit Tests:**
- Test file naming: `*.test.ts` or `*.spec.ts`
- Place tests next to source files or in `tests/` directory
- Use descriptive test names: `should do X when Y`
- Aim for 80%+ code coverage

**Test Structure:**
```typescript
describe('ClassName or FunctionName', () => {
  it('should do X when Y', async () => {
    // Arrange
    const input = { ... };

    // Act
    const result = await functionUnderTest(input);

    // Assert
    expect(result).toEqual(expected);
  });
});
```

## Contributing

1. Follow coding standards above
2. Write tests for new features
3. Ensure all tests pass: `npm test`
4. Ensure code is linted: `npm run lint`
5. Format code: `npm run format`
6. Use conventional commit format: `<type>(<scope>): <subject>`
7. Pre-commit hooks will run automatically

## License

ISC

## Support

For issues, questions, or contributions, please refer to the project documentation in the `docs/` directory.
