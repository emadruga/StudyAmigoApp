#!/bin/bash
# =============================================================================
# StudyAmigo - Install Backup Cron on a Running EC2 Instance
# =============================================================================
# Run this ONCE from your Mac after:
#   1. terraform apply  (creates the S3 bucket + attaches IAM instance profile)
#   2. The EC2 instance is running
#
# Usage:
#   chmod +x server/tools/install_backup_cron.sh
#   ./server/tools/install_backup_cron.sh <BUCKET_NAME>
#
# Example:
#   ./server/tools/install_backup_cron.sh study-amigo-backups-123456789012
#
# The bucket name is shown in terraform output:
#   cd server/aws_terraform && terraform output backup_bucket
# =============================================================================

set -euo pipefail

# --- Args --------------------------------------------------------------------
EC2_HOST="${EC2_HOST:-54.152.109.26}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/study-amigo-aws}"
SSH_USER="${SSH_USER:-ubuntu}"
BUCKET="${1:-}"

if [[ -z "$BUCKET" ]]; then
  echo "Usage: $0 <BUCKET_NAME>"
  echo "       EC2_HOST=<ip>   (default: 54.152.109.26)"
  echo "       SSH_KEY=<path>  (default: ~/.ssh/study-amigo-aws)"
  echo ""
  echo "Get bucket name: cd server/aws_terraform && terraform output backup_bucket"
  exit 1
fi

SSH_OPTS="-i ${SSH_KEY} -o StrictHostKeyChecking=no -o ConnectTimeout=10"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing backup system on ${EC2_USER:-ubuntu}@${EC2_HOST}"
echo "    Bucket : ${BUCKET}"

# --- Upload backup.sh --------------------------------------------------------
echo "[1/4] Uploading backup.sh..."
scp $SSH_OPTS \
  "${SCRIPT_DIR}/backup.sh" \
  "${SSH_USER}@${EC2_HOST}:/tmp/backup.sh"

# --- Install on EC2 ----------------------------------------------------------
echo "[2/4] Installing to /opt/studyamigo-backup/..."
ssh $SSH_OPTS "${SSH_USER}@${EC2_HOST}" bash <<EOF
set -euo pipefail

# Install destination
sudo mkdir -p /opt/studyamigo-backup
sudo cp /tmp/backup.sh /opt/studyamigo-backup/backup.sh
sudo chmod 750 /opt/studyamigo-backup/backup.sh
sudo chown root:ubuntu /opt/studyamigo-backup/backup.sh

# Write environment file (bucket name injected here)
sudo tee /opt/studyamigo-backup/env > /dev/null <<ENVEOF
STUDYAMIGO_BACKUP_BUCKET=${BUCKET}
ENVEOF
sudo chmod 640 /opt/studyamigo-backup/env
sudo chown root:ubuntu /opt/studyamigo-backup/env

# Ensure log file exists and is writable by ubuntu
sudo touch /var/log/studyamigo-backup.log
sudo chown ubuntu:ubuntu /var/log/studyamigo-backup.log

echo "  Files installed OK"
EOF

# --- Install cron job --------------------------------------------------------
echo "[3/4] Installing cron job (daily 06:00 UTC = 03:00 BRT)..."
ssh $SSH_OPTS "${SSH_USER}@${EC2_HOST}" bash <<'EOF'
set -euo pipefail

# The cron wrapper sources the env file then calls backup.sh
sudo tee /opt/studyamigo-backup/run.sh > /dev/null <<'RUNEOF'
#!/bin/bash
# Sourced by cron — loads env vars then runs backup
set -euo pipefail
source /opt/studyamigo-backup/env
exec /opt/studyamigo-backup/backup.sh
RUNEOF
sudo chmod 750 /opt/studyamigo-backup/run.sh
sudo chown root:ubuntu /opt/studyamigo-backup/run.sh

# Install cron for ubuntu user
CRON_LINE="0 6 * * * /opt/studyamigo-backup/run.sh >> /var/log/studyamigo-backup.log 2>&1"
# Remove any existing studyamigo-backup cron entry then re-add
(crontab -l 2>/dev/null | grep -v 'studyamigo-backup' || true
 echo "$CRON_LINE") | crontab -

echo "  Cron installed:"
crontab -l | grep studyamigo-backup
EOF

# --- Smoke test (dry-run via env check) --------------------------------------
echo "[4/4] Smoke-testing — checking AWS credentials via instance profile..."
ssh $SSH_OPTS "${SSH_USER}@${EC2_HOST}" bash <<EOF
set -euo pipefail
CALLER=\$(aws sts get-caller-identity --output text --query 'Arn' 2>&1 || true)
if echo "\$CALLER" | grep -q 'arn:aws'; then
  echo "  IAM instance profile OK: \$CALLER"
else
  echo "  WARNING: Could not verify IAM credentials: \$CALLER"
  echo "  The instance profile may not be attached yet."
  echo "  Run: terraform apply  then wait ~30 s and retry."
fi
EOF

echo ""
echo "==> Done. Backup will run daily at 06:00 UTC (03:00 BRT)."
echo ""
echo "    Verify first backup after tomorrow morning:"
echo "    ssh -i ${SSH_KEY} ${SSH_USER}@${EC2_HOST} 'tail -50 /var/log/studyamigo-backup.log'"
echo ""
echo "    Or trigger a manual test run right now:"
echo "    ssh -i ${SSH_KEY} ${SSH_USER}@${EC2_HOST} 'source /opt/studyamigo-backup/env && /opt/studyamigo-backup/backup.sh'"
