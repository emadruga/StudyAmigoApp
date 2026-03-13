# StudyAmigo — Automated Backup & Restore

## 1. The Problem

StudyAmigo stores all user data in two SQLite assets on the EC2 instance's root EBS volume:

| Asset | Purpose |
|---|---|
| `server/admin.db` | User credentials, user IDs |
| `server/user_dbs/<username>.db` | Per-user flashcard collections (Anki-compatible) |

Because both assets live on the root EBS volume (not a separate data volume), a `terraform destroy` / `terraform apply` cycle **destroys all user data**. This is exactly what happened on 2026-03-13 when the EC2 instance was recreated — all data was lost and had to be restored from a 2-day-old local backup.

A manual backup process is also fragile: if the developer's Mac is lost or the local copy is outdated, data cannot be recovered.

---

## 2. Solution: Automated Daily Backup to S3

### 2.1 Architecture

```
EC2 Instance (cron 06:00 UTC = 03:00 BRT)
    │
    ├── gzip(admin.db)          → admin.db.gz
    └── tar.gz(user_dbs/)       → user_dbs.tar.gz
                │
                ▼
        S3 Bucket (AES-256 encrypted, private)
        s3://study-amigo-backups-<ACCOUNT_ID>/
            └── backups/
                ├── week-1/
                │   ├── monday/
                │   │   ├── admin.db.gz
                │   │   ├── user_dbs.tar.gz
                │   │   └── meta.json
                │   ├── tuesday/ …
                │   └── saturday/
                ├── week-2/ …
                ├── week-3/ …
                └── week-4/ …
```

### 2.2 Rotation Scheme — 4-Week Rolling Window

The backup maintains **28 slots** (4 weeks × 7 days). Each slot is overwritten when the same slot recurs, so storage is capped at 28 compressed backups.

**Slot key:** `backups/week-{1..4}/{day-of-week}/`

**Week-slot calculation:**

```
Reference Saturday: 2026-03-14 00:00:00 UTC  (epoch 1741910400)
Days since reference ÷ 7 = weeks elapsed
(weeks elapsed mod 4) + 1 = current week slot (1–4)
```

| Elapsed weeks | Slot | Calendar span |
|---|---|---|
| 0 | 1 | Mar 14 – Mar 20 2026 |
| 1 | 2 | Mar 21 – Mar 27 2026 |
| 2 | 3 | Mar 28 – Apr 03 2026 |
| 3 | 4 | Apr 04 – Apr 10 2026 |
| 4 | **1** ← rotation | Apr 11 – Apr 17 2026 |
| 5 | **2** ← rotation | Apr 18 – Apr 24 2026 |

Every Saturday at midnight UTC the week slot advances. Old backups from the previous cycle in the same slot are silently overwritten.

### 2.3 Storage Estimate

| File | Typical compressed size |
|---|---|
| `admin.db.gz` | ~8 KB |
| `user_dbs.tar.gz` | ~5–15 MB (≈70 users) |

28 slots × ~15 MB ≈ **420 MB maximum**. At S3 standard pricing (~$0.023/GB/month) that is **< $0.01/month**.

---

## 3. AWS Infrastructure

All resources are declared in `server/aws_terraform/backup.tf` and managed with Terraform.

| Resource | Name | Purpose |
|---|---|---|
| `aws_s3_bucket` | `study-amigo-backups-<ACCOUNT>` | Stores all backup archives |
| `aws_s3_bucket_server_side_encryption_configuration` | — | AES-256 at rest |
| `aws_s3_bucket_public_access_block` | — | Blocks all public access |
| `aws_iam_role` | `study-amigo-ec2-backup-role` | EC2 assumes this role |
| `aws_iam_role_policy` | `study-amigo-s3-backup-policy` | Scoped S3 read/write on the backup bucket only |
| `aws_iam_instance_profile` | `study-amigo-ec2-instance-profile` | Attaches the role to the EC2 instance |

The EC2 instance in `main.tf` now carries `iam_instance_profile`, so **no AWS access keys are stored on the server**. The backup script uses the instance profile credentials automatically via the AWS metadata service.

---

## 4. Files

| File | Location | Purpose |
|---|---|---|
| `backup.tf` | `server/aws_terraform/` | Terraform — S3 + IAM |
| `backup.sh` | `server/tools/` | Cron backup script (runs on EC2) |
| `install_backup_cron.sh` | `server/tools/` | One-time installer (run from Mac) |
| `verify_backups.py` | `server/tools/` | Verify all 28 slots in S3 (run from Mac) |
| `restore_backup.py` | `server/tools/` | Restore a backup (run from Mac or EC2) |

---

## 5. Deployment

### Step 1 — Apply Terraform

```bash
cd server/aws_terraform
terraform apply
```

This creates the S3 bucket and IAM instance profile, and attaches the profile to the EC2 instance **in-place** (no instance replacement required).

After apply, note the bucket name:

```bash
terraform output backup_bucket
# → study-amigo-backups-123456789012
```

### Step 2 — Install the Cron on the Running Instance

Run `install_backup_cron.sh` once from your Mac:

```bash
chmod +x server/tools/install_backup_cron.sh

./server/tools/install_backup_cron.sh study-amigo-backups-123456789012

# Override SSH target if needed:
# EC2_HOST=54.152.109.26 SSH_KEY=~/.ssh/study-amigo-aws \
#   ./server/tools/install_backup_cron.sh study-amigo-backups-123456789012
```

This script:
1. Uploads `backup.sh` to `/opt/studyamigo-backup/backup.sh` on EC2
2. Writes the bucket name to `/opt/studyamigo-backup/env`
3. Installs a cron entry: `0 6 * * *` (06:00 UTC = 03:00 BRT)
4. Verifies the IAM instance profile is working

### Step 3 — Trigger a Manual Test Run

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  'source /opt/studyamigo-backup/env && /opt/studyamigo-backup/backup.sh'
```

Check the log:

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  'tail -50 /var/log/studyamigo-backup.log'
```

### Step 4 — Verify on S3

```bash
pip install boto3          # one-time
python3 server/tools/verify_backups.py \
  --bucket study-amigo-backups-123456789012 \
  --profile study-amigo
```

---

## 6. `verify_backups.py` — Usage

Prints a 28-row status grid showing the state of every backup slot.

```
Usage: python3 server/tools/verify_backups.py --bucket BUCKET [options]

Options:
  --bucket BUCKET       S3 bucket name (required)
  --profile PROFILE     AWS CLI profile (default: instance profile / AWS_PROFILE)
  --region  REGION      AWS region (default: us-east-1)
  --verify-integrity    Download each archive and verify gzip/tar integrity (slower)
```

### Example output

```
StudyAmigo Backup Verifier
Bucket : study-amigo-backups-123456789012

Slot                             Status       admin.db.gz  user_dbs.tar.gz  Age                Timestamp
──────────────────────────────────────────────────────────────────────────────────────────────────────────────
  week-1/monday                  OK                  8 KB          12 MB    0 d 3 h ago        2026-03-17T06:00:02Z  (73 user dbs)
  week-1/tuesday                 OK                  8 KB          12 MB    1 d 3 h ago        2026-03-16T06:00:01Z  (73 user dbs)
  week-1/wednesday               EMPTY
  …
► week-1/friday                  OK                  8 KB          12 MB    2 h 1 min ago      2026-03-13T06:00:03Z  (73 user dbs)
  week-1/saturday                EMPTY
  week-1/sunday                  EMPTY

  week-2/monday                  EMPTY
  …
```

`►` marks the current slot. `EMPTY` means no backup has run for that slot yet (expected during the first 4 weeks). `PARTIAL` means some files uploaded but others are missing (indicates a failed backup run).

---

## 7. `restore_backup.py` — Usage

Two modes: **LOCAL** (run on the EC2 instance itself) and **REMOTE** (orchestrated over SSH from your Mac).

### 7.1 List available backups

```bash
# From Mac (remote)
python3 server/tools/restore_backup.py \
  --bucket study-amigo-backups-123456789012 \
  --profile study-amigo \
  --list

# From EC2 (local)
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

# Once on EC2:

# Restore latest backup
python3 /opt/study-amigo/server/tools/restore_backup.py \
  --bucket study-amigo-backups-123456789012 \
  --latest

# Restore a specific slot
python3 /opt/study-amigo/server/tools/restore_backup.py \
  --bucket study-amigo-backups-123456789012 \
  --week 1 --day friday

# Dry run (no changes)
python3 /opt/study-amigo/server/tools/restore_backup.py \
  --bucket study-amigo-backups-123456789012 \
  --latest --dry-run
```

The script will:
1. Download selected backup from S3 to a temp directory on EC2
2. Save the current databases to `/tmp/studyamigo-pre-restore/` (safety copy)
3. Stop the `flashcard_server` Docker container
4. Decompress `admin.db.gz` → `server/admin.db`
5. Extract `user_dbs.tar.gz` → `server/user_dbs/`
6. Fix ownership (`ubuntu:ubuntu`)
7. Start the `flashcard_server` container
8. Verify it is running

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

Same steps as local mode, but orchestrated over SSH from your Mac. Requires `boto3` installed on the Mac.

### 7.4 Safety features

- **Pre-restore snapshot**: current databases are always copied to `/tmp/studyamigo-pre-restore/` before any changes, so you can manually roll back if needed.
- **Confirmation prompt**: the script asks you to type `yes` before making any changes (skipped with `--dry-run`).
- **Tar path filtering**: only `user_dbs/` entries are extracted from the tar archive — no path traversal possible.

---

## 8. Log File

All backup runs are appended to `/var/log/studyamigo-backup.log` on the EC2 instance.

```bash
# View last backup run
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  'tail -30 /var/log/studyamigo-backup.log'
```

A successful run looks like:

```
[2026-03-14 06:00:02 UTC] ================================================================
[2026-03-14 06:00:02 UTC] StudyAmigo backup starting
[2026-03-14 06:00:02 UTC]   Week slot : 1/4
[2026-03-14 06:00:02 UTC]   Day       : saturday
[2026-03-14 06:00:02 UTC]   S3 target : s3://study-amigo-backups-123456789012/backups/week-1/saturday
[2026-03-14 06:00:02 UTC] ================================================================
[2026-03-14 06:00:03 UTC] Compressing admin.db...
[2026-03-14 06:00:03 UTC]   admin.db.gz : 8.0K
[2026-03-14 06:00:03 UTC] Compressing user_dbs/...
[2026-03-14 06:00:05 UTC]   user_dbs.tar.gz : 12M (73 databases)
[2026-03-14 06:00:05 UTC] Uploading to S3...
[2026-03-14 06:00:07 UTC] ================================================================
[2026-03-14 06:00:07 UTC] Backup complete: s3://study-amigo-backups-123456789012/backups/week-1/saturday
[2026-03-14 06:00:07 UTC] ================================================================
```

---

## 9. Future Enhancements (Recommended)

| Enhancement | Benefit |
|---|---|
| Separate EBS data volume for `user_dbs/` + `admin.db` | EC2 can be replaced without losing data |
| SNS/SES alert on backup failure | Immediate notification if cron backup fails |
| Add backup installation to `user_data.sh` | New instances automatically get cron backup without manual `install_backup_cron.sh` |
| AWS Backup service | Managed solution with cross-region copy and compliance controls |
