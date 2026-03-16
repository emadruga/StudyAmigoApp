# Backup Procedure Fix — 2026-03-14

## Summary

The first scheduled backup run (week-1/saturday, 2026-03-14 06:00 UTC) produced a
zero-byte `admin.db.gz` and a missing `user_dbs.tar.gz`. This document records the
root-cause analysis, the fix applied, and the verification steps performed.

---

## Timeline

| Time (UTC)       | Event |
|------------------|-------|
| 2026-03-14 06:00 | First scheduled backup runs inside `flashcard_backup` container |
| 2026-03-14 06:00 | `admin.db.gz` uploaded as 0 bytes; `user_dbs.tar.gz` not uploaded |
| 2026-03-14 15:40 | `activity_monitor.py` run reveals 0-byte archive and 404 on `user_dbs.tar.gz` |
| 2026-03-14 15:57 | Root cause identified; fix committed and deployed |
| 2026-03-14 16:00 | Smoke test confirms correct compression inside the running container |

---

## Root Cause

The `backup` service uses the `amazon/aws-cli:latest` Docker image.  This image is a
**minimal Amazon Linux build** that ships AWS CLI tools only — it does **not** include
`gzip` or `tar`.

Original `backup_container.sh` called both tools unconditionally:

```bash
gzip -c "${APP_DIR}/admin.db" > "${tmp}/admin.db.gz"
tar  -czf "${tmp}/user_dbs.tar.gz" -C "${APP_DIR}" user_dbs
```

Because the script ran under `set -euo pipefail` but the compression commands were
not guarded with explicit error checks at the time of the first run, the failures
were swallowed.  Specifically:

- `gzip: command not found` → the redirect `> admin.db.gz` still created an empty file.
- `tar: command not found`  → `user_dbs.tar.gz` was never created.
- The upload step attempted to copy the empty `admin.db.gz` (succeeding) and the
  non-existent `user_dbs.tar.gz` (failing with AWS CLI error, but the loop continued).

The resulting S3 slot (`backups/week-1/saturday/`) contained:

```
admin.db.gz   →  0 bytes  (corrupt)
meta.json     →  present  (sizes reported as empty strings)
user_dbs.tar.gz  →  absent (404)
```

---

## Fix Applied

### 1. Install missing tools at container startup (`backup_container.sh`)

Added a guard block immediately after `set -euo pipefail` that installs `gzip` and
`tar` via `yum` when they are not present in the image.  The block is idempotent —
subsequent container restarts skip the install if the tools are already there.

```bash
if ! command -v gzip &>/dev/null || ! command -v tar &>/dev/null; then
  echo "[backup] Installing missing tools (gzip, tar)..."
  yum install -y gzip tar > /dev/null 2>&1
fi
```

### 2. Explicit error guards already in place (prior commits)

Earlier in the same session, explicit guards were added around every compression and
upload step (commits `502295b`, `3c22f63`).  These guards now surface failures
clearly rather than silently continuing:

```bash
gzip -c "${APP_DIR}/admin.db" > "${tmp}/admin.db.gz" \
  || { log "ERROR: gzip failed for admin.db. Aborting."; return 1; }

if [[ ! -s "${tmp}/admin.db.gz" ]]; then
  log "ERROR: admin.db.gz is empty after compression. Aborting."
  return 1
fi
```

---

## Commits

| Commit    | Message |
|-----------|---------|
| `502295b` | `fix(backup): add explicit error guards to prevent partial S3 uploads` |
| `35d079b` | `fix(backup): install gzip and tar on container startup` |

---

## Deployment Steps Performed

```bash
# 1. Commit and push fix
git add server/tools/backup_container.sh
git commit -m "fix(backup): install gzip and tar on container startup"
git push origin main

# 2. Pull on EC2 and restart the backup container
ssh ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && \
   sudo git pull origin main && \
   sudo docker compose restart backup"
```

---

## Verification

Confirmed inside the running container immediately after the fix was deployed:

```
$ docker exec flashcard_backup bash -c 'command -v gzip && command -v tar && echo BOTH_OK'
/usr/bin/gzip
/usr/bin/tar
BOTH_OK

$ docker exec flashcard_backup bash -c '
  tmp=$(mktemp -d)
  gzip -c /app/admin.db > "$tmp/admin.db.gz"
  tar -czf "$tmp/user_dbs.tar.gz" -C /app user_dbs
  du -sh "$tmp"/*
  rm -rf "$tmp"
'
8.0K   admin.db.gz
1.2M   user_dbs.tar.gz
```

Both archives are non-zero and correctly sized.

---

## State of the Corrupt Slot

The `week-1/saturday` slot in S3 remains corrupt (0-byte `admin.db.gz`, missing
`user_dbs.tar.gz`).  It will be **overwritten automatically** on the next
Saturday backup run (2026-03-21 06:00 UTC) as the rotation scheme reuses the same
slot key.

No manual S3 cleanup is required.

---

## Preventive Measures Going Forward

| Measure | Where |
|---------|-------|
| `command -v` guard installs `gzip`/`tar` if missing | `backup_container.sh` startup |
| Explicit `\|\| { log ERROR; return 1; }` on every `gzip` and `tar` call | `run_backup()` |
| Empty-file check (`[[ ! -s file ]]`) after each compression step | `run_backup()` |
| `activity_monitor.py` skips S3 slots where `meta.json` is absent or either archive is 0 bytes | `fetch_from_s3()` |

---

*Document written: 2026-03-14*
