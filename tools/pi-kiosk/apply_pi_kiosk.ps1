param(
    [string]$VhdPath = "C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx",
    [string]$Distro = "Ubuntu"
)

$ErrorActionPreference = "Stop"

$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$stagingDir = "C:\pitablet_virtual_sd\pi-kiosk-staging"
$wslRoot = "/root/pi-root"
$wslBoot = "/root/pi-boot"

New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
Copy-Item (Join-Path $toolDir "kiosk.env") (Join-Path $stagingDir "kiosk.env") -Force
Copy-Item (Join-Path $toolDir "labwc-autostart") (Join-Path $stagingDir "labwc-autostart") -Force
Copy-Item (Join-Path $toolDir "pitablet-kiosk-launcher.sh") (Join-Path $stagingDir "pitablet-kiosk-launcher.sh") -Force
Copy-Item (Join-Path $toolDir "kiosk-home.html") (Join-Path $stagingDir "kiosk-home.html") -Force

$stagingWsl = "/mnt/" + $stagingDir.Substring(0,1).ToLower() + $stagingDir.Substring(2).Replace("\","/")
$applyShPath = Join-Path $stagingDir "apply-kiosk.sh"
$runnerLog = "C:\pitablet_virtual_sd\pi-kiosk-run.log"

wsl --shutdown | Out-Null

$mountScript = @'
set -eu
mkdir -p /root/pi-root /root/pi-boot
mountpoint -q /root/pi-root || mount -o rw /dev/sdd2 /root/pi-root
mountpoint -q /root/pi-boot || mount -o rw /dev/sdd1 /root/pi-boot
mkdir -p /root/pi-root/etc/pitablet /root/pi-root/usr/local/bin /root/pi-root/opt/pitablet/kiosk /root/pi-root/home/pi/.config/labwc
cp __STAGING__/kiosk.env /root/pi-root/etc/pitablet/kiosk.env
cp __STAGING__/labwc-autostart /root/pi-root/home/pi/.config/labwc/autostart
cp __STAGING__/pitablet-kiosk-launcher.sh /root/pi-root/usr/local/bin/pitablet-kiosk-launcher.sh
cp __STAGING__/kiosk-home.html /root/pi-root/opt/pitablet/kiosk/home.html
chmod 644 /root/pi-root/etc/pitablet/kiosk.env /root/pi-root/home/pi/.config/labwc/autostart /root/pi-root/opt/pitablet/kiosk/home.html
chmod 755 /root/pi-root/usr/local/bin/pitablet-kiosk-launcher.sh
chown -R 1000:1000 /root/pi-root/home/pi/.config /root/pi-root/opt/pitablet
python3 - <<'PY'
from pathlib import Path
lightdm = Path('/root/pi-root/etc/lightdm/lightdm.conf')
text = lightdm.read_text(encoding='utf-8')
text = text.replace('autologin-user=rpi-first-boot-wizard', 'autologin-user=pi')
lightdm.write_text(text, encoding='utf-8')
PY
cat > /root/pi-root/etc/systemd/system/getty@tty1.service.d/autologin.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
EOF
for link in \
  /root/pi-root/etc/systemd/system/cloud-init.target.wants/cloud-init-network.service \
  /root/pi-root/etc/systemd/system/cloud-init.target.wants/cloud-config.service \
  /root/pi-root/etc/systemd/system/cloud-init.target.wants/cloud-init-main.service \
  /root/pi-root/etc/systemd/system/cloud-init.target.wants/cloud-final.service \
  /root/pi-root/etc/systemd/system/cloud-init.target.wants/cloud-init-local.service \
  /root/pi-root/etc/systemd/system/cloud-config.target.wants/cloud-init-hotplugd.socket \
  /root/pi-root/etc/systemd/system/network-online.target.wants/NetworkManager-wait-online.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/nfs-client.target \
  /root/pi-root/etc/systemd/system/nfs-client.target.wants/nfs-blkmap.service \
  /root/pi-root/etc/systemd/system/remote-fs.target.wants/nfs-client.target \
  /root/pi-root/etc/systemd/system/dbus-org.freedesktop.ModemManager1.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/ModemManager.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/avahi-daemon.service \
  /root/pi-root/etc/systemd/system/sockets.target.wants/avahi-daemon.socket \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/cups-browsed.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/cups.path \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/cups.service \
  /root/pi-root/etc/systemd/system/printer.target.wants/cups.service \
  /root/pi-root/etc/systemd/system/sockets.target.wants/cups.socket \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/rpcbind.service \
  /root/pi-root/etc/systemd/system/sockets.target.wants/rpcbind.socket \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/glamor-test.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/rp1-test.service \
  /root/pi-root/etc/systemd/system/multi-user.target.wants/userconfig.service \
  /root/pi-root/etc/systemd/system/bluetooth.target.wants/bluetooth.service \
  /root/pi-root/etc/systemd/system/graphical.target.wants/udisks2.service \
  /root/pi-root/etc/systemd/system/graphical.target.wants/accounts-daemon.service
do
  rm -f "$link"
done
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
