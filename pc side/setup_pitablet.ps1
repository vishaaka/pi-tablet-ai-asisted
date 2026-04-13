param(
    [string]$TargetDir,
    [switch]$SkipBackup,
    [switch]$InstallRequirements
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SettingsPath = Join-Path $ScriptDir "config\settings.json"
$Settings = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json

$PackageName = [string]$Settings.deployment.package_name
if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    $TargetDir = [string]$Settings.deployment.target_dir
}
$BackupRoot = [string]$Settings.deployment.backup_root
$ExcludeDirs = @($Settings.deployment.exclude_dirs)
$ExcludeFiles = @($Settings.deployment.exclude_files)

function Invoke-Robocopy {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludeDirPaths = @(),
        [string[]]$ExcludeFiles = @()
    )

    $args = @(
        $Source,
        $Destination,
        "/MIR",
        "/R:1",
        "/W:1",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS"
    )

    if ($ExcludeDirPaths.Count -gt 0) {
        $args += "/XD"
        $args += $ExcludeDirPaths
    }

    if ($ExcludeFiles.Count -gt 0) {
        $args += "/XF"
        $args += $ExcludeFiles
    }

    & robocopy @args | Out-Host
    if ($LASTEXITCODE -gt 7) {
        throw "Robocopy failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Deploy package: $PackageName"
Write-Host "Source: $ScriptDir"
Write-Host "Target: $TargetDir"

$TargetManage = Join-Path $TargetDir "manage_servers.bat"
if (Test-Path -LiteralPath $TargetManage) {
    Write-Host "Stopping existing target services..."
    & $TargetManage stop all_safe | Out-Host
}

if ((Test-Path -LiteralPath $TargetDir) -and -not $SkipBackup) {
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupDir = Join-Path $BackupRoot $Stamp
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

    $TargetExcludePaths = @()
    foreach ($name in $ExcludeDirs) {
        $TargetExcludePaths += (Join-Path $TargetDir $name)
    }

    Write-Host "Creating backup: $BackupDir"
    Invoke-Robocopy -Source $TargetDir -Destination $BackupDir -ExcludeDirPaths $TargetExcludePaths -ExcludeFiles $ExcludeFiles
}

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

$SourceExcludePaths = @()
foreach ($name in $ExcludeDirs) {
    $SourceExcludePaths += (Join-Path $ScriptDir $name)
}

Write-Host "Syncing workspace package to target..."
Invoke-Robocopy -Source $ScriptDir -Destination $TargetDir -ExcludeDirPaths $SourceExcludePaths -ExcludeFiles $ExcludeFiles

if ($InstallRequirements) {
    $RequirementsPath = Join-Path $TargetDir "requirements.txt"
    if (Test-Path -LiteralPath $RequirementsPath) {
        Write-Host "Installing Python requirements..."
        python -m pip install -r $RequirementsPath
        if ($LASTEXITCODE -ne 0) {
            throw "pip install failed with exit code $LASTEXITCODE"
        }
    }
}

Write-Host ""
Write-Host "Deployment completed."
Write-Host "Package name : $PackageName"
Write-Host "Live folder   : $TargetDir"
Write-Host "Backups       : $BackupRoot"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. $TargetDir\baslat.bat"
Write-Host "  2. or $TargetDir\manage_servers.bat start all"
