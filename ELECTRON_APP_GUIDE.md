# GHL WHIZ - Electron Desktop App

## To Build:

```bash
# Create new project
npm create vite@latest ghl-wiz-desktop -- --template react
cd ghl-wiz-desktop

# Install dependencies
npm install
npm install electron electron-builder axios

# Install Electron as dev dependency
npm install -D concurrently wait-on cross-env

# Copy the React app files from this directory
# Then run:
npm run electron:dev
```

## Project Structure:
```
ghl-wiz-desktop/
├── src/
│   ├── App.jsx           (Main chat interface)
│   ├── components/
│   │   ├── ChatMessage.jsx
│   │   ├── ChatInput.jsx
│   │   └── Sidebar.jsx
│   └── api/
│       └── chromadb.js   (API calls to your backend)
├── electron/
│   └── main.js          (Electron main process)
├── package.json
└── README.md
```

## Features:
- Modern chat UI with message history
- Real-time ChromaDB queries
- Dark/light mode
- Keyboard shortcuts
- Tray icon support
- Auto-updates (optional)

## To Run:
```bash
npm run electron:dev
```

## To Build Executable:
```bash
npm run electron:build
```

This creates a standalone .exe you can click to launch!
