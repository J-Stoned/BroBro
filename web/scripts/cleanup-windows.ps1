Write-Host "BroBro Cleanup Script" -ForegroundColor Cyan

# Kill Python
Write-Host "Killing Python processes..."
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "[OK] Python stopped" -ForegroundColor Green

# Kill Node
Write-Host "Killing Node processes..."
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "[OK] Node stopped" -ForegroundColor Green

# Kill port 8000
Write-Host "Cleaning port 8000..."
$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "[OK] Port 8000 freed" -ForegroundColor Green
}

# Kill port 8001
Write-Host "Cleaning port 8001..."
$conn = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "[OK] Port 8001 freed" -ForegroundColor Green
}

# Kill port 3000
Write-Host "Cleaning port 3000..."
$conn = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "[OK] Port 3000 freed" -ForegroundColor Green
}

Write-Host "Cleanup complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"
