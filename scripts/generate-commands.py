#!/usr/bin/env python3
"""
GHL WHIZ Command Generator
Generates 221+ slash commands from specifications CSV
"""

import csv
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
CSV_PATH = "data/commands-specification.csv"
OUTPUT_DIR = ".claude/commands/ghl-whiz"
TEMPLATE_DIR = "."
STATUS_LOG = "scripts/generation-status.log"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Command template
COMMAND_TEMPLATE = """---
command_id: {command_id}
aliases: []
category: {category}
tags: {tags}
use_cases: ["{use_case}"]
complexity: beginner
estimated_time: 30min
search_keywords: []
similar_commands: {similar_commands}
---

# {title}

## What It Does
{purpose}

## When To Use This
- {use_case}
- For {category} automation
- When you need to {purpose_lower}

## How It Works

### Step 1: Parse User Input
Extract parameters from your request

### Step 2: Query Knowledge Base
Search `ghl-best-practices` for: {kb_searches}
Search `ghl-tutorials` for: implementation guides

### Step 3: Generate Output
Create production-ready configuration

### Step 4: Offer Deployment
Provide deployment options via MCP tools

## Real-World Examples
- **Example 1:** {use_case}
- **Example 2:** Advanced {use_case} setup
- **Example 3:** {category} best practices application

## Output Format
Depends on command type: JSON workflow, guide, checklist, or analysis

## Common Mistakes
- Mistake 1: Not customizing for your specific use case
- Mistake 2: Skipping the deployment validation step
- Mistake 3: Not reviewing the generated output before deploying

## Next Steps
1. Review the generated output
2. Customize if needed
3. Deploy to your GHL account
4. Monitor and iterate

## Pro Tips
- Test with a sample contact first
- Review best practices before deploying
- Ask for help with `/ghl-search` if unsure
- Check `/ghl-best-practices` for industry-specific guidance

## Related Commands
See similar_commands above for related workflows
"""

def format_title(command_id):
    """Convert ghl-command to Title Case"""
    return " ".join(word.capitalize() for word in command_id.replace("ghl-", "").split("-"))

def parse_similar_commands(similar_str):
    """Parse similar commands string into list"""
    if not similar_str or similar_str == "":
        return []
    return [f'"{cmd.strip()}"' for cmd in similar_str.split("|")]

def generate_command_file(row):
    """Generate a single command markdown file"""
    try:
        command_id = row['command_id']
        
        # Skip if already done
        if row['status'] == 'done':
            return None, f"SKIP: {command_id} (already done)"
        
        # Extract and format data
        title = format_title(command_id)
        category = row['category']
        purpose = row['purpose']
        purpose_lower = purpose.lower()
        use_case = row['real_world_example']
        kb_searches = row['kb_search_queries']
        similar_cmds = parse_similar_commands(row['similar_commands'])
        similar_cmds_str = "[" + ", ".join(similar_cmds) + "]"
        
        # Generate tags from category
        tags = f'["{category}", "automation"]'
        
        # Build content
        content = COMMAND_TEMPLATE.format(
            command_id=command_id,
            category=category,
            tags=tags,
            use_case=use_case,
            title=title,
            purpose=purpose,
            purpose_lower=purpose_lower,
            kb_searches=kb_searches,
            similar_commands=similar_cmds_str
        )
        
        # Write file
        output_path = os.path.join(OUTPUT_DIR, f"{command_id}.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path, f"DONE: {command_id}"
    
    except Exception as e:
        return None, f"ERROR: {row['command_id']} - {str(e)}"

def main():
    """Main generation function"""
    print("=" * 70)
    print("🚀 GHL WHIZ COMMAND GENERATOR")
    print("=" * 70)
    print(f"\n📁 Reading specifications from: {CSV_PATH}")
    print(f"📝 Output directory: {OUTPUT_DIR}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track stats
    generated = 0
    skipped = 0
    errors = 0
    
    results = []
    
    # Read CSV and generate
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                output_path, status = generate_command_file(row)
                results.append(status)
                
                if output_path:
                    generated += 1
                    print(f"✅ {idx:3d}. {status}")
                elif "SKIP" in status:
                    skipped += 1
                    print(f"⏭️  {idx:3d}. {status}")
                else:
                    errors += 1
                    print(f"❌ {idx:3d}. {status}")
    
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find {CSV_PATH}")
        print("   Make sure you're running this from the GHL WHIZ root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 GENERATION SUMMARY")
    print("=" * 70)
    print(f"✅ Generated: {generated} new commands")
    print(f"⏭️  Skipped:   {skipped} (already done)")
    print(f"❌ Errors:    {errors}")
    print(f"📦 Total:     {generated + skipped + errors} processed")
    print(f"\n📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Write log
    os.makedirs(os.path.dirname(STATUS_LOG), exist_ok=True)
    with open(STATUS_LOG, 'w', encoding='utf-8') as f:
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Generated: {generated} | Skipped: {skipped} | Errors: {errors}\n\n")
        f.write("\n".join(results))
    
    print(f"📝 Status log: {STATUS_LOG}\n")
    
    if errors == 0:
        print("🎉 GENERATION SUCCESSFUL!")
        return 0
    else:
        print("⚠️  GENERATION COMPLETE WITH ERRORS")
        return 1

if __name__ == "__main__":
    sys.exit(main())
