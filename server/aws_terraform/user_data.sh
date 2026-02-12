#!/bin/bash
# =============================================================================
# StudyAmigo - EC2 Bootstrap Script (user_data)
# =============================================================================
# This script runs automatically on the first boot of the EC2 instance.
# It installs Docker, clones the application, and starts the containers.
#
# Logs: /var/log/cloud-init-output.log
# =============================================================================

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "========================================"
echo "StudyAmigo Bootstrap - Starting"
echo "========================================"

# -----------------------------------------------------------------------------
# 1. System Updates
# -----------------------------------------------------------------------------
echo "[1/7] Updating system packages..."
apt-get update -y
apt-get upgrade -y

# -----------------------------------------------------------------------------
# 2. Install Docker
# -----------------------------------------------------------------------------
echo "[2/7] Installing Docker..."

# Install prerequisites
apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  git

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Compose plugin
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add the ubuntu user to the docker group
usermod -aG docker ubuntu

# Enable Docker to start on boot
systemctl enable docker
systemctl start docker

# -----------------------------------------------------------------------------
# 3. Clone the Repository
# -----------------------------------------------------------------------------
echo "[3/7] Cloning StudyAmigo repository..."

APP_DIR="/opt/study-amigo"
git clone ${git_repo_url} "$APP_DIR"
chown -R ubuntu:ubuntu "$APP_DIR"

# -----------------------------------------------------------------------------
# 4. Configure Flask Secret Key
# -----------------------------------------------------------------------------
echo "[4/7] Configuring Flask environment..."

cat > "$APP_DIR/server/.env" <<'ENVFILE'
SECRET_KEY=${flask_secret_key}
FLASK_ENV=production
ENVFILE

# -----------------------------------------------------------------------------
# 5. Configure Client for Root Path Deployment
# -----------------------------------------------------------------------------
echo "[5/7] Configuring client for production..."

cat > "$APP_DIR/client/.env.production" <<'ENVFILE'
VITE_APP_BASE_PATH=/
VITE_API_BASE_URL=
ENVFILE

# -----------------------------------------------------------------------------
# 6. Update docker-compose.yml for Port 80 and CORS
# -----------------------------------------------------------------------------
echo "[6/7] Updating Docker Compose and CORS configuration..."

# Update docker-compose.yml: change port mapping from 8080:80 to 80:80
sed -i 's/"8080:80"/"80:80"/' "$APP_DIR/docker-compose.yml"

# Update Flask CORS to allow the production domain
# Replace the existing CORS origins list with the production domain
sed -i "s|http://localhost:5173|https://${domain_name}|g" "$APP_DIR/server/app.py"

# Also add http variant for Cloudflare flexible SSL
sed -i "s|https://${domain_name}|https://${domain_name}\", \"http://${domain_name}|g" "$APP_DIR/server/app.py"

# -----------------------------------------------------------------------------
# 7. Build and Start Containers
# -----------------------------------------------------------------------------
echo "[7/7] Building and starting Docker containers..."

cd "$APP_DIR"
docker compose build
docker compose up -d

# Wait for containers to be healthy
sleep 10

echo "========================================"
echo "StudyAmigo Bootstrap - Complete!"
echo "========================================"
echo "Containers status:"
docker compose ps
echo ""
echo "Application should be accessible on port 80"
echo "View logs: docker compose logs -f"
