param(
    [string]$VhdPath = "C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $VhdPath)) {
    throw "VHDX bulunamadi: $VhdPath"
}

$scriptLines = @(
    "select vdisk file=""$VhdPath"""
    "detach vdisk"
)

$diskpartScript = Join-Path $env:TEMP "detach_virtual_sd_diskpart.txt"
Set-Content -LiteralPath $diskpartScript -Value $scriptLines -Encoding ASCII

try {
    diskpart /s $diskpartScript
} finally {
    Remove-Item -LiteralPath $diskpartScript -ErrorAction SilentlyContinue
}

Write-Host "Sanal SD ayrildi: $VhdPath" -ForegroundColor Green
