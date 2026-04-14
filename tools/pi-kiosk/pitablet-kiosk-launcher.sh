#!/bin/sh
set -eu

CONFIG_FILE="/etc/pitablet/kiosk.env"

if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1091
    . "$CONFIG_FILE"
fi

URL="${KIOSK_URL:-file:///opt/pitablet/kiosk/home.html}"
BROWSER="${KIOSK_BROWSER:-/usr/bin/chromium}"
MODE="${KIOSK_MODE:-kiosk}"
EXTRA_FLAGS="${KIOSK_EXTRA_FLAGS:-}"

if [ ! -x "$BROWSER" ]; then
    exit 1
fi

mkdir -p "$HOME/.cache/chromium"
pkill -x wf-panel-pi >/dev/null 2>&1 || true
pkill -x pcmanfm >/dev/null 2>&1 || true
pkill -x chromium >/dev/null 2>&1 || true

sleep 2

BASE_FLAGS="--no-first-run --no-default-browser-check --disable-translate --disable-features=Translate,MediaRouter --disk-cache-dir=$HOME/.cache/chromium --password-store=basic"

if [ "$MODE" = "app" ]; then
    exec "$BROWSER" $BASE_FLAGS $EXTRA_FLAGS --app="$URL"
fi

exec "$BROWSER" $BASE_FLAGS $EXTRA_FLAGS --kiosk "$URL"
