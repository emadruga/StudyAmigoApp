#!/bin/bash
# =============================================================================
# StudyAmigo - Backup Container Entrypoint
# =============================================================================
# Runs inside the 'backup' docker-compose service (amazon/aws-cli image).
# Mount: ./server → /app  (read-only)
#
# Behaviour:
#   1. Derive the S3 bucket name from the IAM instance profile at runtime —
#      no hardcoded name, no env var required under normal operation.
#   2. If the bucket is not reachable yet (Terraform not applied), log a
#      warning and retry every hour. Never crash.
#   3. Once the bucket is reachable, sleep until the next 06:00 UTC then
#      run the backup. Loop forever.
#
# Schedule : 06:00 UTC daily = 03:00 America/Sao_Paulo (BRT = UTC-3, no DST)
#
# Rotation : 4-week rolling window, 28 slots (week-1..4 x mon..sun).
#            Reference Saturday: 2026-03-14 00:00:00 UTC (epoch 1741910400).
#            Slot advances every Saturday midnight UTC.
#
# Credentials: EC2 IAM instance profile via metadata service (no keys needed).
#              Accessible from Docker containers via 169.254.169.254.
#
# Override for testing:
#   BACKUP_BUCKET_OVERRIDE=my-bucket  — skip account-ID discovery
# =============================================================================

set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-study-amigo}"
APP_DIR="/app"    # bind-mounted from ./server on the host

# ---------------------------------------------------------------------------
log() {
  echo "[backup] $(date -u '+%Y-%m-%d %H:%M:%S UTC') $*"
}

# ---------------------------------------------------------------------------
# Derive bucket name: query account ID from STS, then construct the name
# using the same formula as Terraform: "${project_name}-backups-${account_id}"
# Returns empty string on failure.
# ---------------------------------------------------------------------------
get_bucket() {
  if [[ -n "${BACKUP_BUCKET_OVERRIDE:-}" ]]; then
    echo "$BACKUP_BUCKET_OVERRIDE"
    return
  fi
  local account_id
  account_id=$(aws sts get-caller-identity --query Account --output text 2>/dev/null) || {
    echo ""
    return
  }
  echo "${PROJECT_NAME}-backups-${account_id}"
}

# ---------------------------------------------------------------------------
# Returns 0 if the bucket exists and we have access, 1 otherwise.
# ---------------------------------------------------------------------------
bucket_reachable() {
  aws s3 ls "s3://$1" --max-items 1 > /dev/null 2>&1
}

# ---------------------------------------------------------------------------
# Seconds until the next occurrence of HH:MM UTC (today or tomorrow).
# ---------------------------------------------------------------------------
secs_until_utc() {
  local target_hour="$1" target_min="$2"
  local now today_target
  now=$(date -u +%s)
  today_target=$(date -u -d "today ${target_hour}:$(printf '%02d' "${target_min}"):00" +%s)
  if [[ $now -lt $today_target ]]; then
    echo $(( today_target - now ))
  else
    echo $(( today_target + 86400 - now ))
  fi
}

# ---------------------------------------------------------------------------
# 4-week slot calculation (identical to backup.sh).
# Reference Saturday: 2026-03-14 00:00:00 UTC = epoch 1741910400
# ---------------------------------------------------------------------------
REF_EPOCH=1741910400

week_slot() {
  local now days_since
  now=$(date -u +%s)
  days_since=$(( (now - REF_EPOCH) / 86400 ))
  days_since=$(( days_since < 0 ? 0 : days_since ))
  echo $(( (days_since / 7) % 4 + 1 ))
}

# ---------------------------------------------------------------------------
# Run one backup.
# ---------------------------------------------------------------------------
run_backup() {
  local bucket="$1"
  local slot dow ts s3_prefix tmp

  slot=$(week_slot)
  dow=$(date -u +%A | tr '[:upper:]' '[:lower:]')
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  s3_prefix="s3://${bucket}/backups/week-${slot}/${dow}"

  log "=== Backup starting: week-${slot}/${dow} → ${s3_prefix} ==="

  # Guard — source files must exist
  if [[ ! -f "${APP_DIR}/admin.db" ]]; then
    log "ERROR: ${APP_DIR}/admin.db not found. Skipping this run."
    return 1
  fi
  if [[ ! -d "${APP_DIR}/user_dbs" ]]; then
    log "ERROR: ${APP_DIR}/user_dbs/ not found. Skipping this run."
    return 1
  fi

  tmp=$(mktemp -d /tmp/backup-XXXXXX)
  # shellcheck disable=SC2064
  trap "rm -rf ${tmp}" RETURN

  # Compress admin.db
  log "  Compressing admin.db..."
  gzip -c "${APP_DIR}/admin.db" > "${tmp}/admin.db.gz"
  local adm_size
  adm_size=$(du -sh "${tmp}/admin.db.gz" | cut -f1)

  # Compress user_dbs/
  log "  Compressing user_dbs/..."
  local db_count
  db_count=$(find "${APP_DIR}/user_dbs" -name "*.db" | wc -l | tr -d ' ')
  tar -czf "${tmp}/user_dbs.tar.gz" -C "${APP_DIR}" user_dbs
  local udb_size
  udb_size=$(du -sh "${tmp}/user_dbs.tar.gz" | cut -f1)

  # Metadata
  cat > "${tmp}/meta.json" <<EOF
{
  "timestamp":                "${ts}",
  "week_slot":                ${slot},
  "day_of_week":              "${dow}",
  "admin_db_compressed_size": "${adm_size}",
  "user_dbs_compressed_size": "${udb_size}",
  "user_db_count":            ${db_count},
  "s3_prefix":                "${s3_prefix}",
  "source":                   "docker-compose-backup-sidecar"
}
EOF

  # Upload
  log "  Uploading (admin: ${adm_size}, user_dbs: ${udb_size}, ${db_count} dbs)..."
  aws s3 cp "${tmp}/admin.db.gz"     "${s3_prefix}/admin.db.gz"     --sse AES256 --only-show-errors
  aws s3 cp "${tmp}/user_dbs.tar.gz" "${s3_prefix}/user_dbs.tar.gz" --sse AES256 --only-show-errors
  aws s3 cp "${tmp}/meta.json"       "${s3_prefix}/meta.json"                     --only-show-errors

  log "=== Backup complete: ${s3_prefix} ==="
}

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
log "Backup sidecar started (project: ${PROJECT_NAME})"

BUCKET=""

while true; do

  # Step 1 — resolve bucket name (retry until instance profile credentials work)
  if [[ -z "$BUCKET" ]]; then
    BUCKET=$(get_bucket)
    if [[ -z "$BUCKET" ]]; then
      log "WARNING: Cannot resolve AWS account ID — instance profile not ready? Retrying in 60 s."
      sleep 60
      continue
    fi
    log "Backup bucket: ${BUCKET}"
  fi

  # Step 2 — confirm bucket is reachable (retry hourly if not yet created by Terraform)
  if ! bucket_reachable "$BUCKET"; then
    log "WARNING: Bucket '${BUCKET}' is not reachable (run 'terraform apply' to create it). Retrying in 1 h."
    sleep 3600
    BUCKET=""   # re-derive in case the issue was also credential-related
    continue
  fi

  # Step 3 — sleep until next 06:00 UTC
  secs=$(secs_until_utc 6 0)
  next=$(date -u -d "@$(( $(date -u +%s) + secs ))" '+%Y-%m-%d %H:%M UTC')
  log "Bucket OK. Next backup at ${next} (sleeping ${secs} s)."
  sleep "$secs"

  # Step 4 — run backup; on failure log and continue (never crash the loop)
  run_backup "$BUCKET" \
    || log "WARNING: Backup run failed. Will retry at the next scheduled time."

done
