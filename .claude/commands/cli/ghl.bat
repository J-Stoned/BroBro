@echo off
REM GHL CLI Launcher for Windows
REM Usage: ghl [command] [input]

cd /d "%~dp0..\..\..\"
python ".claude\commands\cli\ghl-cli.py" %*
