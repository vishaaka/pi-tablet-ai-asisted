@echo off
setlocal enabledelayedexpansion

cd /d C:\pitablet

set PANEL_PORT=9100
set TOOL_PORT=8000
set MIDDLEWARE_PORT=7000
set DASHBOARD_PORT=9000

if "%~1"=="" goto :usage

if /I "%~1"=="start" (
    if /I "%~2"=="panel" goto :start_panel
    if /I "%~2"=="tool" goto :start_tool
    if /I "%~2"=="middleware" goto :start_middleware
    if /I "%~2"=="dashboard" goto :start_dashboard
    if /I "%~2"=="all" goto :start_all
    goto :usage
)

if /I "%~1"=="stop" (
    if /I "%~2"=="panel" goto :stop_panel
    if /I "%~2"=="tool" goto :stop_tool
    if /I "%~2"=="middleware" goto :stop_middleware
    if /I "%~2"=="dashboard" goto :stop_dashboard
    if /I "%~2"=="all" goto :stop_all
    if /I "%~2"=="all_safe" goto :stop_all_safe
    goto :usage
)

if /I "%~1"=="status" goto :status_all

goto :usage


:start_all
call :start_service panel %PANEL_PORT% "python -m uvicorn parent_panel:app --port %PANEL_PORT%"
call :start_service tool %TOOL_PORT% "python -m uvicorn app:app --port %TOOL_PORT%"
call :start_service middleware %MIDDLEWARE_PORT% "python -m uvicorn middleware:app --port %MIDDLEWARE_PORT%"
call :start_service dashboard %DASHBOARD_PORT% "python -m uvicorn dashboard:app --port %DASHBOARD_PORT%"
goto :eof

:start_panel
call :start_service panel %PANEL_PORT% "python -m uvicorn parent_panel:app --port %PANEL_PORT%"
goto :eof

:start_tool
call :start_service tool %TOOL_PORT% "python -m uvicorn app:app --port %TOOL_PORT%"
goto :eof

:start_middleware
call :start_service middleware %MIDDLEWARE_PORT% "python -m uvicorn middleware:app --port %MIDDLEWARE_PORT%"
goto :eof

:start_dashboard
call :start_service dashboard %DASHBOARD_PORT% "python -m uvicorn dashboard:app --port %DASHBOARD_PORT%"
goto :eof


:stop_all
call :stop_service tool %TOOL_PORT%
call :stop_service middleware %MIDDLEWARE_PORT%
call :stop_service dashboard %DASHBOARD_PORT%
call :stop_service panel %PANEL_PORT%
goto :eof

:stop_all_safe
call :stop_service tool %TOOL_PORT%
call :stop_service middleware %MIDDLEWARE_PORT%
call :stop_service dashboard %DASHBOARD_PORT%
goto :eof

:stop_panel
call :stop_service panel %PANEL_PORT%
goto :eof

:stop_tool
call :stop_service tool %TOOL_PORT%
goto :eof

:stop_middleware
call :stop_service middleware %MIDDLEWARE_PORT%
goto :eof

:stop_dashboard
call :stop_service dashboard %DASHBOARD_PORT%
goto :eof


:status_all
call :status_service panel %PANEL_PORT%
call :status_service tool %TOOL_PORT%
call :status_service middleware %MIDDLEWARE_PORT%
call :status_service dashboard %DASHBOARD_PORT%
goto :eof


:start_service
set SERVICE_NAME=%~1
set SERVICE_PORT=%~2
set SERVICE_CMD=%~3

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%SERVICE_PORT% ^| findstr LISTENING') do (
    echo %SERVICE_NAME% already running on port %SERVICE_PORT%
    goto :eof
)

echo Starting %SERVICE_NAME% on port %SERVICE_PORT%...
start "%SERVICE_NAME%" cmd /k "cd /d C:\pitablet && %SERVICE_CMD%"
timeout /t 2 >nul
echo %SERVICE_NAME% started
goto :eof


:stop_service
set SERVICE_NAME=%~1
set SERVICE_PORT=%~2
set FOUND_PID=

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%SERVICE_PORT% ^| findstr LISTENING') do (
    set FOUND_PID=%%a
)

if not defined FOUND_PID (
    echo %SERVICE_NAME% is not running
    goto :eof
)

echo Stopping %SERVICE_NAME% PID !FOUND_PID! ...
taskkill /PID !FOUND_PID! /F >nul 2>nul
echo %SERVICE_NAME% stopped
goto :eof


:status_service
set SERVICE_NAME=%~1
set SERVICE_PORT=%~2
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%SERVICE_PORT% ^| findstr LISTENING') do (
    echo %SERVICE_NAME%=running
    goto :eof
)
echo %SERVICE_NAME%=stopped
goto :eof


:usage
echo Usage:
echo   manage_servers.bat start panel
echo   manage_servers.bat start tool
echo   manage_servers.bat start middleware
echo   manage_servers.bat start dashboard
echo   manage_servers.bat start all
echo   manage_servers.bat stop panel
echo   manage_servers.bat stop tool
echo   manage_servers.bat stop middleware
echo   manage_servers.bat stop dashboard
echo   manage_servers.bat stop all
echo   manage_servers.bat stop all_safe
echo   manage_servers.bat status
exit /b 1