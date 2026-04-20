# Activity Monitor — How-To Guide

`activity_monitor.py` analyses card reviews and card creations across all user
databases for a chosen time window, and ranks students by consistency and
engagement.

---

## How It Works

### Database access strategy

The script supports three data sources, tried in this order of preference:

| Priority | Source | When used |
|----------|--------|-----------|
| 1 | **S3 backup** (default) | `--profile` or `--bucket` provided (or auto-derived) |
| 2 | **SSH / live production** | `--host` provided; used as fallback when no S3 backups exist |
| 3 | **Local files** | `--local-only` flag |

#### S3 (default)

The script downloads the latest (or a specified) automated backup from the S3
bucket, decompresses the archives into a temp directory, and analyses the
resulting SQLite files. The bucket name is derived automatically from the AWS
account ID via STS — no hardcoded name required:

```
study-amigo-backups-<account-id>
```

The backup rotation uses 28 slots (`week-1..4 × monday..sunday`), matching the
schedule produced by `backup_container.sh`. The script reads `meta.json` from
each slot to determine completeness; **incomplete slots** (zero-byte or missing
archives) are skipped automatically and the next complete slot is used instead.

#### SSH / live production (fallback)

When `--host` is given and no S3 backups are available, the script uses `scp`
to copy `admin.db` and the entire `user_dbs/` directory from the EC2 host
directly. This works because `docker-compose.yml` bind-mounts `./server → /app`
inside the `flashcard_server` container, making all databases accessible on the
host at `$REMOTE_PATH/admin.db` and `$REMOTE_PATH/user_dbs/`. No `docker exec`
needed.

After analysis the temp folder is automatically deleted (unless `--cache-dir`
is used).

### What is analysed

| Metric | Source | Notes |
|--------|--------|-------|
| Card reviews | `revlog.id` (ms timestamp) | Filtered to the chosen window |
| Card creations | `cards.id` (ms timestamp) | Seed/sample cards (`id ≤ 1,700,000,000,000 ms`) excluded; pre-loaded "Verbal Tenses" deck excluded |
| User list | `admin.db → users` table | Maps `user_id` to `username` and `name` |

### Engagement score (Top-10 ranking)

A weighted composite score out of ~1.0:

| Component | Weight | Description |
|-----------|--------|-------------|
| Consistency | 55 % | `active_days / window_days` |
| Volume | 35 % | `log(reviews + creations)` — log-scaled so power users don't dwarf everyone |
| Quality | 10 % | Penalises a high "Again" (ease=1) ratio |

---

## Prerequisites

- Python 3.8+ (standard library only for SSH/local modes)
- **`boto3`** — required for S3 mode: `pip install boto3`
- AWS credentials configured (profile or environment variables) — for S3 mode
- SSH access to the EC2 instance (`~/.ssh/study-amigo-aws` by default) — for SSH fallback only
- The `scp` command available locally — for SSH fallback only

---

## Usage

```
python activity_monitor.py [OPTIONS]
```

### Time window options

| Flag | Window |
|------|--------|
| `--interval 24h` | Last 24 hours |
| `--interval week` | Last 7 days |
| `--interval 2weeks` | Last 14 days |
| `--interval 3weeks` | Last 21 days |
| `--interval month` | Last 30 days |
| `--interval custom --start YYYY-MM-DD [--end YYYY-MM-DD]` | Custom range; `--end` defaults to today |

### S3 options (primary source)

| Flag | Default | Description |
|------|---------|-------------|
| `--profile NAME` | *(none)* | AWS named profile to use (e.g. `study-amigo`) |
| `--bucket NAME` | *(auto-derived)* | Explicit S3 bucket name; skips STS account-ID lookup |
| `--region REGION` | `us-east-1` | AWS region |
| `--week N` | *(latest)* | Select a specific rotation week (1–4) |
| `--day NAME` | *(latest)* | Select a specific day of the week (e.g. `friday`) |
| `--list-slots` | *(off)* | Print all available slots and prompt for interactive selection |
| `--s3-prefix PREFIX` | `backups/v15` | S3 key prefix for backup slots. Use `backups` for SAv1.0. |
| `--v10` | *(off)* | Shortcut for SAv1.0 (legacy): sets `--s3-prefix backups`, `--remote-path /opt/study-amigo/server`, `--container flashcard_server` |

When neither `--week`/`--day` nor `--list-slots` is given, the **most recent
complete** slot is selected automatically.

#### SAv1.0 vs SAv1.5 S3 layout

Both versions write to the same bucket but use different prefixes:

| Version | S3 prefix | Backup time | Default? |
|---------|-----------|-------------|----------|
| SAv1.5 | `backups/v15/week-{1..4}/{day}/` | 08:00 UTC daily | **sim** |
| SAv1.0 | `backups/week-{1..4}/{day}/` | 06:00 UTC daily | não — use `--v10` |

### SSH / live-production options (fallback)

| Flag | Default | Description |
|------|---------|-------------|
| `--host HOST` | *(none — triggers SSH mode)* | EC2 Elastic IP or hostname |
| `--key PATH` | `~/.ssh/study-amigo-aws` | SSH private key path |
| `--user USER` | `ubuntu` | SSH login user |
| `--remote-path PATH` | `/opt/study-amigo-v15/server` | Path to the server directory on EC2 (SAv1.5 default; `--v10` changes this to `/opt/study-amigo/server`) |
| `--container NAME` | `v15_server` | Docker container name (SAv1.5 default; `--v10` changes this to `flashcard_server`) |

### Local-only mode (no network)

If you already have the databases locally, skip all network access:

```bash
python activity_monitor.py --interval week --local-only \
    --admin-db /path/to/admin.db \
    --user-db-dir /path/to/user_dbs
```

### Output options

| Flag | Description |
|------|-------------|
| `--top N` | Number of users shown in the ranking (default: 10) |
| `--no-breakdown` | Skip the per-user detailed breakdown section |

---

## Examples

```bash
# ── SAv1.5 — S3 (default, prefix: backups/v15) ───────────────────────────

# Most common: last week, auto-select latest complete backup
python activity_monitor.py --interval week --profile study-amigo

# Explicit bucket (skips STS lookup)
python activity_monitor.py --interval week \
    --bucket study-amigo-backups-645069181643 --profile study-amigo

# Last month
python activity_monitor.py --interval month --profile study-amigo

# Specific slot (week 1, thursday)
python activity_monitor.py --interval week --profile study-amigo \
    --week 1 --day thursday

# Interactive slot picker
python activity_monitor.py --interval week --profile study-amigo \
    --list-slots

# ── SAv1.0 — S3 legacy (prefix: backups/) ────────────────────────────────

# Shortcut: --v10 sets prefix + remote-path + container to SAv1.0 values
python activity_monitor.py --interval week --v10 --profile study-amigo

# Specific slot
python activity_monitor.py --interval week --v10 --profile study-amigo \
    --week 2 --day tuesday

# ── SSH / live production ─────────────────────────────────────────────────

# SAv1.5 — pull from live v15 stack (default)
python activity_monitor.py --interval week --host 54.152.109.26

# SAv1.0 — pull directly from legacy production
python activity_monitor.py --interval week --v10 --host 54.152.109.26

# Non-default key / remote path
python activity_monitor.py --interval month \
    --host 54.152.109.26 \
    --key ~/.ssh/my-other-key \
    --remote-path /opt/study-amigo/server

# ── Local files ───────────────────────────────────────────────────────────

# Already have the DBs locally — skip all network
python activity_monitor.py --interval week --local-only \
    --admin-db /tmp/dbs/admin.db \
    --user-db-dir /tmp/dbs/user_dbs

# ── Output control ────────────────────────────────────────────────────────

# Top 20 students, no per-user breakdown
python activity_monitor.py --interval month --profile study-amigo \
    --top 20 --no-breakdown

# Custom date range
python activity_monitor.py --interval custom \
    --start 2026-01-15 --end 2026-02-28 \
    --profile study-amigo
```

---

## Incomplete Slot Handling

When a backup run fails mid-way (e.g. missing `gzip`/`tar` in the container),
the S3 slot can be left with a zero-byte `admin.db.gz` or a missing
`user_dbs.tar.gz`. The script detects this via the `complete` field derived
from S3 object sizes:

| Situation | Behaviour |
|-----------|-----------|
| Latest slot is incomplete, others exist | Warning printed; next complete slot selected automatically |
| Explicitly requested slot (`--week`/`--day`) is incomplete | Error printed; exits with guidance to use `--list-slots` |
| All slots incomplete | Returns `None`; SSH fallback offered if `--host` was given |

---

## Output Sections

### 1. Daily Activity Summary

Aggregated table across **all** students for every day in the window:

```
════════════════════════════════════════════════════════════════════════════════
  DAILY ACTIVITY SUMMARY
════════════════════════════════════════════════════════════════════════════════
  Date            Reviews   Novos Cards  Active Users
────────────────────────────────────────────────────────────────────────────────
  2026-02-25          142          38            12
  2026-02-26          198          61            17
  ...
────────────────────────────────────────────────────────────────────────────────
  TOTAL               340          99            29 user-days
```

### 2. Top-10 Most Consistent & Engaged Students

Ranked by engagement score:

```
════════════════════════════════════════════════════════════════════════════════
  TOP-10 MOST CONSISTENT & ENGAGED STUDENTS
════════════════════════════════════════════════════════════════════════════════
  #    Full Name                      Active   Reviews  Novos Cards   Avg time   Score
────────────────────────────────────────────────────────────────────────────────
  1    Maria Silva                         7       210         45      12.3s   0.821
  2    João Pereira                        6       185         32       9.8s   0.743
  ...
```

### 3. Per-User Breakdown

Detail for the top-N most active users (suppress with `--no-breakdown`):

```
  Maria Silva
    Reviews:      210
    Novos cards:    45
    Active days:  7 / 7
    Avg review:   12.3s
    Ease dist:    Again=12 (5%)  Hard=31  Good=143  Easy=24
    Engagement:   0.821
```

---

## File Naming Convention

The script resolves user databases in this order:

1. `user_dbs/<username>.anki2` — original scheme
2. `user_dbs/user_<id>.db` — alternative scheme used in some deployments

Both naming conventions are supported transparently.

---

## Caching

By default the script downloads all databases into a temporary folder that is
deleted at the end of each run. Use `--cache-dir` to persist them on disk so
that subsequent runs skip the download entirely.

### Flags

| Flag | Description |
|------|-------------|
| `--cache-dir DIR` | Store (and reuse) databases in `DIR` instead of a temp folder |
| `--refresh` | Force a new download even when `--cache-dir` already has data |

### Behaviour

| Situation | What happens |
|-----------|--------------|
| No `--cache-dir` | Temp folder created, databases downloaded, folder deleted after run |
| `--cache-dir` set, dir is empty | Databases downloaded and saved in `DIR` |
| `--cache-dir` set, dir already has data | Download skipped; cached files used immediately |
| `--cache-dir` set + `--refresh` | Databases re-downloaded and cached files overwritten |

### Examples

```bash
# First run — downloads and caches
python activity_monitor.py --interval week --profile study-amigo \
    --cache-dir ~/.cache/studyamigo

# Subsequent runs — no download, instant analysis
python activity_monitor.py --interval month --profile study-amigo \
    --cache-dir ~/.cache/studyamigo

# Force fresh data (e.g. after students have been active)
python activity_monitor.py --interval week --profile study-amigo \
    --cache-dir ~/.cache/studyamigo --refresh
```

> **Tip:** the cached databases are plain SQLite files. You can also inspect
> them directly with any SQLite browser or pass the directory to
> `--local-only` mode for offline analysis:
>
> ```bash
> python activity_monitor.py --interval week --local-only \
>     --admin-db ~/.cache/studyamigo/admin.db \
>     --user-db-dir ~/.cache/studyamigo/user_dbs
> ```

---

## Related Files

| File | Description |
|------|-------------|
| `server/tools/activity_monitor.py` | The script itself |
| `server/tools/backup_container.sh` | SAv1.0 backup sidecar — populates `backups/week-{slot}/{day}/` at 06:00 UTC |
| `server/tools/backup_container_v15.sh` | SAv1.5 backup sidecar — populates `backups/v15/week-{slot}/{day}/` at 08:00 UTC |
| `server/docs/APP_BACKUP_RESTORE.md` | S3 backup rotation scheme, slot layout, restore procedure |
| `server/docs/Backup_Procedure_Fix_20260314.md` | Post-mortem for the first zero-byte backup (missing gzip/tar) |
| `server/docs/AWS_DOCKER_DEPLOY.md` | Full EC2 + Docker deployment guide |
| `docker-compose.yml` | SAv1.0 docker-compose (bind-mount that makes host-side DB access possible) |
| `server_v2/scripts/deploy_v15.sh` | SAv1.5 deploy script — generates docker-compose.yml for the v15 stack |
| `docs/ANKI_DB_SCHEMA.md` | Schema reference for `revlog`, `cards`, `notes` |
| `docs/ADMIN_DB_SCHEMA.md` | Schema reference for `admin.db` |

---

## IMPORTANT — Risk of Corrupt Database Copies (SSH mode only)

> This section applies only when using the SSH fallback (`--host`). S3 backups
> use compressed archives created by the backup container and are not subject
> to this risk.

### The problem

SQLite uses auxiliary files during write transactions:

- **Journal mode** (default): `<db>-journal` is written alongside the main file during a transaction.
- **WAL mode**: `<db>-wal` and `<db>-shm` are written alongside the main file.

If `scp` copies a `.db` file at the exact moment a write transaction is open
(e.g. a student submitting a card review), the copy can land in a
**partially-written, inconsistent state** — the journal or WAL file that would
complete the transaction is not included.

In practice the risk window is very small (a review write takes milliseconds),
so most copies will be fine. However, it is not guaranteed.

> **The live database on the server is never affected.** `scp` only reads; it
> cannot corrupt the original files.

### Safe alternative: `sqlite3 .backup`

The safest approach is to use SQLite's online backup API via the `sqlite3` CLI
on the remote host. This is safe even during concurrent writes:

```bash
# Back up a single user DB safely, then download it
ssh -i ~/.ssh/study-amigo-aws ubuntu@<host> \
    "sqlite3 /opt/study-amigo/server/user_dbs/user_21.db \".backup '/tmp/user_21_safe.db'\""
scp -i ~/.ssh/study-amigo-aws ubuntu@<host>:/tmp/user_21_safe.db ./user_21.db
```

### Mitigation when using this script in SSH mode

If you use `--refresh` to re-download and WAL mode is active, copying the
entire `user_dbs/` directory also copies any `.db-wal` and `.db-shm` files
that exist alongside the main database. SQLite can reconstruct the correct
state from them, so the local copy will be consistent as long as all three
files are copied together.

For a monitoring tool where slight inconsistency on one user's stats is
acceptable, the current `scp` approach is a reasonable trade-off. For backups
intended to be authoritative, use the S3 backup source or the `sqlite3
.backup` method above.
