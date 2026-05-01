param(
    [string]$VhdPath = "C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx",
    [string]$Distro = "Ubuntu"
)

$ErrorActionPreference = "Stop"

$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$stagingDir = "C:\pitablet_virtual_sd\pi-kiosk-staging"
$wslRoot = "/root/pi-root"
$wslBoot = "/root/pi-boot"
$repoRoot = Split-Path -Parent (Split-Path -Parent $toolDir)
$piSideSource = Join-Path $repoRoot "pi-side"

New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
Remove-Item -Recurse -Force (Join-Path $stagingDir "pi-side") -ErrorAction SilentlyContinue
Copy-Item (Join-Path $toolDir "kiosk.env") (Join-Path $stagingDir "kiosk.env") -Force
Copy-Item (Join-Path $toolDir "ayda-web.env") (Join-Path $stagingDir "ayda-web.env") -Force
Copy-Item (Join-Path $toolDir "labwc-autostart") (Join-Path $stagingDir "labwc-autostart") -Force
Copy-Item (Join-Path $toolDir "pitablet-kiosk-launcher.sh") (Join-Path $stagingDir "pitablet-kiosk-launcher.sh") -Force
Copy-Item (Join-Path $toolDir "pitablet-install-runtime.sh") (Join-Path $stagingDir "pitablet-install-runtime.sh") -Force
Copy-Item (Join-Path $toolDir "kiosk-home.html") (Join-Path $stagingDir "kiosk-home.html") -Force
Copy-Item (Join-Path $toolDir "ayda-web.service") (Join-Path $stagingDir "ayda-web.service") -Force
Copy-Item (Join-Path $toolDir "apply_pi_kiosk_linux.sh") (Join-Path $stagingDir "apply_pi_kiosk_linux.sh") -Force
Copy-Item $piSideSource (Join-Path $stagingDir "pi-side") -Recurse -Force

$stagingWsl = "/mnt/" + $stagingDir.Substring(0,1).ToLower() + $stagingDir.Substring(2).Replace("\","/")
$applyShPath = Join-Path $stagingDir "apply-kiosk.sh"
$runnerLog = "C:\pitablet_virtual_sd\pi-kiosk-run.log"

wsl --shutdown | Out-Null

$mountScript = @'
set -eu
mkdir -p /root/pi-root /root/pi-boot
mountpoint -q /root/pi-root || mount -o rw /dev/sdd2 /root/pi-root
mountpoint -q /root/pi-boot || mount -o rw /dev/sdd1 /root/pi-boot
sh __STAGING__/apply_pi_kiosk_linux.sh --root /root/pi-root --staging __STAGING__
sync
'@

$mountScript = $mountScript.Replace('__STAGING__', $stagingWsl)

[System.IO.File]::WriteAllText($applyShPath, ($mountScript -replace "`r?`n", "`n"), [System.Text.UTF8Encoding]::new($false))

$runner = @"
$ErrorActionPreference = 'Stop'
'START ' + (Get-Date -Format o) | Set-Content -Path '$runnerLog' -Encoding utf8
wsl --mount --vhd $VhdPath --bare 2>&1 | Add-Content -Path '$runnerLog'
Start-Sleep -Seconds 3
wsl -d $Distro -u root sh $stagingWsl/apply-kiosk.sh 2>&1 | Add-Content -Path '$runnerLog'
'END' | Add-Content -Path '$runnerLog'
"@

$runnerPath = Join-Path $toolDir "run_apply_pi_kiosk.ps1"
Set-Content -Path $runnerPath -Value $runner -Encoding utf8
Start-Process PowerShell -Verb RunAs -Wait -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File",$runnerPath)
Get-Content -Path $runnerLog
