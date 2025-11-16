# Claude API Context/Tool Use Fix - November 3, 2025

## Problem Summary

API Error 400 when using the chat endpoint with conversation history:

```
messages.152.content.0: unexpected tool_use_id found in tool_result blocks: toolu_0193WRYHRZATo7RUSCT6CoSL. 
Each tool_result block must have a corresponding tool_use block in the previous message.
```

## Root Cause

When Claude uses tools during a conversation, it creates paired messages:

1. **Assistant message with tool_use block**:
```python
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll search for that..."},
    {"type": "tool_use", "id": "toolu_123", "name": "search", "input": {...}}
  ]
}
```

2. **User message with tool_result block**:
```python
{
  "role": "user",
  "content": [
    {"type": "tool_result", "tool_use_id": "toolu_123", "content": "results..."}
  ]
}
```

The error occurred because:
- Conversation history was being sent to the API with tool_result blocks
- The corresponding tool_use blocks were missing or mismatched
- This breaks Claude API's validation (tool_use_id must match a tool_use in the previous message)

## Solution Implemented

### 1. Added Conversation History Validation (main.py lines 460-563)

**Key Improvements:**
- Validates tool_use/tool_result pairing
- Strips orphaned tool_result blocks (no matching tool_use)
- Converts tool blocks to text-only when pairing is broken
- Removes both messages in a broken tool pair
- Handles both string and array content types

### 2. Added Utility Function (main.py lines 40-60)

```python
def strip_tool_blocks_from_message(content):
    """Strip tool_use and tool_result blocks, return text-only content"""
```

### 3. Added Environment Variable Override

New `.env` option: `CLAUDE_FORCE_TEXT_ONLY`

**Usage:**
```bash
# .env file
CLAUDE_FORCE_TEXT_ONLY=true  # Strip ALL tool blocks (safest but loses context)
CLAUDE_FORCE_TEXT_ONLY=false # Smart validation (default, recommended)
```

## How It Works

### Smart Validation Mode (Default: CLAUDE_FORCE_TEXT_ONLY=false)

1. **Process each message in conversation history**
2. **For string content:** Pass through after size/validation checks
3. **For array content with tool_result:**
   - Check if previous message is from assistant
   - Verify tool_use_id matches in previous message
   - If invalid: Strip tool blocks, extract text only
   - If broken pair: Remove both messages
4. **For other array content:** Pass through if valid

### Force Text-Only Mode (CLAUDE_FORCE_TEXT_ONLY=true)

1. **Strip ALL tool_use and tool_result blocks**
2. **Extract only text content**
3. **Simplest but loses tool interaction context**

## Testing

### Option 1: Quick Test (Recommended)Restart your backend server and test the chat endpoint.

The conversation history is now validated and cleaned before sending to Claude API.

### Option 2: Test with curl

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how do I send an SMS in GHL?",
    "conversation_history": [
      {
        "role": "user",
        "content": "tell me about workflows"
      },
      {
        "role": "assistant", 
        "content": "Workflows in GHL are automation sequences..."
      }
    ],
    "n_results": 5
  }'
```

### Option 3: Force Text-Only Mode (If issues persist)

1. Edit `.env` file:
```bash
CLAUDE_FORCE_TEXT_ONLY=true
```

2. Restart backend
3. Test again

This strips ALL tool blocks but is the safest option if validation issues persist.

## Monitoring

The fix includes detailed logging:

```
[INFO] Validated 25 messages from conversation history
[WARN] Message 15 has tool_result but previous message is not from assistant
[FIX] Stripping tool_use/tool_result blocks and converting to text-only
[ERROR] Message 20 has tool_result IDs that don't match previous tool_use IDs
  tool_use IDs: {'toolu_abc123'}
  tool_result IDs: {'toolu_xyz789'}
[FIX] Removing BOTH messages to break the invalid chain
```

## What Changed in Code

### Files Modified

1. **web/backend/main.py**
   - Added `strip_tool_blocks_from_message()` utility (lines 40-60)
   - Updated chat endpoint validation logic (lines 460-563)
   - Added FORCE_TEXT_ONLY environment check

2. **web/backend/.env.example**
   - Added `CLAUDE_FORCE_TEXT_ONLY` configuration option

3. **FIXES/CLAUDE_CONTEXT_FIX_2025-11-03.md**
   - This documentation file

### Key Code Sections

**Tool Block Validation:**
```python
# Check if previous assistant message has matching tool_use
prev_content = validated_messages[-1]["content"]
if isinstance(prev_content, list):
    tool_use_ids = {
        block.get("id")
        for block in prev_content
        if isinstance(block, dict) and block.get("type") == "tool_use"
    }
    
    tool_result_ids = {
        block.get("tool_use_id")
        for block in content
        if isinstance(block, dict) and block.get("type") == "tool_result"
    }
    
    if not tool_result_ids.issubset(tool_use_ids):
        # Remove invalid pair
        validated_messages.pop()
        continue
```

**Force Text-Only Override:**
```python
if FORCE_TEXT_ONLY:
    text_only_content = strip_tool_blocks_from_message(content)
    if text_only_content:
        validated_messages.append({
            "role": role,
            "content": text_only_content
        })
    continue
```

## Benefits of This Fix

1. **Prevents API errors** - Validates tool_use/tool_result pairing before sending to Claude
2. **Automatic recovery** - Strips broken tool blocks and extracts text
3. **Configurable** - Can force text-only mode if needed
4. **Detailed logging** - Shows exactly what's being cleaned/removed
5. **Backward compatible** - Works with existing conversation history

## Important Notes

### Token Limits

The fix includes size checks:
- 1MB max per message
- Messages over 1MB are truncated to 500KB
- This is based on your concern about the $100/month plan token limits

### When to Use Force Text-Only Mode

Use `CLAUDE_FORCE_TEXT_ONLY=true` if:
- You continue to see tool_use_id errors
- You don't need tool interaction history
- You want maximum stability
- You're on a lower-tier plan with strict limits

**Trade-off:** You lose the context of what tools were used and their results.

### Production Deployment

For production:
1. Keep `CLAUDE_FORCE_TEXT_ONLY=false` (default)
2. Monitor logs for validation warnings
3. Only enable force text-only if errors persist
4. Consider implementing conversation history pruning to keep context under limits

## Troubleshooting

### If you still get errors:

1. **Enable force text-only mode:**
```bash
CLAUDE_FORCE_TEXT_ONLY=true
```

2. **Check your conversation history structure**
- Look for tool_use or tool_result in the content
- Verify role alternation (user -> assistant -> user)

3. **Clear conversation history**
- Start a fresh conversation
- The error likely came from accumulated broken tool pairs

4. **Check token usage**
- Large conversation histories consume more tokens
- Consider implementing a sliding window (keep last N messages only)

## Next Steps

### Immediate (Already Done)
- ✅ Added validation logic
- ✅ Added utility function
- ✅ Added environment variable
- ✅ Updated .env.example
- ✅ Created documentation

### Recommended for Production
- [ ] Add conversation history pruning (keep last 10-20 messages)
- [ ] Add token usage tracking per conversation
- [ ] Implement conversation summarization for long threads
- [ ] Add rate limiting per user
- [ ] Set up monitoring/alerting for validation warnings

### For $100/Month Plan Token Optimization
- [ ] Implement message compression (remove redundant context)
- [ ] Add caching for common queries
- [ ] Limit conversation history depth
- [ ] Add token usage dashboard for users

## Testing Results

### Before Fix
```
API Error: 400
messages.152.content.0: unexpected tool_use_id found in tool_result blocks
```

### After Fix (Expected)
```
[INFO] Validated 152 messages from conversation history
[FIX] Stripping tool_use/tool_result blocks and converting to text-only (if any broken pairs)
✅ Chat response generated successfully
```

## Contact

If you continue to experience issues after implementing this fix:

1. Check the backend logs for validation warnings
2. Enable `CLAUDE_FORCE_TEXT_ONLY=true` as a temporary measure
3. Share the logs showing what messages are being cleaned

---

**Fix implemented:** November 3, 2025  
**Version:** 1.0  
**Status:** ✅ Ready for testing