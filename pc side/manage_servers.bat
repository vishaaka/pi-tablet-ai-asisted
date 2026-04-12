@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\pitablet\manage_servers.ps1" %*
exit /b %ERRORLEVEL%