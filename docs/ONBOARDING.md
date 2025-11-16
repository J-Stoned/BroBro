# BroBro Onboarding Guide

Welcome to **BroBro** - Your AI-powered GoHighLevel automation assistant with 275 specialized commands enriched with Josh Wash's proven business workflows.

## What is BroBro?

BroBro is a comprehensive command-line interface that provides:
- **275 specialized commands** for GoHighLevel automation
- **Josh Wash business architecture** - 4 proven workflows with validated success metrics
- **AI-powered semantic search** - Find commands using natural language
- **Interactive 7-step workflow execution** - From concept to deployment
- **Complete knowledge base** - GHL docs, tutorials, and best practices

## Quick Start (5 Minutes)

### Step 1: Verify Installation

```bash
cd "C:\Users\justi\BroBro"
python .claude/commands/cli/ghl-cli.py list
```

You should see all 275 commands organized by 16 categories.

### Step 2: Try Your First Command

Let's set up an appointment reminder automation:

```bash
python .claude/commands/cli/ghl-cli.py appointment-reminder "setup 24-hour reminder for pressure washing appointments"
```

**What happens**:
1. The system parses your request
2. Queries the knowledge base for best practices
3. Generates 3 workflow variations (recommended, simplified, advanced)
4. Shows deployment-ready JSON configuration
5. Offers to deploy via MCP integration

### Step 3: Search for Commands

Use semantic search to find what you need:

```bash
# Find appointment-related commands
python .claude/commands/cli/ghl-cli.py search "appointment reminders"

# Find SMS automation
python .claude/commands/cli/ghl-cli.py search "send text messages to customers"

# Find Josh Wash workflows
python .claude/commands/cli/ghl-cli.py search "josh wash booking flow"
```

### Step 4: Get Command Help

```bash
python .claude/commands/cli/ghl-cli.py help appointment-reminder
```

Shows:
- Command description
- Category and tags
- Josh Wash workflow details
- Proven pattern and success metrics
- Usage examples

### Step 5: Explore by Category

```bash
# See all commands
python .claude/commands/cli/ghl-cli.py list

# Get comprehensive help
python .claude/commands/cli/ghl-help.py overview

# Get started guide
python .claude/commands/cli/ghl-help.py start
```

---

## First 5 Commands to Try

### 1. Appointment Reminder (`appointment-reminder`)

**What it does**: Creates multichannel (SMS + Email) appointment reminder automation

**Josh Wash Workflow**: Appointment Reminder - Day Before
- **Success Metrics**: 85% show-up rate, 72% confirmation rate, 40% no-show reduction
- **Pattern**: trigger: booking → wait 1 day → multichannel (SMS + Email)

**Try it**:
```bash
python .claude/commands/cli/ghl-cli.py appointment-reminder "setup reminders for cleaning appointments"
```

**When to use**:
- Service-based businesses (plumbing, cleaning, HVAC)
- Appointment-heavy industries (medical, legal, consulting)
- Reducing no-shows and last-minute cancellations

---

### 2. Email Sequence (`email-sequence`)

**What it does**: Creates automated email nurture sequences with personalization

**Josh Wash Workflow**: Booking Confirmation Email
- **Success Metrics**: 78% open rate, 45% click-through rate
- **Pattern**: trigger: booking → immediate Email + hidden actions

**Try it**:
```bash
python .claude/commands/cli/ghl-cli.py email-sequence "create 5-email nurture sequence for pressure washing leads"
```

**When to use**:
- Lead nurturing campaigns
- Post-purchase onboarding
- Re-engagement sequences
- Educational drip campaigns

---

### 3. Lead Nurture (`lead-nurture`)

**What it does**: Designs multi-touch lead nurturing workflows with scoring

**Try it**:
```bash
python .claude/commands/cli/ghl-cli.py lead-nurture "nurture sequence for home service leads"
```

**When to use**:
- Converting cold leads to warm prospects
- Building trust over time
- Educating leads about your services
- Qualifying leads automatically

---

### 4. Form Builder (`form-builder`)

**What it does**: Creates high-converting forms with best practices

**Try it**:
```bash
python .claude/commands/cli/ghl-cli.py form-builder "quote request form for pressure washing"
```

**When to use**:
- Lead capture pages
- Quote request forms
- Survey and feedback collection
- Registration and signup forms

---

### 5. SMS Automation (`sms-automation`)

**What it does**: Sets up SMS automation workflows with compliance

**Try it**:
```bash
python .claude/commands/cli/ghl-cli.py sms-automation "appointment confirmations via SMS"
```

**When to use**:
- Time-sensitive communications
- Appointment reminders and confirmations
- Flash sales and promotions
- Two-way SMS conversations

---

## Common Workflows Explained

### Workflow 1: Complete Lead-to-Customer Journey

**Goal**: Automate entire customer acquisition process

**Commands to use**:
1. `form-builder` - Create lead capture form
2. `lead-nurture` - Setup nurture sequence
3. `appointment-reminder` - Automate booking reminders
4. `sales-follow-up` - Post-appointment follow-up
5. `feedback-collection` - Get testimonials

**Execution**:
```bash
# Step 1: Lead capture
python .claude/commands/cli/ghl-cli.py form-builder "pressure washing quote form"

# Step 2: Nurture leads
python .claude/commands/cli/ghl-cli.py lead-nurture "5-day educational sequence"

# Step 3: Booking automation
python .claude/commands/cli/ghl-cli.py appointment-reminder "24hr and 1hr reminders"

# Step 4: Follow-up
python .claude/commands/cli/ghl-cli.py sales-follow-up "post-service thank you + review request"

# Step 5: Collect feedback
python .claude/commands/cli/ghl-cli.py feedback-collection "automated review requests"
```

---

### Workflow 2: SaaS Mode Setup

**Goal**: Configure GoHighLevel for white-label SaaS

**Commands to use**:
1. `saas-mode` - SaaS configuration guide
2. `custom-domain` - Setup white-label domain
3. `subscription-management` - Configure billing
4. `client-onboarding` - Automate client setup

**Execution**:
```bash
python .claude/commands/cli/ghl-cli.py saas-mode "setup SaaS with Stripe integration"
python .claude/commands/cli/ghl-cli.py custom-domain "configure white-label domain"
python .claude/commands/cli/ghl-cli.py subscription-management "setup monthly billing plans"
python .claude/commands/cli/ghl-cli.py client-onboarding "automate new client welcome sequence"
```

---

### Workflow 3: Funnel Optimization

**Goal**: Build high-converting sales funnels

**Commands to use**:
1. `funnel-builder` - Create funnel structure
2. `landing-page-optimization` - Optimize for conversions
3. `a-b-testing` - Test variations
4. `analytics-setup` - Track performance

**Execution**:
```bash
python .claude/commands/cli/ghl-cli.py funnel-builder "3-page funnel for pressure washing"
python .claude/commands/cli/ghl-cli.py landing-page-optimization "improve landing page conversions"
python .claude/commands/cli/ghl-cli.py a-b-testing "test headline variations"
python .claude/commands/cli/ghl-cli.py analytics-setup "track funnel performance"
```

---

## Tips for Power Users

### 1. Use Semantic Search for Discovery

Instead of memorizing command names, describe what you want:

```bash
# Good: Natural language
python .claude/commands/cli/ghl-cli.py search "automate follow-up after customer books"

# Also good: Specific features
python .claude/commands/cli/ghl-cli.py search "85% show-up rate"

# Also good: By workflow
python .claude/commands/cli/ghl-cli.py search "josh wash booking confirmation"
```

### 2. Filter by Category

```bash
# Sales commands only
python .claude/commands/cli/ghl-help.py category sales

# All ecommerce commands
python .claude/commands/cli/ghl-help.py category ecommerce

# Lead generation commands
python .claude/commands/cli/ghl-help.py category lead
```

### 3. Combine Commands for Complex Workflows

Build multi-step automations by chaining commands:

```bash
# Step 1: Capture leads
python .claude/commands/cli/ghl-cli.py popup-form-builder "exit-intent popup"

# Step 2: Tag and segment
python .claude/commands/cli/ghl-cli.py tag-automation "tag based on form responses"

# Step 3: Route to pipeline
python .claude/commands/cli/ghl-cli.py pipeline-automation "move to nurture pipeline"

# Step 4: Start nurture
python .claude/commands/cli/ghl-cli.py email-sequence "7-day nurture sequence"
```

### 4. Leverage Josh Wash Workflows

All commands are enriched with 4 proven Josh Wash workflows:

**Appointment Reminder - Day Before** (85% show-up rate):
- Use for: Service appointments, consultations, demos
- Pattern: booking → wait 1 day → SMS + Email

**Booking Confirmation Email** (78% open rate):
- Use for: Immediate confirmations, receipts
- Pattern: booking → immediate Email + hidden actions

**Maintenance Club Purchase** (95% activation rate):
- Use for: Memberships, subscriptions, recurring services
- Pattern: purchase → SMS + Email → membership setup

**Popup Form Submitted** (34% quote conversion):
- Use for: Lead magnets, quote requests, consultation bookings
- Pattern: form submit → tag + pipeline → nurture

**Find commands by workflow**:
```bash
python .claude/commands/search/search_api.py --workflow "Appointment Reminder - Day Before"
```

### 5. Save Common Patterns

Create bash scripts for your most common operations:

```bash
# File: setup-service-business.sh
#!/bin/bash

echo "Setting up service business automation..."

python .claude/commands/cli/ghl-cli.py form-builder "service quote form"
python .claude/commands/cli/ghl-cli.py appointment-reminder "24hr + 1hr reminders"
python .claude/commands/cli/ghl-cli.py sms-automation "appointment confirmations"
python .claude/commands/cli/ghl-cli.py feedback-collection "post-service reviews"

echo "Automation setup complete!"
```

---

## Understanding the 7-Step Workflow

Every command follows this execution flow:

### Step 1: Parse User Input
- Analyzes your request
- Identifies goal and context
- Maps to Josh Wash pattern

### Step 2: Query Knowledge Base
- Searches `ghl-best-practices` collection
- Searches `ghl-tutorials` collection
- Returns top 3-5 relevant strategies

### Step 3: Generate Configuration Variations
- **Variation 1**: Josh Wash Proven Pattern (recommended)
- **Variation 2**: Simplified version (testing/low-volume)
- **Variation 3**: Advanced multi-touch (complex journeys)

### Step 4: Display Configuration Options
- Full workflow structure
- Deployment-ready JSON
- Real Josh Wash variables ({{business.name}}, {{contact.first_name}}, etc.)

### Step 5: Best Practices & Customization
- Key best practices from Josh Wash
- Common mistakes to avoid
- Customization opportunities

### Step 6: Offer MCP Deployment
- Option to deploy directly to GHL account
- Save JSON for manual deployment
- Test configuration first

### Step 7: Post-Deployment Guidance
- Success metrics to track
- Optimization suggestions
- Next steps

---

## Categories Overview

### 16 Command Categories

1. **ADS** (14 commands) - Ad campaigns, targeting, budget optimization
2. **ADVANCED** (11 commands) - API docs, branding, custom fields
3. **COMPLIANCE** (14 commands) - GDPR, CAN-SPAM, consent management
4. **CONTENT** (16 commands) - Content calendar, personalization, A/B testing
5. **CUSTOMER** (16 commands) - Onboarding, retention, churn prevention
6. **ECOMMERCE** (18 commands) - Payments, cart recovery, subscriptions
7. **INTEGRATION** (20 commands) - API integration, webhooks, data export
8. **LEAD** (64 commands) - Lead capture, nurture, scoring, conversion
9. **LEARNING** (8 commands) - Training, tutorials, best practices
10. **META** (9 commands) - System commands, command discovery, help
11. **REPORTING** (16 commands) - Analytics, attribution, ROI tracking
12. **SALES** (17 commands) - Sales automation, follow-up, pipeline
13. **STRATEGY** (10 commands) - Growth strategy, competitive analysis
14. **TEMPLATES** (12 commands) - Reusable templates for emails, forms, funnels
15. **TROUBLESHOOTING** (10 commands) - Common errors, debugging, support
16. **WORKFLOW** (20 commands) - Workflow automation, triggers, actions

---

## Next Steps

### Beginner Track
1. ✅ Complete this onboarding guide
2. Try the 5 starter commands listed above
3. Build your first complete workflow (Lead-to-Customer)
4. Read [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md) for all commands

### Intermediate Track
1. Explore all 16 categories
2. Learn Josh Wash workflows in depth
3. Build multi-step automations
4. Integrate with GHL API (Epic 3)

### Advanced Track
1. Customize command templates
2. Create your own workflow patterns
3. Build MCP tool integrations
4. Contribute to knowledge base

---

## Getting Help

### Built-in Help

```bash
# Overview of all commands
python .claude/commands/cli/ghl-help.py overview

# Getting started guide
python .claude/commands/cli/ghl-help.py start

# Category-specific help
python .claude/commands/cli/ghl-help.py category sales

# Command-specific help
python .claude/commands/cli/ghl-cli.py help appointment-reminder

# Fuzzy search for typos
python .claude/commands/cli/ghl-help.py suggest "apointment"
```

### Documentation

- **ONBOARDING.md** (this file) - Getting started guide
- **COMMAND_REFERENCE.md** - Complete command listing
- **.claude/commands/cli/README.md** - CLI documentation
- **.claude/commands/search/README.md** - Search system docs
- **CLI_COMPLETION_REPORT.md** - CLI tool details

### Search the Knowledge Base

```bash
# Semantic search
python .claude/commands/cli/ghl-cli.py search "your question"

# Direct ChromaDB search
python .claude/commands/search/search_api.py --search "your question"

# Filter by category
python .claude/commands/search/search_api.py --search "automation" --category sales
```

---

## Troubleshooting

### Command not found

If you see "Command not found", use fuzzy matching:

```bash
python .claude/commands/cli/ghl-help.py suggest "apointment"
```

This will suggest similar commands with similarity scores.

### Search not working

Ensure ChromaDB is indexed:

```bash
python .claude/commands/search/search_api.py --stats
```

If indexed count is 0, rebuild:

```bash
python .claude/commands/search/search_api.py --rebuild
```

### Slow performance

- First run downloads embedding model (79.3 MB) - one-time only
- Subsequent queries: <1 second
- If still slow, check ChromaDB logs

---

## Success Stories (Josh Wash Metrics)

### Appointment Reminder Workflow
- **85% show-up rate** (vs. 60% industry average)
- **40% reduction in no-shows**
- **72% confirmation rate** within 24 hours

### Booking Confirmation Email
- **78% open rate** (vs. 20% industry average)
- **45% click-through rate**
- **<2 hour average response time**

### Maintenance Club Purchase
- **95% activation rate**
- **89% member retention** after 12 months
- **34% upsell rate** to higher tiers

### Popup Form Submitted
- **34% quote conversion rate**
- **67% form completion rate**
- **56% follow-up engagement**

---

## Welcome to BroBro!

You now have access to 275 specialized automation commands powered by Josh Wash's proven business workflows. Start with the 5 starter commands, explore categories that match your business needs, and leverage semantic search to discover new capabilities.

**Your first command**:
```bash
python .claude/commands/cli/ghl-cli.py appointment-reminder "setup 24-hour reminder"
```

Happy automating! 🚀
