# 🚨 IMMEDIATE FIX - Claude Code Context Issue

## The Problem
Claude Code is storing images in conversation history and sending them to Anthropic API even when you send text-only messages. This causes the "image exceeds 5MB" error.

## URGENT FIX - DO THIS NOW

### In Claude Code:
1. Type: `/clear`
2. Press Enter
3. Try sending your message again

**That's it!** This clears the conversation context.

## If That Doesn't Work

Try this sequence:

1. **Close Claude Code completely**
   - Exit the VS Code extension

2. **Delete the cache:**
   ```bash
   # On Windows:
   rmdir %APPDATA%\Anthropic /s /q
   
   # On Mac:
   rm -rf ~/.anthropic
   
   # On Linux:
   rm -rf ~/.local/share/anthropic
   ```

3. **Reopen Claude Code**
   - Start fresh without any conversation history

4. **Try sending a message**
   - Should work now

## Why This Happens

Claude Code bug: Images get stored in conversation history, and even text-only messages include the full history when calling Anthropic API

## Prevent It Going Forward

### ✅ DO THIS:
- Type `/clear` every 10-20 messages
- Avoid pasting large images
- Reference file paths instead: `Can you review /path/to/file.png`
- Start new sessions periodically

### ❌ AVOID THIS:
- Pasting large screenshots
- Long conversations with images
- Accumulating 50+ messages

## For Development Going Forward

Since Claude Code has this limitation, consider:

1. **Use Claude web interface**: https://claude.ai
   - No context bloat issues
   - Better for long conversations
   - Supports large file uploads

2. **Keep Claude Code sessions short**
   - Clear context frequently
   - Start new conversations often

3. **Use text references**
   - Don't paste images
   - Use file paths instead
   - Let Claude read files directly

## Quick Commands

```
/clear       - Clear conversation context (USE THIS!)
/file [path] - Reference a file
/search      - Search files
/recent      - Show recent files
```

---

**Try `/clear` right now and let me know if it fixes it!**

If not, close and reopen Claude Code fresh.
