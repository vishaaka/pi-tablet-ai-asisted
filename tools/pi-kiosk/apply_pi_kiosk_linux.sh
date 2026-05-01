#!/bin/sh
set -eu

ROOT_DIR=""
STAGING_DIR=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --root)
            ROOT_DIR="$2"
            shift 2
            ;;
        --staging)
            STAGING_DIR="$2"
            shift 2
            ;;
        *)
            echo "Bilinmeyen parametre: $1" >&2
            exit 1
            ;;
    esac
done

if [ -z "$ROOT_DIR" ] || [ -z "$STAGING_DIR" ]; then
    echo "Kullanim: $0 --root /mnt/pi-root --staging /tmp/pi-kiosk-staging" >&2
    exit 1
fi

mkdir -p \
    "$ROOT_DIR/etc/pitablet" \
    "$ROOT_DIR/usr/local/bin" \
    "$ROOT_DIR/opt/pitablet/kiosk" \
    "$ROOT_DIR/opt/pitablet" \
    "$ROOT_DIR/etc/systemd/system" \
    "$ROOT_DIR/etc/systemd/system/multi-user.target.wants" \
    "$ROOT_DIR/home/pi/.config/labwc"

cp "$STAGING_DIR/kiosk.env" "$ROOT_DIR/etc/pitablet/kiosk.env"
cp "$STAGING_DIR/ayda-web.env" "$ROOT_DIR/etc/pitablet/ayda-web.env"
cp "$STAGING_DIR/labwc-autostart" "$ROOT_DIR/home/pi/.config/labwc/autostart"
cp "$STAGING_DIR/pitablet-kiosk-launcher.sh" "$ROOT_DIR/usr/local/bin/pitablet-kiosk-launcher.sh"
cp "$STAGING_DIR/pitablet-install-runtime.sh" "$ROOT_DIR/usr/local/bin/pitablet-install-runtime.sh"
cp "$STAGING_DIR/kiosk-home.html" "$ROOT_DIR/opt/pitablet/kiosk/home.html"
cp "$STAGING_DIR/ayda-web.service" "$ROOT_DIR/etc/systemd/system/ayda-web.service"

rm -rf "$ROOT_DIR/opt/pitablet/pi-side"
cp -R "$STAGING_DIR/pi-side" "$ROOT_DIR/opt/pitablet/pi-side"

chmod 644 \
    "$ROOT_DIR/etc/pitablet/kiosk.env" \
    "$ROOT_DIR/etc/pitablet/ayda-web.env" \
    "$ROOT_DIR/home/pi/.config/labwc/autostart" \
    "$ROOT_DIR/opt/pitablet/kiosk/home.html" \
    "$ROOT_DIR/etc/systemd/system/ayda-web.service"
chmod 755 \
    "$ROOT_DIR/usr/local/bin/pitablet-kiosk-launcher.sh" \
    "$ROOT_DIR/usr/local/bin/pitablet-install-runtime.sh"

chown -R 1000:1000 \
    "$ROOT_DIR/home/pi/.config" \
    "$ROOT_DIR/opt/pitablet"

python3 - "$ROOT_DIR" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
lightdm = root / "etc/lightdm/lightdm.conf"
if lightdm.exists():
    text = lightdm.read_text(encoding="utf-8")
    text = text.replace("autologin-user=rpi-first-boot-wizard", "autologin-user=pi")
    lightdm.write_text(text, encoding="utf-8")
PY

mkdir -p "$ROOT_DIR/etc/systemd/system/getty@tty1.service.d"
cat > "$ROOT_DIR/etc/systemd/system/getty@tty1.service.d/autologin.conf" <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
EOF

ln -sf ../ayda-web.service "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/ayda-web.service"

for link in \
  "$ROOT_DIR/etc/systemd/system/cloud-init.target.wants/cloud-init-network.service" \
  "$ROOT_DIR/etc/systemd/system/cloud-init.target.wants/cloud-config.service" \
  "$ROOT_DIR/etc/systemd/system/cloud-init.target.wants/cloud-init-main.service" \
  "$ROOT_DIR/etc/systemd/system/cloud-init.target.wants/cloud-final.service" \
  "$ROOT_DIR/etc/systemd/system/cloud-init.target.wants/cloud-init-local.service" \
  "$ROOT_DIR/etc/systemd/system/cloud-config.target.wants/cloud-init-hotplugd.socket" \
  "$ROOT_DIR/etc/systemd/system/network-online.target.wants/NetworkManager-wait-online.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/nfs-client.target" \
  "$ROOT_DIR/etc/systemd/system/nfs-client.target.wants/nfs-blkmap.service" \
  "$ROOT_DIR/etc/systemd/system/remote-fs.target.wants/nfs-client.target" \
  "$ROOT_DIR/etc/systemd/system/dbus-org.freedesktop.ModemManager1.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/ModemManager.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/avahi-daemon.service" \
  "$ROOT_DIR/etc/systemd/system/sockets.target.wants/avahi-daemon.socket" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/cups-browsed.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/cups.path" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/cups.service" \
  "$ROOT_DIR/etc/systemd/system/printer.target.wants/cups.service" \
  "$ROOT_DIR/etc/systemd/system/sockets.target.wants/cups.socket" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/rpcbind.service" \
  "$ROOT_DIR/etc/systemd/system/sockets.target.wants/rpcbind.socket" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/glamor-test.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/rp1-test.service" \
  "$ROOT_DIR/etc/systemd/system/multi-user.target.wants/userconfig.service" \
  "$ROOT_DIR/etc/systemd/system/bluetooth.target.wants/bluetooth.service" \
  "$ROOT_DIR/etc/systemd/system/graphical.target.wants/udisks2.service" \
  "$ROOT_DIR/etc/systemd/system/graphical.target.wants/accounts-daemon.service"
do
  rm -f "$link"
done

sync
echo "Pi kiosk ve AYDA web entegrasyonu rootfs icine yazildi: $ROOT_DIR"
