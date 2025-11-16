# BroBro Platform Scripts

## Cleanup Scripts

### PowerShell (Recommended)
```bash
npm run cleanup
# OR
powershell -ExecutionPolicy Bypass -File scripts/cleanup-windows.ps1
```

### Batch File (Alternative)
```bash
npm run cleanup-bat
# OR
scripts\cleanup-windows.bat
```

## Startup Scripts

### Start All Services
```bash
npm run start-all
# OR
scripts\start-all.bat
```

Opens 3 terminal windows:
- ChromaDB on port 8001
- Backend on port 8000
- Frontend on port 3000

### Full Restart (Cleanup + Start)
```bash
npm run restart
# OR
scripts\restart-all.bat
```

## Manual Cleanup

If scripts don't work, try manual steps:

1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to Details tab
3. Find all `python.exe` processes -> End Task
4. Find all `node.exe` processes -> End Task
5. Restart computer if still stuck

## Troubleshooting

### "Cannot kill process"
- Run PowerShell/CMD as Administrator
- Or restart computer

### "Port still in use"
Check what's using the port:
```bash
netstat -ano | findstr :8000
```

Kill specific process:
```bash
taskkill /F /PID <process_id>
```

### Scripts don't run
Enable PowerShell scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
