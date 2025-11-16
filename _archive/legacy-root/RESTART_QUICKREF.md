# 🚀 QUICK RESTART REFERENCE

**Created**: 2025-10-29
**Purpose**: Quick commands to get back up and running after restart

---

## ⚡ 3-Step Restart (Fast)

### 1. Start ChromaDB
```bash
npm run start-chroma
```
Wait 5 seconds for Docker to start.

### 2. Start Backend
```bash
cd web/backend
python main.py
```
Wait for "Uvicorn running on http://localhost:8000"

### 3. Start Frontend
```bash
cd web/frontend
npm run dev
```
Wait for "Local: http://localhost:3000"

### 4. Open Browser
```
http://localhost:3000
```

---

## ✅ What Should Work

### 4 Tabs Visible
1. 💬 **Chat** - AI-powered chat interface
2. 📖 **Commands** - Browse 100+ commands
3. 🔍 **Search** - Direct search
4. ⚙️ **Setup** - System health

### Test Chat
- Type message → Press Enter → See results

### Test Commands
- Browse grid → Click command → See modal → Click "Use in Chat"

### Test Integration
- Commands → "Use in Chat" → Auto-switches to Chat tab

---

## 🔧 If Something's Wrong

### Frontend won't start?
```bash
cd web/frontend
npm install
npm run dev
```

### Backend won't start?
```bash
# Check ChromaDB first
docker ps

# If not running:
npm run start-chroma
```

### Console errors?
- Shouldn't happen (had ZERO before restart)
- Clear browser cache
- Restart frontend

---

## 📞 Help Files

- **CHECKPOINT_2025-10-29.md** - Full restart guide
- **EPIC_8_QUICKSTART.md** - Chat interface guide
- **EPIC_8_9_SESSION_SUMMARY.md** - What was completed
- **WEB_INTERFACE_QUICKSTART.md** - 5-minute setup

---

## ✅ Status: PRODUCTION READY

- Epic 8: Chat Interface ✅ Complete
- Epic 9: Command Library ✅ Complete
- Zero console errors ✅ Verified
- All 9 epics complete ✅

**Safe to restart. Everything is saved.**

---

**Quick Ref Card** | **BroBro v1.0.0** | **2025-10-29**
