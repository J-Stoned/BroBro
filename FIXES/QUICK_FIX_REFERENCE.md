# QUICK FIX REFERENCE - Claude Context Issue

## Problem
```
API Error: 400
messages.152.content.0: unexpected tool_use_id found in tool_result blocks
```

## Cause
Conversation history had tool_result blocks without matching tool_use blocks in previous message.

## Solution Applied

### Files Changed
1. `web/backend/main.py` - Added validation logic
2. `web/backend/.env.example` - Added CLAUDE_FORCE_TEXT_ONLY option

### What Was Fixed
- ✅ Validates tool_use/tool_result pairing
- ✅ Strips orphaned tool blocks
- ✅ Converts broken pairs to text-only
- ✅ Handles both string and array content
- ✅ Added environment variable override

## Quick Start

### 1. Restart Backend
```bash
cd C:\Users\justi\BroBro\web\backend
python main.py
```

### 2. Test the Fix
```bash
python test_context_fix.py
```

Expected output:
```
✅ PASS - Simple Conversation
✅ PASS - With Tool Blocks
✅ PASS - Broken Tool Blocks
✅ PASS - Orphaned Tool Result

Passed: 4/4
🎉 All tests passed!
```

### 3. If Issues Persist

Edit `.env`:
```bash
CLAUDE_FORCE_TEXT_ONLY=true
```

Restart backend and test again.

## How It Works

### Default Mode (CLAUDE_FORCE_TEXT_ONLY=false)
- Smart validation
- Checks tool_use/tool_result pairing
- Strips only broken tool blocks
- Keeps valid tool context

### Force Text-Only Mode (CLAUDE_FORCE_TEXT_ONLY=true)
- Strips ALL tool blocks
- Safest but loses tool context
- Use if validation issues persist

## Monitoring Logs

Look for these in backend console:

```bash
[INFO] Validated 25 messages from conversation history
[WARN] Message 15 has tool_result but previous message is not from assistant
[FIX] Stripping tool_use/tool_result blocks and converting to text-only
```

## Production Recommendations

1. **Keep default mode** (CLAUDE_FORCE_TEXT_ONLY=false)
2. **Monitor logs** for validation warnings
3. **Implement history pruning** (keep last 10-20 messages)
4. **Add token tracking** for $100/month plan

## Token Optimization (For $100 Plan)

Current implementation includes:
- 1MB max per message
- Auto-truncation to 500KB for large messages
- Validation removes broken message pairs (saves tokens)

Additional recommendations:
- Limit conversation history to last 20 messages
- Clear old conversations regularly
- Add caching for common queries

## Files to Review

### Documentation
- `FIXES/CLAUDE_CONTEXT_FIX_2025-11-03.md` - Full documentation

### Code
- `web/backend/main.py` - Lines 40-60 (utility function)
- `web/backend/main.py` - Lines 460-563 (validation logic)

### Testing
- `web/backend/test_context_fix.py` - Test suite

## Support

If you need help:
1. Check backend logs
2. Run test suite
3. Try force text-only mode
4. Share logs if issue persists

---

**Status:** ✅ Fixed and tested  
**Date:** November 3, 2025  
**Ready for:** Production deployment