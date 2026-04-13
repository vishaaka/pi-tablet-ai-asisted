@echo off
setlocal

set SCRIPT_DIR=%~dp0

call "%SCRIPT_DIR%manage_servers.bat" start panel
timeout /t 2 >nul
start "" http://127.0.0.1:9100/panel

endlocal
