@echo off
cd /d "%~dp0"
netstat -ano | findstr ":8765" | findstr "LISTENING" >nul
if errorlevel 1 start "Сайт команды 7" /MIN python -m http.server 8765
ping -n 2 127.0.0.1 >nul
start "" "http://127.0.0.1:8765/demo.html"
