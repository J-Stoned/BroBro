# BroBro Web Interface - Quick Start Guide

🎉 **Epic 7: Setup Management - COMPLETE!**

## 🚀 5-Minute Quick Start

### Prerequisites Check
```bash
# Verify you have:
python --version  # Need 3.8+
node --version    # Need 18+
npm --version     # Need 9+
```

### Step 1: Start ChromaDB
```bash
# From project root
npm run start-chroma
```

### Step 2: Start Backend (Choose one method)

**Method A - Batch Script (Windows):**
```bash
cd web
start-backend.bat
```

**Method B - Manual:**
```bash
cd web/backend
pip install -r requirements.txt
python main.py
```

✅ Backend running at: **http://localhost:8000**

### Step 3: Start Frontend (Choose one method)

**Method A - Batch Script (Windows):**
```bash
cd web
start-frontend.bat
```

**Method B - Manual:**
```bash
cd web/frontend
npm install
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

## 🎯 Access the Application

1. **Open your browser**: http://localhost:3000
2. **Search Tab**: Try searching "appointment reminders"
3. **Setup Management Tab**: View system health and configuration

## ✨ What You Can Do

### Search Interface
- Search across 1,235+ GHL documents
- Filter by Commands or Documentation
- View relevance scores
- Access source links
- See example queries

### Setup Management (Epic 7)
- Monitor system health
- Check ChromaDB connection
- View collection statistics
- See configuration details
- Refresh system data

## 🔍 Test It Works

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Search
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "workflows", "n_results": 3}'
```

### Test 3: System Info
```bash
curl http://localhost:8000/api/system/info
```

## 📊 Expected Results

### Healthy System
- ✅ Backend: "status": "healthy"
- ✅ ChromaDB: "chroma_connected": true
- ✅ Collections: ghl-knowledge-base (252), ghl-docs (960)
- ✅ Total: 1,212 documents

### Search Results
- ⚡ Response time: 100-130ms
- 🎯 Relevance scores: 70-87%
- 📚 Mixed sources: Commands + Documentation
- 🔗 Direct links to official docs

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Install dependencies
cd web/backend
pip install fastapi uvicorn pydantic python-dotenv
```

### Frontend Won't Start
```bash
# Install dependencies
cd web/frontend
npm install
```

### ChromaDB Not Connected
```bash
# Start ChromaDB from project root
npm run start-chroma

# Verify it's running
docker ps | grep chroma
```

### Port Already in Use
```bash
# Backend: Edit web/backend/main.py, change port 8000
# Frontend: Edit web/frontend/vite.config.js, change port 3000
```

## 📚 Documentation

- **Full Documentation**: [web/README.md](web/README.md)
- **Deployment Guide**: [web/DEPLOYMENT.md](web/DEPLOYMENT.md)
- **Implementation Details**: [web/IMPLEMENTATION_SUMMARY.md](web/IMPLEMENTATION_SUMMARY.md)

## 🎓 BMAD-METHOD

This web interface was built following the BMAD-METHOD:

✅ **Epic 7 Stories (All Complete)**:
1. System health monitoring
2. ChromaDB connection management
3. Collection statistics display
4. Configuration information
5. Live refresh capability

## 🎉 Success!

If you see:
- ✅ Green health indicator in top-right
- ✅ Search returns results
- ✅ Setup Management shows system info
- ✅ No error messages

**You're ready to go!** 🚀

## 🆘 Need Help?

1. Check [web/README.md](web/README.md) for detailed docs
2. Review [web/DEPLOYMENT.md](web/DEPLOYMENT.md) for deployment
3. See [web/IMPLEMENTATION_SUMMARY.md](web/IMPLEMENTATION_SUMMARY.md) for technical details

---

**BroBro v1.0.0** | Built with BMAD-METHOD | Production Ready ✅
