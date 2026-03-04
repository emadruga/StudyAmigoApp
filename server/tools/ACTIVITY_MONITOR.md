# Activity Monitor — How-To Guide

`activity_monitor.py` analyses card reviews and card creations across all user
databases for a chosen time window, and ranks students by consistency and
engagement.

---

## How It Works

### Database access strategy

The script uses `scp` over SSH to copy `admin.db` and the entire `user_dbs/`
directory from the EC2 host to a local temp folder. This works because the
`docker-compose.yml` bind-mounts `./server → /app` inside the `flashcard_server`
container, so all databases are directly accessible on the host at
`$REMOTE_PATH/admin.db` and `$REMOTE_PATH/user_dbs/`. No `docker exec` needed.

After analysis the temp folder is automatically deleted.

### What is analysed

| Metric | Source | Notes |
|---|---|---|
| Card reviews | `revlog.id` (ms timestamp) | Filtered to the chosen window |
| Card creations | `cards.id` (ms timestamp) | Seed/sample cards (`id ≤ 1,700,000,000,000 ms`) excluded |
| User list | `admin.db → users` table | Maps `user_id` to `username` and `name` |

### Engagement score (Top-10 ranking)

A weighted composite score out of ~1.0:

| Component | Weight | Description |
|---|---|---|
| Consistency | 55 % | `active_days / window_days` |
| Volume | 35 % | `log(reviews + creations)` — log-scaled so power users don't dwarf everyone |
| Quality | 10 % | Penalises a high "Again" (ease=1) ratio |

---

## Prerequisites

- Python 3.8+ (standard library only — no `pip install` required)
- SSH access to the EC2 instance (`~/.ssh/study-amigo-aws` by default)
- The `scp` command available locally

---

## Usage

```
python activity_monitor.py [OPTIONS]
```

### Time window options

| Flag | Window |
|---|---|
| `--interval 24h` | Last 24 hours |
| `--interval week` | Last 7 days |
| `--interval 2weeks` | Last 14 days |
| `--interval 3weeks` | Last 21 days |
| `--interval month` | Last 30 days |
| `--interval custom --start YYYY-MM-DD --end YYYY-MM-DD` | Custom inclusive range |

### Connection options

| Flag | Default | Description |
|---|---|---|
| `--host` | *(required)* | EC2 Elastic IP or hostname |
| `--key` | `~/.ssh/study-amigo-aws` | SSH private key path |
| `--user` | `ubuntu` | SSH login user |
| `--remote-path` | `/opt/study-amigo/server` | Path to the server directory on EC2 |
| `--container` | `flashcard_server` | Docker container name (informational) |

### Local-only mode (no SSH)

If you have already copied the databases locally, skip the SSH fetch:

```bash
python activity_monitor.py --interval week --local-only \
    --admin-db /path/to/admin.db \
    --user-db-dir /path/to/user_dbs
```

### Output options

| Flag | Description |
|---|---|
| `--top N` | Number of users shown in the ranking (default: 10) |
| `--no-breakdown` | Skip the per-user detailed breakdown section |

---

## Examples

```bash
# Last week (most common use)
python activity_monitor.py --interval week --host 3.88.xx.xx

# Last 24 hours
python activity_monitor.py --interval 24h --host 3.88.xx.xx

# Last 2 / 3 weeks
python activity_monitor.py --interval 2weeks --host 3.88.xx.xx
python activity_monitor.py --interval 3weeks --host 3.88.xx.xx

# Last month (~30 days)
python activity_monitor.py --interval month --host 3.88.xx.xx

# Custom date range
python activity_monitor.py --interval custom \
    --start 2026-01-15 --end 2026-02-28 \
    --host 3.88.xx.xx

# Non-default SSH key and remote path
python activity_monitor.py --interval month \
    --host 3.88.xx.xx \
    --key ~/.ssh/my-other-key \
    --remote-path /opt/study-amigo/server

# Already have the DBs locally — skip SSH
python activity_monitor.py --interval week --local-only \
    --admin-db /tmp/dbs/admin.db \
    --user-db-dir /tmp/dbs/user_dbs

# Top 20 students, no per-user breakdown
python activity_monitor.py --interval month --host 3.88.xx.xx \
    --top 20 --no-breakdown
```

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
|---|---|
| `--cache-dir DIR` | Store (and reuse) databases in `DIR` instead of a temp folder |
| `--refresh` | Force a new download even when `--cache-dir` already has data |

### Behaviour

| Situation | What happens |
|---|---|
| No `--cache-dir` | Temp folder created, databases downloaded, folder deleted after run |
| `--cache-dir` set, dir is empty | Databases downloaded and saved in `DIR` |
| `--cache-dir` set, dir already has data | Download skipped; cached files used immediately |
| `--cache-dir` set + `--refresh` | Databases re-downloaded and cached files overwritten |

### Examples

```bash
# First run — downloads and caches
python activity_monitor.py --interval week --host 54.152.109.26 \
    --cache-dir ~/.cache/studyamigo

# Subsequent runs — no download, instant analysis
python activity_monitor.py --interval month --host 54.152.109.26 \
    --cache-dir ~/.cache/studyamigo

# Force fresh data (e.g. after students have been active)
python activity_monitor.py --interval week --host 54.152.109.26 \
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
|---|---|
| `server/tools/activity_monitor.py` | The script itself |
| `server/docs/AWS_DOCKER_DEPLOY.md` | Full EC2 + Docker deployment guide |
| `docker-compose.yml` | Defines the bind-mount that makes host-side DB access possible |
| `docs/ANKI_DB_SCHEMA.md` | Schema reference for `revlog`, `cards`, `notes` |
| `docs/ADMIN_DB_SCHEMA.md` | Schema reference for `admin.db` |

---

## IMPORTANT — Risk of Corrupt Database Copies

### The problem

SQLite uses auxiliary files during write transactions:

- **Journal mode** (default): `<db>-journal` is written alongside the main file during a transaction.
- **WAL mode**: `<db>-wal` and `<db>-shm` are written alongside the main file.

If `scp` copies the `.db` file at the exact moment a write transaction is open (e.g. a student submitting a card review), the copy can land in a **partially-written, inconsistent state** — the journal or WAL file that would complete the transaction is not included.

In practice the risk window is very small (a review write takes milliseconds), so most copies will be fine. However, it is not guaranteed.

> **The live database on the server is never affected.** `scp` only reads; it cannot corrupt the original files.

### Safe alternative: `sqlite3 .backup`

The safest approach is to use SQLite's online backup API via the `sqlite3` CLI on the remote host. This is safe even during concurrent writes:

```bash
# Back up a single user DB safely, then download it
ssh -i ~/.ssh/study-amigo-aws ubuntu@<host> \
    "sqlite3 /opt/study-amigo/server/user_dbs/user_21.db \".backup '/tmp/user_21_safe.db'\""
scp -i ~/.ssh/study-amigo-aws ubuntu@<host>:/tmp/user_21_safe.db ./user_21.db
```

### Mitigation when using this script

If you use `--refresh` to re-download and WAL mode is active, copying the entire `user_dbs/` directory (which this script does) also copies any `.db-wal` and `.db-shm` files that exist alongside the main database. SQLite can reconstruct the correct state from them, so the local copy will be consistent as long as all three files are copied together.

For a monitoring tool where slight inconsistency on one user's stats is acceptable, the current `scp` approach is a reasonable trade-off. For backups intended to be authoritative, use the `sqlite3 .backup` method above.
