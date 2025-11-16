@echo off
echo ============================================
echo BroBro - Best Practices Pipeline
echo ============================================
echo.
echo This will:
echo 1. Scrape best practices articles from multiple sources
echo 2. Embed them into the ghl-best-practices collection
echo.
echo ============================================
echo.

echo [Step 1/2] Scraping best practices articles...
echo.
python scripts\scrape-best-practices.py
if errorlevel 1 (
    echo.
    echo [ERROR] Scraping failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo.
echo [Step 2/2] Embedding articles into ChromaDB...
echo.

REM Find the most recent best-practices JSON file
for /f "delims=" %%i in ('dir /b /o-d data\best-practices\best-practices_*.json 2^>nul') do (
    set LATEST_FILE=data\best-practices\%%i
    goto :embed
)

echo [ERROR] No scraped data found!
pause
exit /b 1

:embed
echo Found file: %LATEST_FILE%
echo.
python scripts\embed-best-practices.py "%LATEST_FILE%"
if errorlevel 1 (
    echo.
    echo [ERROR] Embedding failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo [SUCCESS] Best practices pipeline complete!
echo ============================================
echo.
pause
