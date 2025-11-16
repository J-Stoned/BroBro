# Error Handling Test Results

**Date:** October 29, 2025
**Frontend:** Running at http://localhost:3000
**Backend:** Offline (testing scenario)

---

## Test Scenario 1: Backend Offline ✅

### Current State
- Frontend running: http://localhost:3000
- Backend offline (port 8000 not listening)
- ChromaDB offline (port 8001 not listening)

### Expected Behavior

#### 1. Header Connection Status
- [ ] Red "Offline" badge visible
- [ ] No document count shown
- [ ] Status indicator updates automatically

#### 2. Commands Tab
- [ ] Shows OfflineMessage component
- [ ] Message: "Backend Server Offline"
- [ ] Displays startup instructions (4 steps)
- [ ] "Check Connection" button visible
- [ ] No command cards shown

#### 3. Chat Tab
- [ ] Empty state shows initially
- [ ] When sending message → OfflineMessage appears
- [ ] Message about backend not responding
- [ ] Retry button functional

#### 4. Search Tab
- [ ] Empty state shows initially
- [ ] When submitting search → OfflineMessage appears
- [ ] Clear error messaging
- [ ] Retry button functional

#### 5. Setup Management Tab
- [ ] OfflineMessage shown on load
- [ ] Cannot display system info
- [ ] Refresh button shows retry option

#### 6. Footer
- [ ] Shows "ChromaDB disconnected"
- [ ] Shows "0 documents indexed" or similar

---

## Test Scenario 2: Backend Starts (Recovery) ⏳

### Steps to Test
1. Open terminal in `c:\Users\justi\BroBro\web\backend`
2. Run: `python main.py`
3. Wait for: "Uvicorn running on http://0.0.0.0:8000"
4. Wait 10 seconds for health check polling
5. Observe frontend changes

### Expected Behavior

#### Automatic Recovery (within 10 seconds)
- [ ] Header changes to "Online" (green badge)
- [ ] Document count appears (e.g., "1,235 docs")
- [ ] Footer shows "documents indexed"

#### Commands Tab
- [ ] Click "Check Connection" button
- [ ] OfflineMessage disappears
- [ ] Command cards load and display
- [ ] No console errors

#### Chat Tab
- [ ] Click "Check Connection" (if error shown)
- [ ] Error clears
- [ ] Send test message: "How do I create a lead nurture workflow?"
- [ ] Response appears with search results
- [ ] Sources expandable

#### Search Tab
- [ ] Retry previous search OR enter new query
- [ ] Search executes successfully
- [ ] Results display with relevance scores
- [ ] No errors

#### Setup Management Tab
- [ ] Click "Refresh" or "Check Connection"
- [ ] System info loads
- [ ] ChromaDB status shows "Connected" (if ChromaDB is running)
- [ ] Collections display document counts

---

## Test Scenario 3: ChromaDB Disconnected ⏳

### Setup
1. Backend running
2. ChromaDB NOT running
3. Frontend open

### Expected Behavior
- [ ] Header shows "Degraded" (yellow badge)
- [ ] Search works but returns "Service Unavailable" or no results
- [ ] Setup tab shows ChromaDB = Disconnected
- [ ] Footer shows "ChromaDB disconnected"

---

## Console Error Verification

### Frontend Console (F12 → Console)

**Expected Errors (Backend Offline):**
```
Failed to load commands: [object Object]
```

**No Unexpected Errors:**
- ❌ No "undefined is not a function"
- ❌ No "Cannot read property of undefined"
- ❌ No React component errors
- ❌ No missing import errors

### Vite Output

**Expected Proxy Errors (Backend Offline):**
```
[vite] http proxy error: /health
AggregateError [ECONNREFUSED]

[vite] http proxy error: /api/search
AggregateError [ECONNREFUSED]
```

These are EXPECTED and NORMAL when backend is offline.

**No Compilation Errors:**
- ✅ All HMR updates successful
- ✅ No TypeScript/JavaScript syntax errors
- ✅ No module resolution errors

---

## Manual Testing Checklist

### Before Backend Start (Offline State)

Commands Tab:
- [ ] Navigate to Commands tab
- [ ] See OfflineMessage with startup instructions
- [ ] Click "Check Connection" → still offline (expected)
- [ ] No crashes or console errors

Chat Tab:
- [ ] Navigate to Chat tab
- [ ] See empty state with example prompts
- [ ] Type message and click Send
- [ ] See OfflineMessage appear
- [ ] Verify message content makes sense

Search Tab:
- [ ] Navigate to Search tab
- [ ] See empty state
- [ ] Enter search query: "appointment reminders"
- [ ] Click Search
- [ ] See OfflineMessage with retry button

Setup Tab:
- [ ] Navigate to Setup Management tab
- [ ] See OfflineMessage
- [ ] Verify startup instructions are clear

Analytics Tab:
- [ ] Navigate to Analytics tab
- [ ] Check if analytics components handle offline state
- [ ] (May need additional error handling)

Workflows Tab:
- [ ] Navigate to Workflows tab
- [ ] Check if workflow builder handles offline state
- [ ] (May need additional error handling)

### After Backend Start (Recovery)

Header:
- [ ] Wait up to 10 seconds
- [ ] Status changes from "Offline" to "Checking" to "Online"
- [ ] Document count appears

Commands Tab:
- [ ] Return to Commands tab
- [ ] Click "Check Connection"
- [ ] Commands load successfully
- [ ] Can open command details
- [ ] Can favorite commands
- [ ] Search and filters work

Chat Tab:
- [ ] Return to Chat tab
- [ ] Send message: "How do I set up SMS automation?"
- [ ] Response appears quickly
- [ ] Sources are expandable
- [ ] Can copy messages
- [ ] No error messages

Search Tab:
- [ ] Return to Search tab
- [ ] Search for: "lead nurture workflow"
- [ ] Results appear with relevance scores
- [ ] Can view source links
- [ ] Category filters work

Setup Tab:
- [ ] Return to Setup Management tab
- [ ] Click Refresh
- [ ] System info loads
- [ ] ChromaDB status updates
- [ ] Collections show document counts

---

## Performance Verification

### Connection Status Polling
- [ ] Health check occurs every ~10 seconds
- [ ] No excessive network requests
- [ ] Polling doesn't cause performance issues

### Retry Behavior
- [ ] Clicking "Check Connection" makes exactly 1 request
- [ ] Retry doesn't spam the backend
- [ ] Exponential backoff works (1s, 2s, 4s delays)

---

## Edge Cases to Test

### Rapid Backend Restart
1. Backend running
2. Stop backend (Ctrl+C)
3. Immediately restart backend
4. Observe frontend recovery

Expected:
- [ ] Status briefly shows "Offline"
- [ ] Automatically recovers within 10 seconds
- [ ] No stuck states
- [ ] No duplicate requests

### Slow Backend Response
1. Modify backend to add artificial delay (10+ seconds)
2. Make API request
3. Observe timeout behavior

Expected:
- [ ] Request completes (unless >30s timeout)
- [ ] Loading indicator shows during wait
- [ ] No timeout error if <30s
- [ ] Timeout error if >30s

### Network Tab Inspection
1. Open DevTools (F12) → Network tab
2. Filter: Fetch/XHR
3. Trigger API calls (search, load commands, etc.)

Expected:
- [ ] Failed requests show red status (when offline)
- [ ] Successful requests show 200 status (when online)
- [ ] Request/Response data is correct
- [ ] No orphaned pending requests

---

## Documentation Verification

### BACKEND_STARTUP_GUIDE.md
- [ ] Instructions are clear
- [ ] Commands are correct for Windows
- [ ] Paths match actual project structure
- [ ] Troubleshooting section is helpful

### ERROR_HANDLING_IMPLEMENTATION.md
- [ ] Accurately describes implementation
- [ ] Code examples are correct
- [ ] Patterns are easy to follow
- [ ] All modified files listed

---

## Next Steps After Testing

### If Tests Pass ✅
1. Mark error handling implementation complete
2. Update WorkflowBuilder.jsx (optional)
3. Update Analytics components (optional)
4. Document any issues found

### If Tests Fail ❌
1. Note which scenarios failed
2. Check console for error details
3. Fix identified issues
4. Re-test until all scenarios pass

---

## Testing Commands

### Start Backend
```bash
cd "c:\Users\justi\BroBro\web\backend"
python main.py
```

### Start ChromaDB (if needed)
```bash
cd "c:\Users\justi\BroBro"
start-chroma.bat
```

### Check Backend Health
```bash
curl http://localhost:8000/health
```

Or open in browser: http://localhost:8000/health

### View Frontend
http://localhost:3000

### Check Running Processes
```bash
# Check if backend is running (port 8000)
netstat -ano | findstr :8000

# Check if ChromaDB is running (port 8001)
netstat -ano | findstr :8001

# Check if frontend is running (port 3000)
netstat -ano | findstr :3000
```

---

## Test Results Summary

**Date:** ___________
**Tester:** ___________

### Overall Status
- [ ] All core scenarios passed
- [ ] Minor issues found (document below)
- [ ] Major issues found (document below)

### Issues Found
1.
2.
3.

### Notes


---

**Status:** Ready for Testing
**Frontend:** Running at http://localhost:3000 (backend offline)
**Next:** Start backend and verify recovery
