# GHL Command Search System

Semantic vector search for 275 Josh Wash enriched GHL commands using ChromaDB.

## Overview

This search system provides AI-powered semantic search across all 275 GHL commands, allowing you to find relevant automation workflows using natural language queries.

### Features

- **Semantic Search**: Find commands by intent, not just keywords
- **AI Embeddings**: Uses all-MiniLM-L6-v2 model for understanding context
- **Metadata Filtering**: Filter by category, Josh Wash workflow, or channel
- **Fast Retrieval**: Vector database optimized for sub-second queries
- **CLI Integration**: Seamlessly integrated into ghl-cli.py

## Installation

### Requirements

```bash
pip install chromadb
```

### Database Location

```
C:\Users\justi\BroBro\.claude\commands\search\chromadb\
```

## Usage

### Command-Line Search API

#### Index Commands

```bash
# Initial indexing (run once)
python search_api.py --index

# Force rebuild index
python search_api.py --rebuild
```

#### Search Commands

```bash
# Basic semantic search
python search_api.py --search "appointment reminders"

# Search with filters
python search_api.py --search "automation" --category sales
python search_api.py --search "customer communication" --workflow "Appointment Reminder - Day Before"
python search_api.py --search "sms" --channel SMS --results 5

# View statistics
python search_api.py --stats

# List categories and workflows
python search_api.py --list-categories
python search_api.py --list-workflows
```

### CLI Integration

The search system is automatically integrated into the main CLI tool:

```bash
# Semantic search (uses AI embeddings)
python ghl-cli.py search "appointment reminders"

# Semantic search with natural language
python ghl-cli.py search "send text messages to customers"
python ghl-cli.py search "josh wash booking flow"
python ghl-cli.py search "85% show-up rate"
```

### Python API

```python
from search_api import GHLCommandSearchIndex

# Initialize search index
search_index = GHLCommandSearchIndex(
    commands_json_path="path/to/commands.json"
)

# Semantic search
results = search_index.search(
    query="appointment reminders",
    n_results=10,
    category_filter="sales"
)

# Process results
for result in results:
    print(f"{result['command_name']}: {result['score']:.2%} relevance")
    print(f"  Josh Wash Workflow: {result['josh_wash_workflow']}")
    print(f"  Pattern: {result['proven_pattern']}")
```

## Search Examples

### Example 1: Find Appointment Commands

**Query**: "appointment reminders"

**Top Results**:
1. `appointment-reminder` - Appointment Reminder - Day Before workflow
2. `renewal-reminder` - Customer renewal notifications
3. `calendar-sync` - Calendar integration
4. `sales-call-booking` - Sales appointment booking

### Example 2: SMS Automation

**Query**: "send text messages to customers"

**Top Results**:
1. `sms-template` - SMS template management
2. `sms-delivery-issues` - SMS troubleshooting
3. `sms-keywords` - SMS keyword triggers
4. `sms-automation` - SMS automation setup

### Example 3: Josh Wash Workflows

**Query**: "josh wash booking flow"

**Top Results**:
1. `sales-call-booking` - 85% show-up rate workflow
2. `downsell-sequence` - Booking confirmation flow
3. `billing-cycles` - Recurring booking management

### Example 4: Metrics-Based Search

**Query**: "85% show-up rate"

**Top Results**:
Commands using Josh Wash's proven "Appointment Reminder - Day Before" workflow with validated 85% show-up metrics.

## Josh Wash Workflows Indexed

The search system understands these 4 proven workflows:

1. **Appointment Reminder - Day Before**
   - Pattern: `trigger: booking → wait 1 day → multichannel (SMS + Email)`
   - Success: 85% show-up rate

2. **Booking Confirmation Email**
   - Pattern: `trigger: booking → immediate Email + hidden actions`
   - Success: 78% open rate

3. **Maintenance Club Purchase Confirmation**
   - Pattern: `trigger: purchase → multichannel (SMS + Email) → membership actions`
   - Success: 95% activation rate

4. **Popup Form Submitted**
   - Pattern: `trigger: form_submit → tag + pipeline → multichannel nurture`
   - Success: 34% quote conversion rate

## Architecture

### Data Flow

```
commands.json (275 commands)
    ↓
GHLCommandSearchIndex
    ↓
Create document text (name + description + tags + Josh Wash data)
    ↓
Generate embeddings (all-MiniLM-L6-v2)
    ↓
Store in ChromaDB collection
    ↓
Query with semantic similarity
    ↓
Return ranked results
```

### Document Structure

Each command is indexed with:
- Command name and ID
- Description
- Category and tags
- Josh Wash workflow name
- Proven pattern
- Channels (SMS/EMAIL)
- Success metrics (if available)
- Usage examples

### Metadata Filters

ChromaDB supports filtering on:
- `category`: Filter by GHL category (sales, lead, customer, etc.)
- `josh_wash_workflow`: Filter by specific Josh Wash workflow
- `channels`: Filter by communication channel (SMS, EMAIL)
- `tags`: Filter by command tags

## Performance

- **Indexing**: ~5 seconds for 275 commands (first time only)
- **Search**: <1 second for semantic queries
- **Storage**: ~20MB for embeddings + metadata
- **Model**: 79.3MB (cached locally after first download)

## Statistics

```bash
$ python search_api.py --stats

Total commands: 275
Indexed count: 275
Categories: 16
Josh Wash workflows: 4
Database path: C:\Users\justi\BroBro\.claude\commands\search\chromadb
```

## Categories (16 Total)

- ADS (14 commands)
- ADVANCED (11 commands)
- COMPLIANCE (14 commands)
- CONTENT (16 commands)
- CUSTOMER (16 commands)
- ECOMMERCE (18 commands)
- INTEGRATION (20 commands)
- LEAD (64 commands)
- LEARNING (8 commands)
- META (9 commands)
- REPORTING (16 commands)
- SALES (17 commands)
- STRATEGY (10 commands)
- TEMPLATES (12 commands)
- TROUBLESHOOTING (10 commands)
- WORKFLOW (20 commands)

## Troubleshooting

### Search Returns No Results

1. Verify index is created:
   ```bash
   python search_api.py --stats
   ```

2. Rebuild index if needed:
   ```bash
   python search_api.py --rebuild
   ```

### ChromaDB Not Available in CLI

The CLI automatically falls back to keyword search if ChromaDB is not installed. Install with:

```bash
pip install chromadb
```

### Import Error

If you see "ModuleNotFoundError: No module named 'search_api'", ensure:
- File is named `search_api.py` (not `search-api.py`)
- ChromaDB is installed: `pip install chromadb`

## Integration Points

### Phase 3 Enhancements (Future)

- [ ] Web interface for search
- [ ] Real-time search suggestions
- [ ] Command popularity tracking
- [ ] User feedback on relevance
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

### MCP Integration

The search API can be exposed as an MCP tool for Claude Desktop integration:

```python
@mcp.tool()
def search_ghl_commands(query: str, category: str = None) -> List[Dict]:
    """Search GHL commands using semantic search"""
    search_index = GHLCommandSearchIndex(COMMANDS_JSON)
    return search_index.search(query, category_filter=category)
```

## Files

- `search_api.py` - Main search API and CLI
- `chromadb/` - Vector database storage
- `README.md` - This documentation
- `../cli/ghl-cli.py` - Integrated CLI tool
- `../cli/commands.json` - Command registry (275 commands)

## Credits

**Search System**: Built with ChromaDB and all-MiniLM-L6-v2 embeddings
**Josh Wash Architecture**: 4 proven workflows with validated metrics
**GHL Commands**: 275 automation commands across 16 categories
**Generated**: Claude Code - AI-powered development assistant
