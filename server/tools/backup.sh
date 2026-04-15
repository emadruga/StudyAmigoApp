#!/bin/bash
# =============================================================================
# StudyAmigo - Daily Database Backup to S3
# =============================================================================
# Schedule : 3 AM America/Sao_Paulo (= 6 AM UTC, BRT = UTC-3, no DST)
# Cron     : 0 6 * * *
#
# Rotation scheme — 4-week rolling window (28 slots):
#
#   Slot key  : backups/week-{1..4}/{day-of-week}/
#   Cycle     : Advances every Saturday midnight UTC.
#   Reference : Saturday 2026-03-14 00:00:00 UTC (epoch 1741910400).
#
#   Week since reference  │  Slot  │  Overwrites
#   ──────────────────────┼────────┼──────────────────────────────
#   0  (Mar 14 – Mar 20)  │  1     │  (nothing yet)
#   1  (Mar 21 – Mar 27)  │  2     │  (nothing yet)
#   2  (Mar 28 – Apr 03)  │  3     │  (nothing yet)
#   3  (Apr 04 – Apr 10)  │  4     │  (nothing yet)
#   4  (Apr 11 – Apr 17)  │  1     │  week-1 from Mar 14–20
#   5  (Apr 18 – Apr 24)  │  2     │  week-2 from Mar 21–27
#   …
#
# Each slot contains:
#   admin.db.gz        — gzip of admin.db
#   user_dbs.tar.gz    — gzip tar of user_dbs/
#   meta.json          — timestamp, sizes, user-db count
#
# Credentials: IAM instance profile (no access keys needed on EC2).
# Log file   : /var/log/studyamigo-backup.log
# =============================================================================

set -euo pipefail

# --- Configuration -----------------------------------------------------------
APP_DIR="${APP_DIR:-/opt/study-amigo}"
BACKUP_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/studyamigo-backup.log"
BUCKET="${STUDYAMIGO_BACKUP_BUCKET:-}"   # set by install_backup_cron.sh

# Validate bucket
if [[ -z "$BUCKET" ]]; then
  echo "ERROR: STUDYAMIGO_BACKUP_BUCKET environment variable is not set." >&2
  exit 1
fi

# --- Helpers -----------------------------------------------------------------
log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*" | tee -a "$LOG_FILE"
}

# --- 4-Week Slot Calculation -------------------------------------------------
# Reference Saturday: 2026-03-14 00:00:00 UTC
REF_EPOCH=1741910400
NOW_EPOCH=$(date -u +%s)
DAYS_SINCE=$(( (NOW_EPOCH - REF_EPOCH) / 86400 ))
DAYS_SINCE=$(( DAYS_SINCE < 0 ? 0 : DAYS_SINCE ))
WEEK_SLOT=$(( (DAYS_SINCE / 7) % 4 + 1 ))
DOW=$(date -u +%A | tr '[:upper:]' '[:lower:]')   # e.g. "wednesday"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

S3_PREFIX="s3://${BUCKET}/backups/week-${WEEK_SLOT}/${DOW}"

# --- Temp workspace ----------------------------------------------------------
TMP_DIR=$(mktemp -d /tmp/studyamigo-backup-XXXXXX)
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

# --- Start -------------------------------------------------------------------
log "================================================================"
log "StudyAmigo backup starting"
log "  Week slot : ${WEEK_SLOT}/4"
log "  Day       : ${DOW}"
log "  S3 target : ${S3_PREFIX}"
log "================================================================"

# Guard: ensure source files exist
if [[ ! -f "${APP_DIR}/server/admin.db" ]]; then
  log "ERROR: ${APP_DIR}/server/admin.db not found. Aborting."
  exit 1
fi
if [[ ! -d "${APP_DIR}/server/user_dbs" ]]; then
  log "ERROR: ${APP_DIR}/server/user_dbs/ directory not found. Aborting."
  exit 1
fi

# --- Compress admin.db -------------------------------------------------------
log "Compressing admin.db..."
gzip -c "${APP_DIR}/server/admin.db" > "${TMP_DIR}/admin.db.gz"
ADMIN_SIZE=$(du -sh "${TMP_DIR}/admin.db.gz" | cut -f1)
log "  admin.db.gz : ${ADMIN_SIZE}"

# --- Compress user_dbs/ ------------------------------------------------------
log "Compressing user_dbs/..."
USER_DB_COUNT=$(find "${APP_DIR}/server/user_dbs" -name "*.db" | wc -l | tr -d ' ')
tar -czf "${TMP_DIR}/user_dbs.tar.gz" \
    -C "${APP_DIR}/server" \
    user_dbs
UDB_SIZE=$(du -sh "${TMP_DIR}/user_dbs.tar.gz" | cut -f1)
log "  user_dbs.tar.gz : ${UDB_SIZE} (${USER_DB_COUNT} databases)"

# --- Write metadata ----------------------------------------------------------
cat > "${TMP_DIR}/meta.json" <<EOF
{
  "timestamp":                 "${TIMESTAMP}",
  "week_slot":                 ${WEEK_SLOT},
  "day_of_week":               "${DOW}",
  "admin_db_compressed_size":  "${ADMIN_SIZE}",
  "user_dbs_compressed_size":  "${UDB_SIZE}",
  "user_db_count":             ${USER_DB_COUNT},
  "s3_prefix":                 "${S3_PREFIX}",
  "hostname":                  "$(hostname -f)"
}
EOF

# --- Upload to S3 ------------------------------------------------------------
log "Uploading to S3..."
aws s3 cp "${TMP_DIR}/admin.db.gz"     "${S3_PREFIX}/admin.db.gz"     --sse AES256 --only-show-errors
aws s3 cp "${TMP_DIR}/user_dbs.tar.gz" "${S3_PREFIX}/user_dbs.tar.gz" --sse AES256 --only-show-errors
aws s3 cp "${TMP_DIR}/meta.json"       "${S3_PREFIX}/meta.json"                     --only-show-errors

log "================================================================"
log "Backup complete: ${S3_PREFIX}"
log "================================================================"
