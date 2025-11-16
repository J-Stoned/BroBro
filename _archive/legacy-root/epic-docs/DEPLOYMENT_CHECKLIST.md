# BroBro Deployment Checklist

Use this checklist to verify everything is working before deploying to production.

## Pre-Deployment

### Environment Setup
- [ ] Python 3.8+ installed: `python --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] `.env` file created with API keys
- [ ] GOOGLE_API_KEY set and valid
- [ ] ANTHROPIC_API_KEY set and valid
- [ ] CHROMA_URL points to correct instance

### Dependencies
- [ ] Backend dependencies installed: `pip list | grep fastapi`
- [ ] Frontend dependencies installed: `npm list | grep react`
- [ ] No security vulnerabilities: `npm audit`

## Backend Testing

### Server Startup
- [ ] Backend starts without errors: `python -m uvicorn main:app --reload`
- [ ] API responds to health check: `curl http://localhost:8000/health`
- [ ] API docs available: `http://localhost:8000/docs`
- [ ] No error messages in startup

### API Endpoints
- [ ] `/api/chat` endpoint works (Claude)
- [ ] `/api/gemini/chat` endpoint works (Gemini)
- [ ] `/api/collections` lists collections
- [ ] `/api/gemini/status` returns config

### Database Connectivity
- [ ] ChromaDB connection successful
- [ ] Collections loaded: `GET /api/collections`
- [ ] Can query collections
- [ ] No connection errors

## Frontend Testing

### Build & Run
- [ ] Frontend builds without errors: `npm run build`
- [ ] Build succeeds: check `dist/` directory exists
- [ ] Dev server runs: `npm run dev`
- [ ] No build warnings (critical ones only)

### Navigation
- [ ] All tabs render correctly
- [ ] Chat tab has Claude/Gemini selector
- [ ] Can switch between backends
- [ ] Commands tab loads
- [ ] Search tab works
- [ ] Analytics tab displays
- [ ] Workflows tab accessible

### Chat Interface (Claude)
- [ ] Can send messages
- [ ] Can receive responses
- [ ] Markdown renders correctly
- [ ] Sources/citations display
- [ ] Settings work (temperature, tokens)
- [ ] Copy message works
- [ ] Export JSON works
- [ ] Export Markdown works
- [ ] Clear history works
- [ ] Conversation persists after refresh

### Chat Interface (Gemini)
- [ ] Backend selector shows toggle
- [ ] Can switch to Gemini backend
- [ ] Can send messages to Gemini
- [ ] Can receive responses
- [ ] Same features as Claude work
- [ ] Separate conversation history maintained
- [ ] Settings panel works

### UI/UX
- [ ] No console errors (check DevTools)
- [ ] No visual glitches
- [ ] Responsive on mobile (test with DevTools)
- [ ] Touch controls work on mobile
- [ ] Links are clickable
- [ ] Buttons have proper feedback
- [ ] Loading indicators show
- [ ] Error messages are clear

## Integration Testing

### Multi-turn Conversations
- [ ] Send initial question
- [ ] Follow-up question references context
- [ ] Third question continues conversation
- [ ] History shows all exchanges
- [ ] Conversation persists after page refresh

### Backend Switching
- [ ] Start with Claude
- [ ] Switch to Gemini (no data loss)
- [ ] Switch back to Claude
- [ ] Each has separate history
- [ ] Can export from each

### Knowledge Base
- [ ] GHL docs queries work
- [ ] YouTube content retrieval works
- [ ] Business books queries work
- [ ] Can find recent extraction content
- [ ] Citations point to correct sources

## Performance Testing

### Response Times
- [ ] Claude response: < 5 seconds
- [ ] Gemini response: < 3 seconds
- [ ] Frontend interaction: < 500ms
- [ ] No UI blocking during requests

### Load Testing (Optional)
- [ ] Backend handles 5 simultaneous requests
- [ ] Frontend doesn't crash with large responses
- [ ] LocalStorage handles conversation size

## Security Testing

### Authentication
- [ ] API keys are not logged
- [ ] API keys are not in console output
- [ ] API keys are in .env (not in code)
- [ ] .env is in .gitignore

### Data Validation
- [ ] Empty messages rejected
- [ ] Very long messages handled
- [ ] Special characters handled
- [ ] SQL injection not possible (N/A for this system)
- [ ] XSS attacks prevented

### Privacy
- [ ] Conversations stored locally (not uploaded)
- [ ] Can export conversations
- [ ] Can delete conversations
- [ ] No telemetry without consent

## Documentation

### User Facing
- [ ] README.md has Web UI section
- [ ] QUICK_START.md is accurate
- [ ] WEB_UI_SETUP_GUIDE.md is complete
- [ ] Example questions are provided
- [ ] Troubleshooting section covers common issues

### Developer Facing
- [ ] Code has comments where needed
- [ ] Component exports are clear
- [ ] API responses documented
- [ ] Error codes documented

## Deployment Scripts

### Windows (start-servers.bat)
- [ ] Script exists
- [ ] Script is readable
- [ ] Double-click launches servers
- [ ] Both windows appear
- [ ] URLs printed to console

### Unix (start-servers.sh)
- [ ] Script exists
- [ ] Script is executable: `chmod +x`
- [ ] `./start-servers.sh` launches servers
- [ ] Color output displays
- [ ] Can Ctrl+C to stop all

## Final Checks

### Startup Test
- [ ] Run startup script
- [ ] Both servers launch successfully
- [ ] Open http://localhost:5173
- [ ] Can chat immediately
- [ ] No startup errors

### End-to-End Test
- [ ] Send message to Claude
- [ ] Get response with citations
- [ ] Switch to Gemini
- [ ] Send message to Gemini
- [ ] Export conversation
- [ ] Close browser
- [ ] Reopen http://localhost:5173
- [ ] Conversation is still there

### Cleanup
- [ ] No temporary files left
- [ ] No debug mode enabled
- [ ] Console logging is normal
- [ ] Comments are appropriate

## Production Deployment

### Pre-Production
- [ ] All checklist items above complete
- [ ] Create production .env
- [ ] Test with production API keys
- [ ] Run security audit: `npm audit`
- [ ] Test with production database

### Deployment Steps
- [ ] Deploy backend (Render, Railway, etc.)
- [ ] Deploy frontend (Vercel, Netlify, etc.)
- [ ] Configure environment variables
- [ ] Test all endpoints
- [ ] Monitor logs for errors
- [ ] Get feedback from team

### Post-Deployment
- [ ] Set up error logging/monitoring
- [ ] Set up uptime monitoring
- [ ] Document deployment process
- [ ] Create incident response plan
- [ ] Plan for backup/recovery

## Sign-Off

- [ ] All checklist items complete
- [ ] No known bugs
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team approval obtained
- [ ] Ready for production use

**Deployment Date:** _______________

**Approved By:** _______________

**Notes:**
```
[Add any notes here]
```

---

## Quick Reference

### Common Commands

```bash
# Development
npm run dev              # Start frontend dev server
python -m uvicorn main:app --reload  # Start backend dev

# Production
npm run build           # Build frontend
npm run preview         # Preview production build
python -m uvicorn main:app  # Start backend production

# Testing
npm test               # Run frontend tests
python -m pytest       # Run backend tests

# Startup
./start-servers.sh     # Linux/Mac
start-servers.bat      # Windows
```

### Environment Variables Checklist

```
GOOGLE_API_KEY          ✓ Set
ANTHROPIC_API_KEY       ✓ Set
GOOGLE_FILE_SEARCH_STORE_ID  (Optional)
CHROMA_URL              ✓ Set (default: http://localhost:8001)
```

### Endpoints to Verify

```
GET  http://localhost:8000/health           ← Health check
POST http://localhost:8000/api/chat         ← Claude chat
POST http://localhost:8000/api/gemini/chat  ← Gemini chat
GET  http://localhost:8000/docs             ← API documentation
GET  http://localhost:5173                  ← Frontend
```

### Logs to Monitor

```bash
# Backend logs
# Should appear in terminal where uvicorn is running

# Frontend logs
# Should appear in browser console (F12 → Console tab)

# System logs
# Check system logs if servers won't start
```

---

**Version:** 1.0
**Last Updated:** November 15, 2025
