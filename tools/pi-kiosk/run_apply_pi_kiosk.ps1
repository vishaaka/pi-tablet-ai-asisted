Stop = 'Stop'
'START ' + (Get-Date -Format o) | Set-Content -Path 'C:\pitablet_virtual_sd\pi-kiosk-run.log' -Encoding utf8
wsl --mount --vhd C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx --bare 2>&1 | Add-Content -Path 'C:\pitablet_virtual_sd\pi-kiosk-run.log'
Start-Sleep -Seconds 3
wsl -d Ubuntu -u root sh /mnt/c/pitablet_virtual_sd/pi-kiosk-staging/apply-kiosk.sh 2>&1 | Add-Content -Path 'C:\pitablet_virtual_sd\pi-kiosk-run.log'
'END' | Add-Content -Path 'C:\pitablet_virtual_sd\pi-kiosk-run.log'
