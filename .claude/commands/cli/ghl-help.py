#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GHL Help System Module
Provides comprehensive help, fuzzy matching, and command suggestions
"""

import os
import sys
import io
import json
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz, process

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class GHLHelpSystem:
    """Comprehensive help system with fuzzy matching and suggestions"""

    def __init__(self, commands: Dict):
        self.commands = commands
        self.command_names = list(commands.keys())

    def show_help_overview(self):
        """Display comprehensive help overview with all 275 commands by category"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}BroBro - Complete Command Reference{Colors.ENDC}")
        print(f"{Colors.CYAN}275 GoHighLevel Automation Commands with Josh Wash Business Architecture{Colors.ENDC}\n")

        # Group by category
        categories = {}
        for name, cmd in self.commands.items():
            cat = cmd.get('category', 'uncategorized')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd)

        # Display by category
        print(f"{Colors.BOLD}Commands by Category:{Colors.ENDC}\n")

        for category in sorted(categories.keys()):
            cmds = categories[category]
            print(f"{Colors.CYAN}=== {category.upper()} ({len(cmds)} commands) ==={Colors.ENDC}")

            # Show first 10 commands in each category
            for cmd in sorted(cmds, key=lambda x: x['name'])[:10]:
                name = cmd['name']
                desc = cmd.get('description', '')[:60]
                workflow = cmd.get('josh_wash_workflow', '')

                print(f"  {Colors.GREEN}•{Colors.ENDC} {name:<35} {desc}")

                if workflow:
                    print(f"    {Colors.YELLOW}>{Colors.ENDC} {workflow}")

            if len(cmds) > 10:
                print(f"    {Colors.YELLOW}... and {len(cmds) - 10} more{Colors.ENDC}")

            print()

        # Usage examples
        print(f"{Colors.BOLD}Quick Start Examples:{Colors.ENDC}\n")
        print(f"  {Colors.GREEN}List all commands:{Colors.ENDC}")
        print(f"    python ghl-cli.py list\n")

        print(f"  {Colors.GREEN}Search commands:{Colors.ENDC}")
        print(f"    python ghl-cli.py search \"appointment reminders\"")
        print(f"    python ghl-cli.py search \"send sms to customers\"\n")

        print(f"  {Colors.GREEN}Get help for specific command:{Colors.ENDC}")
        print(f"    python ghl-cli.py help appointment-reminder\n")

        print(f"  {Colors.GREEN}Execute a command:{Colors.ENDC}")
        print(f"    python ghl-cli.py appointment-reminder \"setup 24-hour reminder\"\n")

        # Josh Wash Workflows
        print(f"{Colors.BOLD}Josh Wash Proven Workflows:{Colors.ENDC}\n")

        workflows = {}
        for cmd in self.commands.values():
            workflow = cmd.get('josh_wash_workflow', '')
            if workflow:
                if workflow not in workflows:
                    workflows[workflow] = []
                workflows[workflow].append(cmd['name'])

        for workflow, cmds in workflows.items():
            print(f"  {Colors.CYAN}•{Colors.ENDC} {Colors.BOLD}{workflow}{Colors.ENDC} ({len(cmds)} commands)")

        print(f"\n{Colors.CYAN}For detailed documentation, see:{Colors.ENDC}")
        print(f"  • docs/ONBOARDING.md - Getting started guide")
        print(f"  • docs/COMMAND_REFERENCE.md - Complete command reference")
        print(f"  • .claude/commands/cli/README.md - CLI documentation\n")

    def find_similar_commands(self, query: str, threshold: int = 60, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Find similar command names using fuzzy matching

        Args:
            query: Command name to match
            threshold: Minimum similarity score (0-100)
            limit: Maximum number of suggestions

        Returns:
            List of (command_name, similarity_score) tuples
        """
        # Use fuzzywuzzy to find similar commands
        matches = process.extract(query, self.command_names, scorer=fuzz.ratio, limit=limit)

        # Filter by threshold
        return [(name, score) for name, score in matches if score >= threshold]

    def suggest_commands(self, query: str) -> Optional[str]:
        """
        Suggest commands when user input doesn't match exactly

        Args:
            query: User's attempted command

        Returns:
            Formatted suggestion string or None
        """
        similar = self.find_similar_commands(query, threshold=60, limit=5)

        if not similar:
            return None

        suggestion = f"\n{Colors.YELLOW}Command not found: '{query}'{Colors.ENDC}\n"
        suggestion += f"\n{Colors.CYAN}Did you mean one of these?{Colors.ENDC}\n"

        for name, score in similar:
            cmd = self.commands[name]
            desc = cmd.get('description', '')[:50]
            suggestion += f"  {Colors.GREEN}•{Colors.ENDC} {name} (similarity: {score}%)\n"
            suggestion += f"    {desc}\n"

        suggestion += f"\n{Colors.CYAN}Try:{Colors.ENDC}\n"
        suggestion += f"  python ghl-cli.py help {similar[0][0]}\n"
        suggestion += f"  python ghl-cli.py search \"{query}\"\n"

        return suggestion

    def get_top_commands(self, limit: int = 10) -> List[Dict]:
        """Get top recommended commands for new users"""
        # Curated list of most useful starter commands
        starter_commands = [
            'appointment-reminder',
            'email-sequence',
            'lead-nurture',
            'form-builder',
            'workflow-builder',
            'sms-automation',
            'funnel-builder',
            'calendar-setup',
            'contact-management',
            'pipeline-setup'
        ]

        top_cmds = []
        for name in starter_commands[:limit]:
            if name in self.commands:
                top_cmds.append(self.commands[name])

        return top_cmds

    def show_getting_started(self):
        """Display getting started guide"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}Getting Started with BroBro{Colors.ENDC}\n")

        print(f"{Colors.CYAN}Step 1: Explore Available Commands{Colors.ENDC}")
        print(f"  python ghl-cli.py list\n")

        print(f"{Colors.CYAN}Step 2: Try These Starter Commands{Colors.ENDC}\n")

        top_cmds = self.get_top_commands(5)
        for i, cmd in enumerate(top_cmds, 1):
            print(f"  {i}. {Colors.GREEN}{cmd['name']}{Colors.ENDC}")
            print(f"     {cmd.get('description', '')[:70]}")
            print(f"     Example: python ghl-cli.py {cmd['name']} \"your request\"\n")

        print(f"{Colors.CYAN}Step 3: Search for What You Need{Colors.ENDC}")
        print(f"  python ghl-cli.py search \"appointment reminders\"")
        print(f"  python ghl-cli.py search \"send sms\"\n")

        print(f"{Colors.CYAN}Step 4: Get Detailed Help{Colors.ENDC}")
        print(f"  python ghl-cli.py help appointment-reminder\n")

        print(f"{Colors.CYAN}Learn More:{Colors.ENDC}")
        print(f"  • Full tutorial: docs/ONBOARDING.md")
        print(f"  • All commands: docs/COMMAND_REFERENCE.md")
        print(f"  • Josh Wash workflows: .claude/commands/cli/README.md\n")

    def show_category_help(self, category: str):
        """Show all commands in a specific category"""
        category_lower = category.lower()

        # Find commands in category
        cmds = [cmd for cmd in self.commands.values() if cmd.get('category', '').lower() == category_lower]

        if not cmds:
            print(f"\n{Colors.YELLOW}No commands found in category: {category}{Colors.ENDC}")
            print(f"\n{Colors.CYAN}Available categories:{Colors.ENDC}")

            categories = set(cmd.get('category', 'uncategorized') for cmd in self.commands.values())
            for cat in sorted(categories):
                count = len([c for c in self.commands.values() if c.get('category') == cat])
                print(f"  • {cat} ({count} commands)")

            print()
            return

        print(f"\n{Colors.HEADER}{category.upper()} Commands ({len(cmds)} total){Colors.ENDC}\n")

        for cmd in sorted(cmds, key=lambda x: x['name']):
            print(f"{Colors.GREEN}• {cmd['name']}{Colors.ENDC}")
            print(f"  {cmd.get('description', '')}")

            if cmd.get('josh_wash_workflow'):
                print(f"  {Colors.YELLOW}Josh Wash Workflow:{Colors.ENDC} {cmd['josh_wash_workflow']}")

            if cmd.get('proven_pattern'):
                print(f"  {Colors.CYAN}Pattern:{Colors.ENDC} {cmd['proven_pattern']}")

            print()


def main():
    """Test the help system"""
    import sys

    # Load commands
    commands_json = r"C:\Users\justi\BroBro\.claude\commands\cli\commands.json"

    with open(commands_json, 'r', encoding='utf-8') as f:
        commands = json.load(f)

    help_system = GHLHelpSystem(commands)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'overview':
            help_system.show_help_overview()
        elif sys.argv[1] == 'start':
            help_system.show_getting_started()
        elif sys.argv[1] == 'category' and len(sys.argv) > 2:
            help_system.show_category_help(sys.argv[2])
        elif sys.argv[1] == 'suggest' and len(sys.argv) > 2:
            suggestion = help_system.suggest_commands(sys.argv[2])
            if suggestion:
                print(suggestion)
    else:
        help_system.show_help_overview()


if __name__ == "__main__":
    main()
