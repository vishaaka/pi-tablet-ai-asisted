param(
    [string]$VhdPath = "C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx",
    [int]$SizeGB = 110,
    [switch]$Attach
)

$ErrorActionPreference = "Stop"

$artifactDir = Split-Path -Parent $VhdPath
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null

if (Test-Path -LiteralPath $VhdPath) {
    throw "VHDX zaten var: $VhdPath"
}

$sizeMb = [int]($SizeGB * 1024)
$attachLine = if ($Attach) { "attach vdisk" } else { "" }

$scriptLines = @(
    "create vdisk file=""$VhdPath"" maximum=$sizeMb type=expandable"
    "select vdisk file=""$VhdPath"""
)

if ($attachLine) {
    $scriptLines += $attachLine
}

$diskpartScript = Join-Path $env:TEMP "create_virtual_sd_diskpart.txt"
Set-Content -LiteralPath $diskpartScript -Value $scriptLines -Encoding ASCII

try {
    diskpart /s $diskpartScript
} finally {
    Remove-Item -LiteralPath $diskpartScript -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Sanal SD hazirlandi:" -ForegroundColor Green
Write-Host "  $VhdPath"
Write-Host ""
if ($Attach) {
    Write-Host "Disk baglandi. Raspberry Pi Imager ile hedef disk olarak secip kurulum yapabilirsin."
} else {
    Write-Host "Disk henuz baglanmadi. Gerekirse attach_virtual_sd.ps1 ile baglayabilirsin."
}
