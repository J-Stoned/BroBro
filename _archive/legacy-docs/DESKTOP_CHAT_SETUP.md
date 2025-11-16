# 🚀 BroBro Desktop Chat - Setup Guide

## 📊 Quick Comparison

| Feature | Gradio ⭐ | CustomTkinter | Electron |
|---------|----------|---------------|----------|
| **Setup Time** | 2 minutes | 5 minutes | 15 minutes |
| **Look & Feel** | Web-based | Native Windows | Modern Web |
| **File Size** | Small | Small | Large |
| **Dependencies** | Minimal | Minimal | Node.js required |
| **Best For** | Quick start | Native feel | Polish & distribution |

---

## ⭐ OPTION 1: Gradio (RECOMMENDED TO START)

### Installation:
```bash
pip install gradio requests --break-system-packages
```

### Run:
```bash
cd "C:\Users\justi\BroBro"
python desktop_chat_gradio.py
```

### Access:
Opens automatically at `http://localhost:7860`

### Advantages:
✅ Fastest setup (2 minutes)
✅ Professional looking
✅ Auto-refresh on code changes
✅ Built-in chat UI

---

## 💻 OPTION 2: CustomTkinter (Native)

### Installation:
```bash
pip install customtkinter requests --break-system-packages
```

### Run:
```bash
cd "C:\Users\justi\BroBro"
python desktop_chat_tkinter.py
```

### Advantages:
✅ Native Windows app
✅ No browser needed
✅ Lightweight
✅ Fast startup

---

## 🎨 OPTION 3: Electron (Most Polished)

### Prerequisites:
```bash
# Install Node.js from nodejs.org first
```

### Setup:
```bash
cd "C:\Users\justi\BroBro"
npm create vite@latest brobro-electron -- --template react
cd brobro-electron
npm install
npm install electron electron-builder axios
```

### Advantages:
✅ Most professional
✅ Can package as .exe
✅ Full customization

---

## 🔧 Backend Configuration

All options connect to your FastAPI backend at `http://localhost:8000`

### Make sure your backend is running:
```bash
# Start your BroBro FastAPI server
cd "C:\path\to\brobro-backend"
python main.py
```

### API Endpoint Expected:
```
POST http://localhost:8000/query
Body: {
  "query": "user question",
  "n_results": 5
}
```

If your endpoint is different, edit the API URL in the chat file.

---

## 🚀 Quick Start (Recommended)

### 1. Install Gradio:
```bash
pip install gradio requests --break-system-packages
```

### 2. Start Backend:
```bash
# In terminal 1 - Start your BroBro backend
python your_backend.py
```

### 3. Start Chat:
```bash
# In terminal 2 - Start the chat interface
cd "C:\Users\justi\BroBro"
python desktop_chat_gradio.py
```

### 4. Use It!
Browser opens automatically with chat interface!

---

## 📁 Files Created:

- `desktop_chat_gradio.py` - Gradio interface
- `desktop_chat_tkinter.py` - CustomTkinter interface  
- `ELECTRON_APP_GUIDE.md` - Electron setup guide

---

## 💡 Customization

### Change API URL:
Edit the `api_url` variable in any script:
```python
self.api_url = "http://localhost:YOUR_PORT"
```

### Adjust Number of Results:
Change `n_results` in the query:
```python
"n_results": 5  # Get more/fewer results
```

### Customize UI:
- **Gradio**: Edit theme parameter
- **CustomTkinter**: Change colors in ctk.set_default_color_theme()
- **Electron**: Full CSS/React customization

---

## 🎯 My Recommendation:

**Start with Gradio** - It's fastest and looks great!

Then if you want:
- Native feel → Use CustomTkinter
- Maximum polish → Build Electron app

---

## 🆘 Troubleshooting

### "Cannot connect to backend"
- Make sure your FastAPI server is running
- Check the port matches (default: 8000)
- Verify endpoint URL in script

### "Module not found"
```bash
pip install [module-name] --break-system-packages
```

### "Port already in use"
- Close other instances
- Or change port in script

---

## 🔥 Next Steps:

1. Pick an option (I recommend Gradio first!)
2. Install dependencies
3. Start backend
4. Launch chat interface
5. Query your 1,235+ indexed knowledge base!

**Ready to test it?** 🚀
