# 📋 Claude Code Development Guide - Workaround Strategy

## The Situation
Claude Code has a bug where conversation history accumulates images, causing API errors. We need to work around this.

## Best Practices for Unblocked Development

### 1️⃣ Keep Conversations Short
- **Max 20-30 messages per session** with images
- Type `/clear` when approaching the limit
- Start fresh conversations frequently

### 2️⃣ Never Paste Images
Instead of:
```
❌ [Paste screenshot of error]
```

Do this:
```
✅ "I got an error in the file C:\Users\justi\BroBro\web\backend\main.py at line 445"
```

### 3️⃣ Reference Files Directly
Instead of:
```
❌ Here's my code: [paste 100 lines]
```

Do this:
```
✅ "Can you review C:\Users\justi\BroBro\web\frontend\src\components\ChatInterface.jsx"
✅ "Check the chat endpoint at line 378 in web/backend/main.py"
```

### 4️⃣ Use Clear Context Commands

When conversation gets long, type:
```
/clear
```

Then ask your question fresh in the new context.

### 5️⃣ Session Management

**Start of work:**
- Open Claude Code
- Start fresh session
- Ready to go

**During work (every 15-20 minutes):**
- Type `/clear` when conversation gets long
- Start a new focused question
- Continue developing

**End of work:**
- Close Claude Code
- Reopen next session

## Workflow Example

### ❌ Bad Workflow (Causes Errors)
```
1. Open Claude Code
2. Ask 50+ questions
3. Paste 10 screenshots
4. Paste 5 code files
5. Get "image exceeds 5MB" error
6. Stuck
```

### ✅ Good Workflow (Works!)
```
1. Open Claude Code - Fresh session
2. Ask question 1: "Can you review this file..."
3. Ask question 2: "Now let's fix the bug..."
4. Ask question 3: "Can you also check..."
5. Type /clear (or close/reopen)
6. Start new session for new feature
7. Repeat - Never accumulate too much
```

## Working on GHL_WIZ Development

### Starting a Session
```
1. Open Claude Code
2. "I'm working on GHL_WIZ. Help me debug the chat interface."
3. Get help
4. Implement
5. Type /clear or close
6. Start fresh session for next task
```

### Asking for Code Review
```
Ask: "Can you review web/frontend/src/components/ChatInterface.jsx?"

Don't paste the whole file - let Claude read it.
```

### Debugging Errors
```
Ask: "I'm getting an error: [copy error message]
      In file: web/backend/main.py
      At line: 445"

Don't paste 100 lines of code.
```

### Making Changes
```
Ask: "In web/backend/main.py, change line 450 from:
      OLD CODE
      to:
      NEW CODE"

Or: "What should line 450 be to fix this issue?"
```

## Emergency Recovery

If you get stuck:

```bash
# Option 1: Use /clear command
In Claude Code, type: /clear

# Option 2: Close and restart
Close Claude Code completely
Reopen Claude Code
Start fresh conversation

# Option 3: Delete cache
Close Claude Code
Delete: C:\Users\justi\AppData\Roaming\Anthropic\
Reopen Claude Code
```

## File Paths for Reference

Use these when asking Claude Code to review files:

```
C:\Users\justi\BroBro\web\frontend\src\components\ChatInterface.jsx
C:\Users\justi\BroBro\web\backend\main.py
C:\Users\justi\BroBro\web\backend\ghl_api\client.py
C:\Users\justi\BroBro\web\backend\search\unified_search.py
```

## Pro Tips

✅ **DO:**
- Keep conversations focused
- Clear context regularly
- Use file references
- Ask specific questions
- Work on one feature per session

❌ **DON'T:**
- Paste large files
- Include screenshots
- Let conversations go 50+ messages
- Work on multiple features in one session
- Ignore `/clear` prompts

## Keyboard Shortcuts

```
Ctrl+K (or Cmd+K)  - Claude Code command palette
Then type: /clear   - Clear context
Then type: /file    - Reference a file
Then type: /search  - Search files
```

---

**Key Takeaway:** Keep Claude Code conversations SHORT and FOCUSED.

Clear context frequently with `/clear` to prevent errors.

Reference files instead of pasting code.

This way you can develop without hitting the image size limit!
