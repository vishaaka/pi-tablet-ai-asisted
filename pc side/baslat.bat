@echo off
cd /d C:\pitablet
start "Ebeveyn Panel Server" cmd /k "python -m uvicorn parent_panel:app --port 9100"
timeout /t 2 >nul
start "" http://127.0.0.1:9100/panel