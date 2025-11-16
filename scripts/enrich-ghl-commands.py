#!/usr/bin/env python3
"""
GHL Command Enrichment System
Enriches all GHL commands to match the master template standard from ghl-workflow.md
"""

import os
import re
from pathlib import Path
from datetime import datetime
import concurrent.futures

# Configuration
MASTER_TEMPLATE = r"C:\Users\justi\BroBro\.claude\commands\ghl-workflow.md"
COMMANDS_DIR = r"C:\Users\justi\BroBro\.claude\commands\ghl-whiz"
OUTPUT_LOG = r"C:\Users\justi\BroBro\scripts\enrichment-log.txt"
MAX_WORKERS = 10  # Parallel processing threads

# Track statistics
stats = {
    "processed": 0,
    "enriched": 0,
    "skipped": 0,
    "errors": 0,
    "start_time": None,
    "end_time": None
}

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown file"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        body = match.group(2)
        return frontmatter, body
    return None, content

def extract_command_info(filepath):
    """Extract key information from command file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        # Extract command ID from filename
        command_id = Path(filepath).stem

        # Extract title from body
        title_match = re.search(r'^#\s+(.+?)$', body, re.MULTILINE)
        title = title_match.group(1) if title_match else command_id.replace('-', ' ').title()

        # Extract category and purpose from frontmatter
        category = "automation"
        purpose = "GHL automation"

        if frontmatter:
            category_match = re.search(r'category:\s*(.+?)$', frontmatter, re.MULTILINE)
            if category_match:
                category = category_match.group(1).strip()

        # Extract purpose from "What It Does" section
        purpose_match = re.search(r'## What It Does\n(.+?)(?:\n##|\Z)', body, re.DOTALL)
        if purpose_match:
            purpose = purpose_match.group(1).strip()

        return {
            "command_id": command_id,
            "title": title,
            "category": category,
            "purpose": purpose,
            "frontmatter": frontmatter,
            "body": body,
            "original_content": content
        }
    except Exception as e:
        return {"error": str(e)}

def generate_enriched_command(info):
    """Generate enriched command following ghl-workflow.md template structure"""

    command_id = info["command_id"]
    title = info["title"]
    category = info["category"]
    purpose = info["purpose"]

    # Build enriched frontmatter
    enriched_frontmatter = f"""---
description: "{purpose}"
examples:
  - "/{command_id} [primary use case]"
  - "/{command_id} [secondary use case]"
  - "/{command_id} [advanced use case]"
category: {category}
tags: ["{category}", "automation", "ghl"]
---"""

    # Build enriched body following master template structure
    enriched_body = f"""
# {title}

You are an expert GoHighLevel specialist for {category} automation. Your role is to help users implement {command_id.replace('ghl-', '').replace('-', ' ')} by leveraging the knowledge base and offering deployment via MCP tools.

## Command Flow

### Step 1: Parse User Input

Extract the user's goal from their input after `/{command_id}`.

If the goal is unclear, ask: "What would you like to accomplish with {command_id.replace('ghl-', '').replace('-', ' ')}?"

### Step 2: Query Knowledge Base

**Query 1 - Best Practices:**
Search the `ghl-best-practices` ChromaDB collection for proven strategies.

Query format: `{command_id.replace('ghl-', '').replace('-', ' ')} best practices automation`

Return top 3-5 results and extract:
- Proven implementation patterns
- Timing and configuration recommendations
- Optimization tactics
- Common mistakes to avoid

**Query 2 - Tutorials:**
Search the `ghl-tutorials` ChromaDB collection for implementation guides.

Query format: `{command_id.replace('ghl-', '').replace('-', ' ')} setup tutorial`

Return top 3 results and extract:
- Step-by-step guides
- Visual examples
- Tool-specific configuration

### Step 3: Generate Configuration Options

Based on KB results, generate 2-3 configuration variations.

**Option 1: Simple & Fast**
- Quick setup for immediate results
- Minimal configuration
- Best for: First-time users, testing

**Option 2: Comprehensive & Robust**
- Full-featured implementation
- Advanced configuration options
- Best for: Established businesses

**Option 3: Advanced & Intelligent** (if applicable)
- Complex integrations and logic
- Enterprise-level features
- Best for: Power users

### Step 4: Display Configuration Options

Present each option with:
- Based on: [KB Citation]
- Structure: Step-by-step flow
- Expected Results: Metrics and benchmarks
- JSON/Configuration: Real, deployable code

Example format:
```
## Configuration Option 1: Simple Setup

**Based on:** GHL Best Practices - {category.title()} (KB Citation)

**Structure:**
[Step-by-step implementation flow]

**Expected Results:**
- [Metric 1]: [Benchmark]
- [Metric 2]: [Benchmark]

**Configuration:**
```json
{{
  "name": "{title} - Simple",
  "type": "{command_id.replace('ghl-', '')}",
  "config": {{
    // Real configuration here
  }}
}}
```
```

### Step 5: Provide Best Practices & Customization

**Key Best Practices (from KB):**
1. [Best practice 1 from ghl-best-practices]
2. [Best practice 2 from ghl-best-practices]
3. [Best practice 3 from ghl-best-practices]

**Customization Points:**
- [Customization option 1]
- [Customization option 2]
- [Customization option 3]

**Common Mistakes to Avoid:**
- ❌ [Common mistake 1]
- ❌ [Common mistake 2]
- ❌ [Common mistake 3]

### Step 6: Offer MCP Deployment

After presenting options, ask:

```
Would you like to deploy this configuration to your GHL account now?

Options:
1. Deploy Option 1 (Simple)
2. Deploy Option 2 (Comprehensive)
3. Deploy Option 3 (Advanced)
4. Customize first, then deploy
5. Save configuration for manual deployment

Enter your choice (1-5):
```

**If user chooses 1, 2, or 3:**

1. Confirm deployment
2. Execute MCP tool with configuration
3. Show deployment result with next steps

**If user chooses 4 (Customize):**

Ask customization questions and regenerate configuration.

**If user chooses 5 (Save):**

Provide full configuration for manual deployment.

### Step 7: Post-Deployment Guidance

**Testing Checklist:**
- [ ] Verify configuration is active
- [ ] Test with sample data
- [ ] Check logs for errors
- [ ] Confirm expected behavior

**Optimization Tips:**
- Monitor performance metrics
- A/B test variations
- Adjust based on results
- Iterate and improve

## Error Handling

**If KB search returns no results:**
Generate configuration based on standard automation principles and ask if user wants generic template or related alternatives.

**If user input is too vague:**
Request more details about trigger, outcome, and target audience.

**If deployment fails:**
Provide troubleshooting steps and alternative deployment options.

## Advanced Features

Include examples of:
- Conditional logic
- Dynamic content
- Multi-step workflows
- Integration patterns

## Success Metrics

Track these KPIs after deployment:
- [Metric 1]: [Benchmark range]
- [Metric 2]: [Benchmark range]
- [Metric 3]: [Benchmark range]

## Real-World Examples

**Example 1: [Use Case 1]**
[Detailed implementation example]

**Example 2: [Use Case 2]**
[Detailed implementation example]

**Example 3: [Use Case 3]**
[Detailed implementation example]

---

**Remember:** Always cite KB sources, generate real deployable configurations (not templates), and offer MCP deployment. Make implementations actionable, not just concepts.
"""

    return enriched_frontmatter + enriched_body

def enrich_command_file(filepath):
    """Enrich a single command file"""
    try:
        # Extract info
        info = extract_command_info(filepath)

        if "error" in info:
            return {
                "filepath": filepath,
                "status": "error",
                "message": info["error"]
            }

        # Check if already enriched (has Step 1, Step 2 structure)
        if "### Step 1:" in info["body"] and "### Step 2:" in info["body"] and len(info["body"]) > 2000:
            return {
                "filepath": filepath,
                "status": "skipped",
                "message": "Already enriched (has 7-step structure)"
            }

        # Generate enriched content
        enriched_content = generate_enriched_command(info)

        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(enriched_content)

        return {
            "filepath": filepath,
            "status": "enriched",
            "message": f"Enriched successfully ({len(enriched_content)} chars)"
        }

    except Exception as e:
        return {
            "filepath": filepath,
            "status": "error",
            "message": str(e)
        }

def process_commands_parallel(commands_dir, max_workers=10):
    """Process all command files in parallel"""

    # Get all .md files
    command_files = list(Path(commands_dir).glob("*.md"))

    print(f"Found {len(command_files)} command files to process")
    print(f"Using {max_workers} parallel workers\n")

    results = []

    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(enrich_command_file, str(f)): f for f in command_files}

        for idx, future in enumerate(concurrent.futures.as_completed(future_to_file), 1):
            result = future.result()
            results.append(result)

            # Update stats
            stats["processed"] += 1
            if result["status"] == "enriched":
                stats["enriched"] += 1
                print(f"✅ {idx:3d}/{len(command_files)} - ENRICHED: {Path(result['filepath']).name}")
            elif result["status"] == "skipped":
                stats["skipped"] += 1
                print(f"⏭️  {idx:3d}/{len(command_files)} - SKIPPED: {Path(result['filepath']).name}")
            else:
                stats["errors"] += 1
                print(f"❌ {idx:3d}/{len(command_files)} - ERROR: {Path(result['filepath']).name}")

    return results

def generate_report(results):
    """Generate enrichment completion report"""

    duration = (stats["end_time"] - stats["start_time"]).total_seconds()

    report = f"""
{'='*70}
GHL COMMAND ENRICHMENT REPORT
{'='*70}

EXECUTION SUMMARY:
- Start Time: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
- End Time: {stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
- Duration: {duration:.2f} seconds
- Processing Speed: {stats['processed'] / duration:.2f} files/second

RESULTS:
✅ Enriched: {stats['enriched']} commands
⏭️  Skipped: {stats['skipped']} commands (already enriched)
❌ Errors: {stats['errors']} commands
📦 Total Processed: {stats['processed']} commands

SUCCESS RATE: {(stats['enriched'] / stats['processed'] * 100):.1f}%

ENRICHMENT DETAILS:
"""

    for result in results:
        filename = Path(result['filepath']).name
        status = result['status'].upper()
        message = result['message']
        report += f"  [{status}] {filename}: {message}\n"

    report += f"\n{'='*70}\n"

    return report

def main():
    """Main enrichment execution"""

    print("="*70)
    print("🚀 GHL COMMAND ENRICHMENT SYSTEM")
    print("="*70)
    print(f"\n📁 Commands Directory: {COMMANDS_DIR}")
    print(f"📝 Master Template: {MASTER_TEMPLATE}")
    print(f"⚙️  Max Workers: {MAX_WORKERS}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    stats["start_time"] = datetime.now()

    # Process all commands in parallel
    results = process_commands_parallel(COMMANDS_DIR, MAX_WORKERS)

    stats["end_time"] = datetime.now()

    # Generate and display report
    print("\n" + "="*70)
    report = generate_report(results)
    print(report)

    # Save report to file
    os.makedirs(os.path.dirname(OUTPUT_LOG), exist_ok=True)
    with open(OUTPUT_LOG, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"📝 Full report saved to: {OUTPUT_LOG}\n")

    if stats["errors"] == 0:
        print("🎉 ENRICHMENT COMPLETE - ALL FILES PROCESSED SUCCESSFULLY!")
        return 0
    else:
        print(f"⚠️  ENRICHMENT COMPLETE WITH {stats['errors']} ERRORS")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
