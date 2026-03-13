# StudyAmigo — Automated Backup & Restore

## 1. The Problem

StudyAmigo stores all user data in two SQLite assets on the EC2 instance's root EBS volume:

| Asset | Purpose |
|---|---|
| `server/admin.db` | User credentials and user IDs |
| `server/user_dbs/<username>.db` | Per-user flashcard collections (Anki-compatible) |

Because both assets live on the root EBS volume, a `terraform destroy` / `terraform apply`
cycle **destroys all user data**. This happened on 2026-03-13 when the EC2 instance was
recreated — all data was lost and had to be restored from a 2-day-old local backup.

A manual, local-only backup process is also fragile: if the developer's Mac is lost or the
local copy is outdated, data cannot be recovered.

---

## 2. Solution

### 2.1 Overview

A dedicated `backup` container runs as a sidecar service inside the existing
`docker-compose.yml`. It starts and stops automatically alongside the application — no
host-level cron, no manual installation step, no separate deploy procedure.

```
docker-compose up -d
    ├── flashcard_server   (Flask/Gunicorn — unchanged)
    ├── flashcard_client   (Nginx/React    — unchanged)
    └── flashcard_backup   ← new sidecar
            │
            │  on startup:
            ├─ query AWS STS → derive bucket name from account ID
            ├─ check bucket reachable
            │     ├─ NOT reachable → log warning, retry every hour (graceful)
            │     └─ reachable    → sleep until 06:00 UTC, then backup, loop
            │
            └── daily at 06:00 UTC (03:00 BRT):
                    ├── gzip admin.db       → admin.db.gz
                    ├── tar.gz user_dbs/    → user_dbs.tar.gz
                    └── upload both + meta.json → S3
```

### 2.2 Key Design Decisions

**No hardcoded bucket name.** The container derives the bucket name at runtime by calling
`aws sts get-caller-identity` to get the AWS account ID, then constructing
`study-amigo-backups-<ACCOUNT_ID>` — exactly the same formula Terraform uses. This means
no environment variable or config file needs to be updated when the bucket is created.

**Graceful handling of missing bucket.** The Terraform S3 bucket and IAM instance profile
may not exist yet when the container first starts (e.g. `docker-compose up -d` was run
before `terraform apply`). The container detects this, logs a clear warning, and retries
every hour until the bucket becomes reachable. It never crashes.

**No host-level cron.** The backup schedule is managed entirely inside the container using
a `sleep` loop. This means no SSH, no `install_backup_cron.sh`, no host setup.

**Zero impact on `docker-compose up -d`.** Docker Compose only starts the new `backup`
service — it leaves `flashcard_server` and `flashcard_client` running and untouched.

### 2.3 Rotation — 4-Week Rolling Window

The backup maintains **28 slots** (4 weeks × 7 days). Each slot is silently overwritten
when the same slot recurs, so storage cost is capped and never grows unboundedly.

**S3 path structure:**
```
s3://study-amigo-backups-<ACCOUNT_ID>/
    backups/
        week-1/
            monday/    { admin.db.gz, user_dbs.tar.gz, meta.json }
            tuesday/   { … }
            …
            sunday/    { … }
        week-2/ …
        week-3/ …
        week-4/ …
```

**Slot calculation:**

A fixed reference Saturday (2026-03-14 00:00 UTC, epoch `1741910400`) is used as the
origin. The current week slot is:

```
days_since_reference = (now_epoch - 1741910400) / 86400
week_slot = (days_since_reference / 7) mod 4 + 1   →  1, 2, 3, or 4
```

The slot advances every Saturday at midnight UTC. After 4 weeks the cycle repeats,
overwriting the oldest matching slot:

| Elapsed weeks | Slot | Example span |
|---|---|---|
| 0 | 1 | Mar 14 – Mar 20 2026 |
| 1 | 2 | Mar 21 – Mar 27 2026 |
| 2 | 3 | Mar 28 – Apr 03 2026 |
| 3 | 4 | Apr 04 – Apr 10 2026 |
| 4 | **1** ← rotates | Apr 11 – Apr 17 2026 |
| 5 | **2** ← rotates | Apr 18 – Apr 24 2026 |

### 2.4 Storage Estimate

| File | Typical compressed size |
|---|---|
| `admin.db.gz` | ~8 KB |
| `user_dbs.tar.gz` | ~5–15 MB (≈73 users) |

28 slots × ~15 MB ≈ **420 MB maximum** → less than **$0.01/month** on S3 Standard.

---

## 3. AWS Infrastructure

Managed by Terraform in `server/aws_terraform/backup.tf`. Created once with
`terraform apply` — **does not touch the EC2 instance**.

| Resource | Name | Purpose |
|---|---|---|
| `aws_s3_bucket` | `study-amigo-backups-<ACCOUNT>` | Stores all backup archives |
| SSE configuration | — | AES-256 encryption at rest |
| Public access block | — | All public access blocked |
| `aws_iam_role` | `study-amigo-ec2-backup-role` | Assumed by EC2 via instance profile |
| `aws_iam_role_policy` | `study-amigo-s3-backup-policy` | S3 read/write on backup bucket only |
| `aws_iam_instance_profile` | `study-amigo-ec2-instance-profile` | Attaches role to EC2 |

The EC2 instance carries `iam_instance_profile` in `main.tf`. **No AWS access keys are
stored on the server** — the backup container uses the instance profile credentials
automatically via the EC2 metadata service (`169.254.169.254`), which is reachable from
inside Docker containers.

---

## 4. Files

| File | Location | Purpose |
|---|---|---|
| `backup.tf` | `server/aws_terraform/` | Terraform — S3 bucket + IAM |
| `backup_container.sh` | `server/tools/` | Backup container entrypoint (loop + backup logic) |
| `verify_backups.py` | `server/tools/` | Verify all 28 slots in S3 (run from Mac) |
| `restore_backup.py` | `server/tools/` | Restore a backup from S3 (run from Mac or EC2) |
| `backup.sh` | `server/tools/` | *(Fallback)* Standalone host-level backup script |
| `install_backup_cron.sh` | `server/tools/` | *(Fallback)* Manual host cron installer |

> The fallback scripts (`backup.sh`, `install_backup_cron.sh`) are kept for emergency
> situations where Docker is not available. Under normal operations, the `backup` service
> in `docker-compose.yml` is the only mechanism in use.

---

## 5. Deployment

### Step 1 — Apply Terraform (one-time, safe)

```bash
cd server/aws_terraform
terraform apply
```

This creates the S3 bucket and IAM instance profile. It performs an **in-place update**
to attach the instance profile to the running EC2 instance — **no instance replacement,
no data loss**.

Confirm the bucket name:
```bash
terraform output backup_bucket
# → study-amigo-backups-123456789012
```

### Step 2 — Pull latest code on EC2 and restart compose

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && \
   sudo git pull origin main && \
   sudo docker compose up -d"
```

Docker Compose will:
- Leave `flashcard_server` and `flashcard_client` **running and untouched**
- Create and start the new `flashcard_backup` container

That's it. No further steps required.

### Step 3 — Verify the backup container started

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker compose ps"
```

Expected output:
```
NAME                IMAGE                  STATUS
flashcard_client    study-amigo-client     Up
flashcard_server    study-amigo-server     Up
flashcard_backup    amazon/aws-cli         Up
```

Watch the startup log:
```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker compose logs --tail=20 backup"
```

If the bucket is reachable you will see:
```
[backup] 2026-03-14 06:05:11 UTC Backup bucket: study-amigo-backups-123456789012
[backup] 2026-03-14 06:05:11 UTC Bucket OK. Next backup at 2026-03-15 06:00 UTC (sleeping 86089 s).
```

If Terraform has not been applied yet:
```
[backup] 2026-03-14 06:05:11 UTC WARNING: Bucket 'study-amigo-backups-123456789012' is not reachable
         (may not exist yet — run terraform apply). Retrying in 1 h.
```
→ Run `terraform apply`, wait up to 1 hour, the container will recover automatically.

### Step 4 — Trigger a manual backup to smoke-test

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker compose exec backup \
     sh -c 'BACKUP_BUCKET_OVERRIDE=study-amigo-backups-123456789012 \
            PROJECT_NAME=study-amigo \
            /app/tools/backup_container.sh'"
```

Or simply wait until 06:00 UTC and check the logs.

---

## 6. Monitoring Backups

### View live backup logs
```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker compose logs -f backup"
```

### Verify all 28 slots from your Mac
```bash
pip install boto3   # one-time

python3 server/tools/verify_backups.py \
    --bucket study-amigo-backups-123456789012 \
    --profile study-amigo
```

Example output:
```
StudyAmigo Backup Verifier
Bucket : study-amigo-backups-123456789012

Slot                             Status       admin.db.gz  user_dbs.tar.gz  Age                Timestamp
──────────────────────────────────────────────────────────────────────────────────────────────────────────
  week-1/monday                  OK                  8 KB          12 MB    1 d 3 h ago        2026-03-16T06:00:01Z  (73 user dbs)
  week-1/tuesday                 OK                  8 KB          12 MB    0 d 3 h ago        2026-03-17T06:00:02Z  (73 user dbs)
  week-1/wednesday               EMPTY
  …
► week-1/friday                  OK                  8 KB          12 MB    2 h 1 min ago      2026-03-13T06:00:03Z  (73 user dbs)
  week-1/saturday                EMPTY
  week-1/sunday                  EMPTY

  week-2/ …
```

`►` marks the current active slot. `EMPTY` is expected for slots that haven't run yet.
`PARTIAL` means a backup run was interrupted mid-upload.

With integrity checking (downloads and validates each archive):
```bash
python3 server/tools/verify_backups.py \
    --bucket study-amigo-backups-123456789012 \
    --profile study-amigo \
    --verify-integrity
```

---

## 7. Restoring a Backup

### 7.1 List available backups

**From your Mac:**
```bash
python3 server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --profile study-amigo \
    --list
```

**From EC2 (uses instance profile — no `--profile` needed):**
```bash
python3 /opt/study-amigo/server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --list
```

Output:
```
#   Slot                   Timestamp (UTC)        admin.db.gz  user_dbs.tar.gz  User DBs
──────────────────────────────────────────────────────────────────────────────────────────
1   week-1/friday          2026-03-13T06:00:03Z          8 KB           12 MB        73
2   week-1/thursday        2026-03-12T06:00:01Z          8 KB           12 MB        72
…
```

### 7.2 Restore — LOCAL mode (recommended, run on EC2)

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26

# Restore the latest backup
python3 /opt/study-amigo/server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --latest

# Restore a specific slot
python3 /opt/study-amigo/server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --week 1 --day friday

# Preview without making changes
python3 /opt/study-amigo/server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --latest --dry-run
```

The restore process:
1. Downloads selected backup from S3 to a temp directory on EC2
2. Saves current databases to `/tmp/studyamigo-pre-restore/` (safety snapshot)
3. Stops `flashcard_server` container
4. Decompresses `admin.db.gz` → `server/admin.db`
5. Extracts `user_dbs.tar.gz` → `server/user_dbs/`
6. Fixes ownership (`ubuntu:ubuntu`)
7. Starts `flashcard_server` container
8. Verifies the container is running

### 7.3 Restore — REMOTE mode (from Mac)

```bash
python3 server/tools/restore_backup.py \
    --bucket study-amigo-backups-123456789012 \
    --profile study-amigo \
    --remote \
    --host 54.152.109.26 \
    --ssh-key ~/.ssh/study-amigo-aws \
    --latest
```

### 7.4 Safety features

- **Pre-restore snapshot** — current databases are always saved to
  `/tmp/studyamigo-pre-restore/` before any changes. Manual rollback is possible.
- **Confirmation prompt** — type `yes` to proceed; `--dry-run` skips all changes.
- **Tar path filtering** — only `user_dbs/` entries are extracted; no path traversal.

---

## 8. Successful Backup Log (Reference)

```
[backup] 2026-03-14 06:00:01 UTC === Backup starting: week-1/saturday → s3://study-amigo-backups-123456789012/backups/week-1/saturday ===
[backup] 2026-03-14 06:00:02 UTC   Compressing admin.db...
[backup] 2026-03-14 06:00:02 UTC   Compressing user_dbs/...
[backup] 2026-03-14 06:00:05 UTC   Uploading (admin: 8.0K, user_dbs: 12M, 73 dbs)...
[backup] 2026-03-14 06:00:08 UTC === Backup complete: s3://study-amigo-backups-123456789012/backups/week-1/saturday ===
[backup] 2026-03-14 06:00:08 UTC Bucket OK. Next backup at 2026-03-15 06:00 UTC (sleeping 86392 s).
```

---

## 9. Future Enhancements

| Enhancement | Benefit |
|---|---|
| Separate EBS data volume for `server/` databases | EC2 can be replaced without touching user data |
| SNS/SES alert when backup container exits unexpectedly | Immediate notification of backup failure |
| Cross-region S3 replication | Protects against full AWS region outage |
