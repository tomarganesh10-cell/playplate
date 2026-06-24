#!/usr/bin/env bash
# Provision a fresh Hostinger VPS (Ubuntu 24.04) for Trading Playplate.
# Run as root or with sudo:  bash deploy/setup_vps.sh
set -euo pipefail

echo "==> Updating system packages"
apt-get update -y && apt-get upgrade -y

echo "==> Installing prerequisites"
apt-get install -y ca-certificates curl gnupg ufw git

echo "==> Installing Docker Engine + Compose plugin"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker

echo "==> Configuring firewall (UFW)"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Creating deploy user 'playplate' (docker group)"
if ! id playplate >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash playplate
  usermod -aG docker playplate
fi

echo "==> Enabling automatic security updates"
apt-get install -y unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades || true

echo "==> Done. Next steps:"
echo "    1. su - playplate && git clone <repo> playplate && cd playplate"
echo "    2. cp .env.example .env  &&  edit secrets"
echo "    3. Configure DNS (docs/DNS_CONFIGURATION.md), then: bash deploy/init_ssl.sh"
echo "    4. bash deploy/deploy.sh"
