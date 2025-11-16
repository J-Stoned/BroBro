#!/usr/bin/env python3
"""
Claude Code Conversation History Cleaner
Prevents the "image exceeds 5MB" error by managing conversation context
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_claude_code_config_paths():
    """Find Claude Code configuration directories"""
    home = Path.home()
    
    paths = [
        # Claude Code uses Anthropic CLI config
        home / ".anthropic" / "claude-code",
        home / ".config" / "anthropic",
        home / "AppData" / "Roaming" / "Anthropic",  # Windows
        home / "AppData" / "Local" / "Anthropic",
    ]
    
    return [p for p in paths if p.exists()]

def clear_conversation_context():
    """
    Clear Claude Code conversation history by resetting the context.
    This must be done through Claude Code CLI.
    """
    
    print("=" * 60)
    print("Claude Code Context Manager")
    print("=" * 60)
    print()
    
    print("🔄 Clearing conversation context...")
    print()
    print("⚠️  IMPORTANT: You need to do this MANUALLY in Claude Code:")
    print()
    print("Option 1 - Clear Current Chat:")
    print("  1. Press Ctrl+K (or Cmd+K on Mac)")
    print("  2. Type: /clear")
    print("  3. Press Enter")
    print()
    print("Option 2 - Start Fresh Chat:")
    print("  1. Close Claude Code")
    print("  2. Restart Claude Code")
    print("  3. Start a new session")
    print()
    print("Option 3 - Use This Automated Clearer:")
    print()
    
    try:
        # Try to use Claude Code CLI to clear context
        result = subprocess.run(
            ["claude-code", "--reset"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Claude Code context cleared successfully!")
            print(f"Output: {result.stdout}")
            return True
        else:
            print("⚠️  Claude Code CLI not available or reset failed")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  Claude Code CLI not found in PATH")
        print("   Make sure Claude Code is installed globally")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def prevent_future_issues():
    """
    Provide guidance on preventing this issue in the future
    """
    
    print()
    print("=" * 60)
    print("Prevention Tips")
    print("=" * 60)
    print()
    print("To prevent 'image exceeds 5MB' errors:")
    print()
    print("1. ✅ Clear context regularly")
    print("   - After every 10-20 messages with images")
    print("   - Type: /clear")
    print()
    print("2. ✅ Avoid pasting large images")
    print("   - Instead, reference file paths:")
    print("     'Can you review /path/to/file.png'")
    print()
    print("3. ✅ Use code/text references")
    print("   - Paste code snippets, not screenshots")
    print("   - Use: /file path/to/code.js")
    print()
    print("4. ✅ Start fresh sessions")
    print("   - Close and reopen Claude Code periodically")
    print()
    print("5. ✅ Monitor conversation length")
    print("   - Keep conversations under 50 messages")
    print("   - Clear when adding new images")
    print()

def create_claude_code_commands():
    """
    Create useful Claude Code commands to help manage context
    """
    
    commands = {
        "clear": "Clears the current conversation context",
        "file": "Reference a file without pasting its contents",
        "recent": "Show recent files",
        "settings": "Configure Claude Code settings",
    }
    
    print("=" * 60)
    print("Useful Claude Code Commands")
    print("=" * 60)
    print()
    
    for cmd, desc in commands.items():
        print(f"  /{cmd:<10} - {desc}")
    print()

if __name__ == "__main__":
    print()
    print("🚀 Claude Code Conversation History Manager")
    print()
    
    # Try to clear
    success = clear_conversation_context()
    
    # Show prevention tips
    prevent_future_issues()
    
    # Show commands
    create_claude_code_commands()
    
    print("=" * 60)
    print()
    
    if not success:
        print("💡 IMMEDIATE FIX:")
        print()
        print("In Claude Code, type this and press Enter:")
        print("  /clear")
        print()
    else:
        print("✅ Context cleared! You can continue development now.")
        print()
    
    print("If you continue getting errors:")
    print("  1. Close Claude Code completely")
    print("  2. Delete: ~/.anthropic or equivalent")
    print("  3. Reopen Claude Code")
    print()
