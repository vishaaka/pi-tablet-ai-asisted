#!/bin/sh
set -eu

apt-get update
apt-get install -y python3-requests python3-yaml chromium-browser || \
apt-get install -y python3-requests python3-yaml chromium

echo "Pi runtime bagimliliklari kuruldu."
