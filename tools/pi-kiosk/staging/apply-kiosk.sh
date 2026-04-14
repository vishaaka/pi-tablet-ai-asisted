set -eu
mkdir -p /root/pi-root /root/pi-boot
mountpoint -q /root/pi-root || mount -o rw /dev/sdd2 /root/pi-root
mountpoint -q /root/pi-boot || mount -o rw /dev/sdd1 /root/pi-boot
mkdir -p /root/pi-root/etc/pitablet /root/pi-root/usr/local/bin /root/pi-root/opt/pitablet/kiosk /root/pi-root/home/pi/.config/labwc
cp /mnt/d/kullanıcı/belgeler/github_repo/pi-tablet-ai-asisted/tools/pi-kiosk/staging/kiosk.env /root/pi-root/etc/pitablet/kiosk.env
cp /mnt/d/kullanıcı/belgeler/github_repo/pi-tablet-ai-asisted/tools/pi-kiosk/staging/labwc-autostart /root/pi-root/home/pi/.config/labwc/autostart
cp /mnt/d/kullanıcı/belgeler/github_repo/pi-tablet-ai-asisted/tools/pi-kiosk/staging/pitablet-kiosk-launcher.sh /root/pi-root/usr/local/bin/pitablet-kiosk-launcher.sh
cp /mnt/d/kullanıcı/belgeler/github_repo/pi-tablet-ai-asisted/tools/pi-kiosk/staging/kiosk-home.html /root/pi-root/opt/pitablet/kiosk/home.html
chmod 644 /root/pi-root/etc/pitablet/kiosk.env /root/pi-root/home/pi/.config/labwc/autostart /root/pi-root/opt/pitablet/kiosk/home.html
chmod 755 /root/pi-root/usr/local/bin/pitablet-kiosk-launcher.sh
chown -R 1000:1000 /root/pi-root/home/pi/.config /root/pi-root/opt/pitablet
sed -i 's/^autologin-user=.*/autologin-user=pi/' /root/pi-root/etc/lightdm/lightdm.conf
sed -i 's#^ExecStart=-/sbin/agetty --autologin .*#ExecStart=-/sbin/agetty --autologin pi --noclear %I \#' /root/pi-root/etc/systemd/system/getty@tty1.service.d/autologin.conf
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
  rm -f "\"
done
sync
