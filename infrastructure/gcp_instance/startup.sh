#!/bin/bash
set -euxo pipefail

# Log to both console and file for debugging
exec > >(tee -a /var/log/startup-script.log) 2>&1

apt-get update -y

# Install Docker from Debian repositories
apt-get install -y docker.io

# Enable and start Docker service
systemctl enable docker
systemctl start docker
