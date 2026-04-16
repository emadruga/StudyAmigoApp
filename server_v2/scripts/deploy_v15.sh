#!/usr/bin/env bash
# =============================================================================
# deploy_v15.sh — SAv1.5 deploy script
#
# Runs on the EC2 host (ubuntu@54.152.109.26).
# Executes the full 13-step cutover from SAv1.0 to SAv1.5.
#
# Prerequisites (before running this script):
#   1. admin.db already migrated locally (add_email_to_admin_db.py ran OK)
#   2. Create staging dir and upload migrated admin.db to EC2:
#        ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 "sudo mkdir -p /opt/study-amigo-v15/server"
#        scp -i ~/.ssh/study-amigo-aws ~/.cache/studyamigo/20260415/admin.db \
#            ubuntu@54.152.109.26:/opt/study-amigo-v15/server/admin.db
#   3. Upload this script to EC2:
#        scp -i ~/.ssh/study-amigo-aws server_v2/scripts/deploy_v15.sh \
#            ubuntu@54.152.109.26:~/deploy_v15.sh
#
# Usage (on the EC2 host):
#   chmod +x ~/deploy_v15.sh
#   ~/deploy_v15.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
V10_DIR="/opt/study-amigo"
V15_DIR="/opt/study-amigo-v15"
GIT_REPO="https://github.com/emadruga/StudyAmigoApp.git"
NGINX_CONF="/etc/nginx/sites-available/study-amigo"
MIGRATED_DB="$V15_DIR/server/admin.db"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

info()    { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
abort()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---------------------------------------------------------------------------
# Step 0: Sanity checks
# ---------------------------------------------------------------------------
info "Step 0: Sanity checks"

[[ -d "$V10_DIR" ]]       || abort "SAv1.0 directory not found: $V10_DIR"
[[ -f "$MIGRATED_DB" ]]   || abort "Migrated DB not found: $MIGRATED_DB — upload it first (see script header)"

# ---------------------------------------------------------------------------
# Step 1: Install Nginx on host (idempotent)
# ---------------------------------------------------------------------------
info "Step 1: Install Nginx on EC2 host"
if ! command -v nginx &>/dev/null; then
    sudo apt-get update -q
    sudo apt-get install -y nginx
else
    info "  Nginx already installed — skipping"
fi

# ---------------------------------------------------------------------------
# Step 2: Stop SAv1.0, remap port 80→8081, restart
# ---------------------------------------------------------------------------
info "Step 2: Reconfigure SAv1.0 to port 8081"

COMPOSE_V10="$V10_DIR/docker-compose.yml"

# Stop current stack (frees host port 80)
cd "$V10_DIR"
sudo docker compose down

# Rewrite client port mapping 80:80 → 8081:80 (idempotent)
if grep -q '"8081:80"' "$COMPOSE_V10"; then
    info "  Port already set to 8081 — skipping sed"
else
    sudo sed -i 's|"80:80"|"8081:80"|g' "$COMPOSE_V10"
    info "  Port mapping updated to 8081:80"
fi

sudo docker compose up -d
info "  SAv1.0 containers started on port 8081"

# ---------------------------------------------------------------------------
# Step 3: Configure Nginx host (write config + enable)
# ---------------------------------------------------------------------------
info "Step 3: Write Nginx host config"

sudo tee "$NGINX_CONF" > /dev/null <<'NGINX'
# SAv1.5 — domínio principal
server {
    listen 80;
    server_name study-amigo.app www.study-amigo.app;

    location / {
        proxy_pass         http://127.0.0.1:8082;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}

# SAv1.0 — domínio legado (read-only de emergência)
server {
    listen 80;
    server_name antigo.study-amigo.app;

    location / {
        proxy_pass         http://127.0.0.1:8081;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
NGINX

# Enable site (idempotent)
ENABLED="/etc/nginx/sites-enabled/study-amigo"
if [[ ! -L "$ENABLED" ]]; then
    sudo ln -s "$NGINX_CONF" "$ENABLED"
fi

# Remove default site if present (conflicts with our catch-all)
[[ -f /etc/nginx/sites-enabled/default ]] && sudo rm /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx
info "  Nginx configured and reloaded"

# ---------------------------------------------------------------------------
# Step 4: Verify SAv1.0 is reachable via antigo.study-amigo.app (local curl)
# ---------------------------------------------------------------------------
info "Step 4: Verify SAv1.0 via localhost:8081"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/ || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    info "  SAv1.0 health check OK (HTTP 200)"
else
    warn "  SAv1.0 returned HTTP $HTTP_CODE — check docker logs v10_client"
fi

# ---------------------------------------------------------------------------
# Step 5: Clone SAv1.5 repo
# ---------------------------------------------------------------------------
info "Step 5: Clone SAv1.5 repo to $V15_DIR"
if [[ -d "$V15_DIR" ]]; then
    warn "  $V15_DIR already exists — pulling latest instead"
    cd "$V15_DIR"
    sudo git pull origin main
else
    sudo git clone "$GIT_REPO" "$V15_DIR"
fi

# ---------------------------------------------------------------------------
# Step 6: Copy migrated admin.db and user_dbs
# ---------------------------------------------------------------------------
info "Step 6: Copy databases to SAv1.5"

# admin.db was already uploaded to $V15_DIR/server/admin.db before running this script
info "  admin.db already in place at $MIGRATED_DB"

# user_dbs: copy from SAv1.0 (snapshot at deploy time)
if [[ -d "$V10_DIR/server/user_dbs" ]]; then
    sudo cp -r "$V10_DIR/server/user_dbs" "$V15_DIR/server/user_dbs"
    COUNT=$(find "$V15_DIR/server/user_dbs" -name "*.anki2" | wc -l)
    info "  user_dbs copied ($COUNT .anki2 files)"
else
    warn "  $V10_DIR/server/user_dbs not found — skipping user_dbs copy"
fi

# ---------------------------------------------------------------------------
# Step 7: Create .env for SAv1.5
# ---------------------------------------------------------------------------
info "Step 7: Create .env for SAv1.5"

ENV_FILE="$V15_DIR/server/.env"
if [[ -f "$ENV_FILE" ]]; then
    warn "  .env already exists — skipping (edit manually if needed)"
else
    # Read SECRET_KEY from SAv1.0 to reuse it
    V10_SECRET=$(grep SECRET_KEY "$V10_DIR/server/.env" | cut -d= -f2-)

    sudo tee "$ENV_FILE" > /dev/null <<EOF
SECRET_KEY=${V10_SECRET}
FLASK_ENV=production
SES_SENDER_EMAIL=noreply@metads.app
SES_AWS_REGION=us-east-1
APP_BASE_URL=https://study-amigo.app
STUDYAMIGO_BACKUP_BUCKET=study-amigo-backups-645069181643
APP_DIR=/app
DB_DIR=/app
BACKUP_PREFIX=backups/v15
EOF
    info "  .env created"
fi

# ---------------------------------------------------------------------------
# Step 8: Write docker-compose.yml for SAv1.5
# ---------------------------------------------------------------------------
info "Step 8: Write docker-compose.yml for SAv1.5"

sudo tee "$V15_DIR/docker-compose.yml" > /dev/null <<'COMPOSE'
services:
  server:
    container_name: v15_server
    build: ./server
    restart: unless-stopped
    expose:
      - "8000"
    volumes:
      - ./server:/app
    env_file:
      - ./server/.env
    networks:
      - v15-net

  client:
    container_name: v15_client
    build: ./client
    restart: unless-stopped
    ports:
      - "8082:80"
    depends_on:
      - server
    networks:
      - v15-net

  backup:
    image: amazon/aws-cli:latest
    container_name: v15_backup
    entrypoint: ["/bin/bash"]
    command: ["/app/server_v2/tools/backup_container.sh"]
    volumes:
      - ./server:/app:ro
      - ./server_v2/tools:/app/server_v2/tools:ro
    environment:
      - PROJECT_NAME=study-amigo
      - BACKUP_PREFIX=backups/v15
    restart: unless-stopped
    networks:
      - v15-net

networks:
  v15-net:
    driver: bridge
COMPOSE

info "  docker-compose.yml written"

# Ensure backup scripts are executable (git does not always preserve +x on clone)
sudo chmod +x "$V15_DIR/server/tools/backup.sh"
sudo chmod +x "$V15_DIR/server_v2/tools/backup_container.sh"

# ---------------------------------------------------------------------------
# Step 9: Build and start SAv1.5 containers (sequential to avoid OOM)
# ---------------------------------------------------------------------------
info "Step 9: Build and start SAv1.5 containers (sequential to avoid OOM)"
cd "$V15_DIR"
sudo docker compose build server
sudo docker compose build client
sudo docker compose build backup
sudo docker compose up -d
info "  SAv1.5 containers started"

# ---------------------------------------------------------------------------
# Step 10: Verify SAv1.5 is reachable
# ---------------------------------------------------------------------------
info "Step 10: Verify SAv1.5 via localhost:8082"
sleep 5  # give gunicorn a moment to boot
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/ || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    info "  SAv1.5 health check OK (HTTP 200)"
else
    warn "  SAv1.5 returned HTTP $HTTP_CODE — check: sudo docker compose -f $V15_DIR/docker-compose.yml logs server"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deploy SAv1.5 complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Remaining manual steps:"
echo "  1. Add Cloudflare DNS record:"
echo "       Type: A  Name: antigo  Content: 54.152.109.26  Proxied: yes"
echo "  2. Test study-amigo.app (email login)"
echo "  3. Test antigo.study-amigo.app (username login, legacy)"
echo ""
echo "Rollback (if needed):"
echo "  sudo sed -i 's|127.0.0.1:8082|127.0.0.1:8081|g' $NGINX_CONF"
echo "  sudo nginx -t && sudo systemctl reload nginx"
