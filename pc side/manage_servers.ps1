param(
    [string]$Action,
    [string]$Target
)

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SettingsPath = Join-Path $BaseDir "config\\settings.json"
$Settings = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json

$Ports = @{
    panel = [int]$Settings.services.panel.port
    tool = [int]$Settings.services.tool.port
    middleware = [int]$Settings.services.middleware.port
    dashboard = [int]$Settings.services.dashboard.port
}

$Commands = @{
    panel      = "python -m uvicorn $($Settings.services.panel.uvicorn_app) --host $($Settings.services.panel.host) --port $($Settings.services.panel.port)"
    tool       = "python -m uvicorn $($Settings.services.tool.uvicorn_app) --host $($Settings.services.tool.host) --port $($Settings.services.tool.port)"
    middleware = "python -m uvicorn $($Settings.services.middleware.uvicorn_app) --host $($Settings.services.middleware.host) --port $($Settings.services.middleware.port)"
    dashboard  = "python -m uvicorn $($Settings.services.dashboard.uvicorn_app) --host $($Settings.services.dashboard.host) --port $($Settings.services.dashboard.port)"
}

function Get-PortPids {
    param([int]$Port)

    $pids = @()

    foreach ($line in (netstat -ano -p TCP)) {
        if ($line -match "^\s*TCP\s+\S+:$Port\s+\S+\s+\S+\s+(\d+)\s*$") {
            $foundPid = $matches[1]
            if ($foundPid -match '^\d+$' -and ($pids -notcontains $foundPid)) {
                $pids += $foundPid
            }
        }
    }

    return $pids
}

function Is-PortListening {
    param([int]$Port)
    return (Get-PortPids -Port $Port).Count -gt 0
}

function Start-ServiceByName {
    param([string]$Name)

    if (-not $Ports.ContainsKey($Name)) {
        Write-Host "Unknown service: $Name"
        exit 1
    }

    $port = $Ports[$Name]
    $cmd = $Commands[$Name]

    $existing = Get-PortPids -Port $port
    if ($existing.Count -gt 0) {
        Write-Host "$Name already running on port $port (PID(s): $($existing -join ', '))"
        return
    }

    Write-Host "Starting $Name on port $port ..."
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d $BaseDir && $cmd" -WorkingDirectory $BaseDir

    Start-Sleep -Seconds 4

    $after = Get-PortPids -Port $port
    if ($after.Count -gt 0) {
        Write-Host "$Name started on port $port (PID(s): $($after -join ', '))"
    } else {
        Write-Host "$Name start command ran but port $port is still not listening"
    }
}

function Stop-ServiceByName {
    param([string]$Name)

    if (-not $Ports.ContainsKey($Name)) {
        Write-Host "Unknown service: $Name"
        exit 1
    }

    $port = $Ports[$Name]
    $pids = Get-PortPids -Port $port

    if ($pids.Count -eq 0) {
        Write-Host "$Name is not running"
        return
    }

    Write-Host "Stopping $Name on port $port (PID(s): $($pids -join ', '))"
    foreach ($procId in $pids) {
    try {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    } catch {
    }
}

    Start-Sleep -Seconds 1

    $after = Get-PortPids -Port $port
    if ($after.Count -gt 0) {
        Write-Host "WARNING: $Name still appears to be running on port $port (PID(s): $($after -join ', '))"
    } else {
        Write-Host "$Name stopped"
    }
}

function Show-Status {
    foreach ($name in @('panel','tool','middleware','dashboard')) {
        $port = $Ports[$name]
        if (Is-PortListening -Port $port) {
            $pids = Get-PortPids -Port $port
            Write-Host "${name}=running pid=$($pids -join ',') port=$port"
        } else {
            Write-Host "${name}=stopped port=$port"
        }
    }
}

if ([string]::IsNullOrWhiteSpace($Action)) {
    Write-Host "Usage:"
    Write-Host "  manage_servers.bat start panel"
    Write-Host "  manage_servers.bat start tool"
    Write-Host "  manage_servers.bat start middleware"
    Write-Host "  manage_servers.bat start dashboard"
    Write-Host "  manage_servers.bat start all"
    Write-Host "  manage_servers.bat stop panel"
    Write-Host "  manage_servers.bat stop tool"
    Write-Host "  manage_servers.bat stop middleware"
    Write-Host "  manage_servers.bat stop dashboard"
    Write-Host "  manage_servers.bat stop all"
    Write-Host "  manage_servers.bat stop all_safe"
    Write-Host "  manage_servers.bat status"
    exit 1
}

switch ($Action.ToLower()) {
    "start" {
        switch ($Target.ToLower()) {
            "panel"      { Start-ServiceByName "panel" }
            "tool"       { Start-ServiceByName "tool" }
            "middleware" { Start-ServiceByName "middleware" }
            "dashboard"  { Start-ServiceByName "dashboard" }
            "all" {
                Start-ServiceByName "panel"
                Start-ServiceByName "tool"
                Start-ServiceByName "middleware"
                Start-ServiceByName "dashboard"
            }
            default {
                Write-Host "Unknown start target: $Target"
                exit 1
            }
        }
    }

    "stop" {
        switch ($Target.ToLower()) {
            "panel"      { Stop-ServiceByName "panel" }
            "tool"       { Stop-ServiceByName "tool" }
            "middleware" { Stop-ServiceByName "middleware" }
            "dashboard"  { Stop-ServiceByName "dashboard" }
            "all" {
                Stop-ServiceByName "tool"
                Stop-ServiceByName "middleware"
                Stop-ServiceByName "dashboard"
                Stop-ServiceByName "panel"
            }
            "all_safe" {
                Stop-ServiceByName "tool"
                Stop-ServiceByName "middleware"
                Stop-ServiceByName "dashboard"
            }
            default {
                Write-Host "Unknown stop target: $Target"
                exit 1
            }
        }
    }

    "status" {
        Show-Status
    }

    default {
        Write-Host "Unknown action: $Action"
        exit 1
    }
}
