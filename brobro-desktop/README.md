# 🚀 BroBro Desktop - Complete Setup Guide

## 📋 Prerequisites

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **BroBro Backend Running**
   - Your FastAPI server must be running on http://localhost:8000
   - Make sure ChromaDB is accessible

---

## 🛠️ Installation

### Step 1: Navigate to Project
```bash
cd "C:\Users\justi\BroBro\brobro-desktop"
```

### Step 2: Install Dependencies
```bash
npm install
```

This will install:
- React & React DOM
- Vite (build tool)
- Electron
- Axios (API calls)
- Lucide React (icons)
- Build tools

**Installation time:** ~2-3 minutes

---

## 🎯 Running the App

### Development Mode (Recommended for testing)

**Terminal 1 - Start Backend:**
```bash
cd "C:\Users\justi\BroBro"
# Start your FastAPI backend
python your_backend_file.py
```

**Terminal 2 - Start Desktop App:**
```bash
cd "C:\Users\justi\BroBro\brobro-desktop"
npm run electron:dev
```

The app will:
- ✅ Start Vite dev server on port 5173
- ✅ Launch Electron window automatically
- ✅ Open DevTools for debugging
- ✅ Hot-reload on code changes

---

## 📦 Building Standalone .exe

### Build for Distribution:
```bash
npm run electron:build:win
```

This creates:
- Installable .exe in `dist/`
- Can be shared/installed on other Windows machines
- No Node.js required on target machine

**Build time:** ~5 minutes

**Output location:** `brobro-desktop/dist/BroBro Desktop Setup.exe`

---

## 🎨 Features

### ✅ Built-In:
- Real-time ChromaDB query
- Message history
- Connection status monitoring
- Source attribution
- Auto-scrolling chat
- Keyboard shortcuts (Enter to send)
- Clear chat functionality
- Loading states
- Error handling
- Dark theme UI

### 🔧 Customizable:
- API endpoint URL
- Number of results returned
- UI colors & styling
- Window size & behavior

---

## ⚙️ Configuration

### Change API Endpoint:
Edit `src/api/chromadb.js`:
```javascript
const API_BASE_URL = 'http://localhost:YOUR_PORT';
```

### Change Number of Results:
Edit `src/App.jsx` in `handleSendMessage`:
```javascript
const response = await chromaAPI.query(message, 10); // Change from 5 to 10
```

### Customize Styling:
Edit `src/styles/App.css` - CSS variables at top:
```css
:root {
  --accent: #7aa2f7;  /* Change accent color */
  --bg-primary: #1a1b26;  /* Change background */
  /* ... */
}
```

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
**Problem:** FastAPI server not running
**Solution:** Start your backend first:
```bash
python your_backend.py
```

### "npm install fails"
**Problem:** Node.js not installed or old version
**Solution:** Install Node.js v18+ from nodejs.org

### "Port 5173 already in use"
**Problem:** Another Vite instance running
**Solution:** Kill process or change port in vite.config.js

### App window blank/white
**Problem:** React build error
**Solution:** Check terminal for errors, fix code issues

### Cannot build .exe
**Problem:** Missing build dependencies
**Solution:** 
```bash
npm install electron-builder --save-dev
```

---

## 📁 Project Structure

```
ghl-wiz-desktop/
├── src/
│   ├── components/
│   │   ├── ChatContainer.jsx    # Main chat interface
│   │   ├── ChatMessage.jsx      # Individual messages
│   │   └── Sidebar.jsx          # Left sidebar
│   ├── api/
│   │   └── chromadb.js          # API service
│   ├── styles/
│   │   └── App.css              # All styling
│   ├── App.jsx                  # Main app component
│   └── main.jsx                 # React entry point
├── electron/
│   ├── main.js                  # Electron main process
│   └── preload.js               # Preload script
├── public/                      # Static assets
├── package.json                 # Dependencies & scripts
├── vite.config.js              # Vite configuration
└── index.html                   # HTML entry

```

---

## 🚀 Quick Start Commands

```bash
# Install
npm install

# Run in development
npm run electron:dev

# Build for production
npm run electron:build:win

# Just run React (without Electron)
npm run dev
```

---

## 💡 Development Tips

### Hot Reload
Changes to React components auto-reload in dev mode. No restart needed!

### DevTools
Press `Ctrl+Shift+I` in the app to open DevTools for debugging.

### Console Logs
All console.log statements appear in the DevTools console.

### Backend Testing
Test your backend separately before running the app:
```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"query\":\"test\",\"n_results\":5}"
```

---

## 🎯 Next Steps After Install

1. ✅ Run `npm install`
2. ✅ Start your backend
3. ✅ Run `npm run electron:dev`
4. ✅ Test queries in the app
5. ✅ Customize as needed
6. ✅ Build .exe for distribution

---

## 📧 Support

Issues? Check:
1. Node.js version (v18+)
2. Backend running on port 8000
3. No firewall blocking localhost
4. Terminal for error messages

---

**Built by:** J Stone Media Solutions  
**Version:** 1.0.0  
**Tech Stack:** Electron + React + Vite + Axios

🎉 **Your ELITE desktop app is ready to go!**
