# GHL CLI Tool - Josh Wash Automation System

Command-line interface for all 275 enriched GHL commands with Josh Wash business architecture.

## Installation

No installation required! The CLI tool is ready to use.

**Location:**
```
C:\Users\justi\BroBro\.claude\commands\cli\
```

## Quick Start

### Windows

```bash
# From project root
python .claude/commands/cli/ghl-cli.py list

# Or use the batch launcher
.claude/commands/cli/ghl.bat list
```

### All Platforms

```bash
python ghl-cli.py [command] [user-input]
```

## Usage

### List All Commands

```bash
python ghl-cli.py list
```

Shows all 275 commands organized by category:
- ADS (14 commands)
- COMPLIANCE (14 commands)
- CUSTOMER (16 commands)
- ECOMMERCE (18 commands)
- LEAD (64 commands)
- SALES (17 commands)
- WORKFLOW (20 commands)
- And 10 more categories...

### Search Commands

```bash
python ghl-cli.py search appointment
python ghl-cli.py search email
python ghl-cli.py search "lead scoring"
```

### Get Command Help

```bash
python ghl-cli.py help appointment-reminder
python ghl-cli.py help email-sequence
```

Shows:
- Description
- Category and tags
- Josh Wash workflow pattern
- Success metrics
- Usage examples

### Execute a Command

```bash
python ghl-cli.py appointment-reminder "book a pressure washing appointment tomorrow"
python ghl-cli.py email-sequence "setup nurture sequence for new leads"
python ghl-cli.py lead-scoring "create scoring rules for hot leads"
```

## Command Execution Flow

When you execute a command, it follows a 7-step workflow:

### Step 1: Parse User Input
- Extracts goal from your request
- Identifies context and patterns
- Maps to Josh Wash workflow

### Step 2: Query Knowledge Base
- Searches `ghl-best-practices` collection
- Searches `ghl-tutorials` collection
- Returns top 3-5 relevant results

### Step 3: Generate Configuration Variations
- **Variation 1:** Josh Wash Proven Pattern (Recommended)
- **Variation 2:** Simplified Version (single-channel)
- **Variation 3:** Advanced Multi-Touch (complex logic)

### Step 4: Display Configuration Options
- Shows deployment-ready JSON
- Lists Josh Wash variables
- Provides real-world examples

### Step 5: Best Practices & Customization
- Key best practices from Josh Wash
- Common mistakes to avoid
- Customization points

### Step 6: Offer MCP Deployment
- Interactive deployment options
- Customization wizard
- JSON export for manual deployment

### Step 7: Post-Deployment Guidance
- Success tracking checklist
- KPI monitoring
- Benchmarks from Josh Wash data

## Command Categories

| Category | Count | Examples |
|----------|-------|----------|
| **LEAD** | 64 | email-sequence, lead-scoring, nurture-drip |
| **WORKFLOW** | 20 | workflow-trigger, conditional-routing, api-trigger |
| **INTEGRATION** | 20 | zapier-integration, salesforce-integration |
| **ECOMMERCE** | 18 | cart-recovery, checkout-builder, subscription-management |
| **SALES** | 17 | appointment-reminder, sales-workflow, proposal-builder |
| **CUSTOMER** | 16 | client-onboarding, churn-prevention, customer-health-score |
| **CONTENT** | 16 | blog-automation, content-calendar, video-marketing |
| **REPORTING** | 16 | analytics-setup, funnel-analysis, revenue-tracking |
| **ADS** | 14 | facebook-ads, google-ads, ad-targeting |
| **COMPLIANCE** | 14 | gdpr-compliance, ccpa-compliance, consent-management |
| **TEMPLATES** | 12 | template-library, template-create, template-customize |
| **ADVANCED** | 11 | custom-fields, api-documentation, webhook-documentation |
| **STRATEGY** | 10 | growth-strategy, automation-strategy, competitive-analysis |
| **TROUBLESHOOTING** | 10 | troubleshoot, common-errors, integration-troubleshoot |
| **META** | 9 | command-finder, help, search |
| **LEARNING** | 8 | getting-started, tutorial, course-builder |

**Total: 275 commands**

## Josh Wash Workflows Integrated

All commands are enriched with 4 proven Josh Wash workflows:

### 1. Appointment Reminder - Day Before
- **Pattern:** `trigger: booking → wait 1 day → multichannel (SMS + Email)`
- **Success Rate:** 85% show-up rate
- **Channels:** SMS + Email
- **Metrics:**
  - Show-up rate: 85%
  - Confirmation rate: 72%
  - No-show reduction: 40%

### 2. Booking Confirmation Email
- **Pattern:** `trigger: booking → immediate Email + hidden actions`
- **Success Rate:** 78% open rate
- **Channels:** Email
- **Metrics:**
  - Open rate: 78%
  - Confirmation click: 65%
  - Booking completion: 88%

### 3. Maintenance Club Purchase Confirmation
- **Pattern:** `trigger: purchase → multichannel (SMS + Email) → membership actions`
- **Success Rate:** 95% activation rate
- **Channels:** SMS + Email
- **Metrics:**
  - Membership activation: 95%
  - First booking rate: 68%
  - Retention 30-day: 91%

### 4. Popup Form Submitted
- **Pattern:** `trigger: form → form automation + nested workflow actions`
- **Success Rate:** 34% quote conversion
- **Channels:** Email + SMS
- **Metrics:**
  - Lead capture: 100%
  - Follow-up sent: 98%
  - Quote conversion: 34%

## Josh Wash Variables

All commands include these real business variables:

**Business Variables:**
- `{{business.name}}` → "Josh Wash Pressure Washing"
- `{{business.owner}}` → "Josh"
- `{{business.phone}}` → Your phone number
- Email domain: `@joshwash.com`

**Appointment Variables:**
- `{{appointment.start_time}}` - Appointment start time
- `{{appointment.start_date}}` - Appointment date
- `{{appointment.title}}` - Service name
- `{{appointment.location}}` - Service location
- `{{appointment.service}}` - Service type

**Contact Variables:**
- `{{contact.first_name}}` - Customer first name
- `{{contact.last_name}}` - Customer last name
- `{{contact.email}}` - Email address
- `{{contact.phone}}` - Phone number
- `{{contact.address}}` - Property address

**Custom Fields:**
- `membership_status` - Maintenance Club status
- `membership_level` - Club membership tier
- `last_service_date` - Last service completed
- `property_type` - Residential/Commercial

## Example Commands

### Appointment Automation
```bash
python ghl-cli.py appointment-reminder "set up reminder workflow"
python ghl-cli.py booking-confirmation "configure instant confirmation"
python ghl-cli.py appointment-no-show "handle no-shows"
```

### Email Marketing
```bash
python ghl-cli.py email-sequence "create welcome sequence"
python ghl-cli.py email-personalization "add dynamic content"
python ghl-cli.py email-deliverability "improve inbox placement"
```

### Lead Management
```bash
python ghl-cli.py lead-scoring "build scoring model"
python ghl-cli.py lead-routing "route by territory"
python ghl-cli.py lead-nurture "setup drip campaign"
```

### Sales Automation
```bash
python ghl-cli.py sales-workflow "automate follow-ups"
python ghl-cli.py proposal-builder "generate proposals"
python ghl-cli.py sales-pipeline "track opportunities"
```

### Forms & Funnels
```bash
python ghl-cli.py form-validation "add field validation"
python ghl-cli.py funnel-analysis "analyze conversion rates"
python ghl-cli.py landing-page-design "optimize for conversion"
```

## Command Registry

All command metadata is stored in:
```
C:\Users\justi\BroBro\.claude\commands\cli\commands.json
```

Contains:
- Command ID, name, description
- Category and tags
- Josh Wash workflow mapping
- Success metrics
- File paths

## Files

- **ghl-cli.py** - Main CLI application (Python 3.6+)
- **ghl.bat** - Windows batch launcher
- **commands.json** - Command registry (275 commands)
- **README.md** - This file

## Requirements

- Python 3.6+
- No external dependencies required!

## Troubleshooting

### Command not found

```bash
python ghl-cli.py list
```

Check available commands and search for similar names.

### Unicode encoding errors (Windows)

The CLI automatically handles UTF-8 encoding on Windows. If you still see errors, run:

```bash
chcp 65001
python ghl-cli.py [command] [input]
```

### Permission errors

Ensure you have read access to:
```
C:\Users\justi\BroBro\.claude\commands\ghl-whiz-josh-wash\
```

## Advanced Usage

### Save Command Registry

```bash
python ghl-cli.py --save-registry
```

Regenerates `commands.json` from all 275 .md files.

### Filter by Category

```bash
python ghl-cli.py list --category lead
python ghl-cli.py list --category sales
```

### Batch Processing

Create a script to execute multiple commands:

```bash
# execute_workflows.bat
python ghl-cli.py appointment-reminder "book apt" > output1.txt
python ghl-cli.py email-sequence "nurture" > output2.txt
python ghl-cli.py lead-scoring "score" > output3.txt
```

## Development

### Add New Commands

1. Create `.md` file in `ghl-whiz-josh-wash/`
2. Follow frontmatter format:
```yaml
---
description: "Command description"
examples:
  - "/command-name example 1"
  - "/command-name example 2"
category: automation
tags: ["tag1", "tag2"]
josh_wash_workflow: "Workflow Name"
proven_pattern: "trigger → action pattern"
---
```

3. Regenerate registry:
```bash
python ghl-cli.py --save-registry
```

### Customize Workflows

Edit command `.md` files to update:
- JSON configurations
- Success metrics
- Best practices
- Examples

## Support

For issues or questions:
1. Check command help: `python ghl-cli.py help [command-name]`
2. Search commands: `python ghl-cli.py search [keyword]`
3. Review full documentation: `.claude/commands/ghl-whiz-josh-wash/[command].md`

## License

Internal tool for Josh Wash Pressure Washing automation system.

---

**GHL CLI Tool v1.0**
Built with Josh Wash BMAD-METHOD
275 Production-Ready Commands
Ready for Phase 3: Search Indexing
