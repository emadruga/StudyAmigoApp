#!/usr/bin/env python3
"""
Activity Monitor — StudyAmigo

Analyses card reviews and card creations per day across all users for a
chosen time window, then prints a Top-10 "Most Consistent & Engaged Students"
ranking.

DATA SOURCE (pick one — S3 is the default):

  S3 backup (default — reads the latest automated backup from the bucket):
    python activity_monitor.py --interval week \\
        --bucket study-amigo-backups-645069181643 \\
        --profile study-amigo

    Use the most-recent backup (default when no --week/--day are given):
        python activity_monitor.py --interval week \\
            --bucket study-amigo-backups-645069181643 --profile study-amigo

    Use a specific backup slot:
        python activity_monitor.py --interval week \\
            --bucket study-amigo-backups-645069181643 --profile study-amigo \\
            --week 1 --day friday

    Interactive slot selection (omit --week/--day):
        python activity_monitor.py --interval week \\
            --bucket study-amigo-backups-645069181643 --profile study-amigo \\
            --list-slots

  SSH / live production (old default — copies databases directly from EC2):
    python activity_monitor.py --interval week --host 54.152.109.26

    # Override host / key:
    python activity_monitor.py --interval week \\
        --host 3.88.12.34 \\
        --key ~/.ssh/study-amigo-aws \\
        --remote-path /opt/study-amigo/server

  Local databases (no network required):
    python activity_monitor.py --interval week --local-only \\
        --admin-db /tmp/activity_monitor_dbs/admin.db \\
        --user-db-dir /tmp/activity_monitor_dbs/user_dbs

CACHE:
    Add --cache-dir DIR to keep the downloaded databases between runs.
    Use --refresh to force a fresh download even when the cache is populated.

INTERVALS:
    --interval 24h | week | 2weeks | 3weeks | month | custom
    --start YYYY-MM-DD  (with --interval custom)
    --end   YYYY-MM-DD  (optional, defaults to today)
"""

import argparse
import gzip
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _HAS_ZONEINFO = True
except ImportError:          # Python < 3.9
    _ZoneInfo = None         # type: ignore[assignment,misc]
    _HAS_ZONEINFO = False


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SSH_USER    = "ubuntu"
DEFAULT_SSH_KEY     = os.path.expanduser("~/.ssh/study-amigo-aws")
DEFAULT_REMOTE_PATH = "/opt/study-amigo/server"
DEFAULT_CONTAINER   = "flashcard_server"
DEFAULT_AWS_REGION  = "us-east-1"
DEFAULT_AWS_PROFILE = "study-amigo"

# In-container paths (relative to /app, which is mounted from $REMOTE_PATH)
CONTAINER_ADMIN_DB  = "/app/admin.db"
CONTAINER_USER_DBS  = "/app/user_dbs"

# revlog.id is in milliseconds; cards.id is in milliseconds too
MS = 1_000

# S3 backup slot tables (matches backup_container.sh and APP_BACKUP_RESTORE.md)
DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday",
                "saturday", "sunday"]
WEEK_SLOTS   = [1, 2, 3, 4]
# Reference Saturday 2026-03-14 00:00 UTC (epoch used in the backup rotation)
_REF_EPOCH   = 1_741_910_400


# ─────────────────────────────────────────────────────────────────────────────
# Time window helpers
# ─────────────────────────────────────────────────────────────────────────────

def resolve_interval(interval: str, start: Optional[str], end: Optional[str]) -> Tuple[datetime, datetime]:
    """Return (start_dt, end_dt) in UTC for the chosen interval."""
    now = datetime.now(timezone.utc)

    if interval == "24h":
        return now - timedelta(hours=24), now
    if interval == "week":
        return now - timedelta(weeks=1), now
    if interval == "2weeks":
        return now - timedelta(weeks=2), now
    if interval == "3weeks":
        return now - timedelta(weeks=3), now
    if interval == "month":
        return now - timedelta(days=30), now
    if interval == "custom":
        if not start:
            sys.exit("--interval custom requires --start YYYY-MM-DD")
        start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_dt = (
            datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            if end
            else now.replace(hour=23, minute=59, second=59)
        )
        return start_dt, end_dt

    sys.exit(f"Unknown interval '{interval}'. Choose: 24h, week, 2weeks, 3weeks, month, custom")


def interval_label(start_dt: datetime, end_dt: datetime) -> str:
    fmt = "%Y-%m-%d %H:%M UTC"
    return f"{start_dt.strftime(fmt)}  →  {end_dt.strftime(fmt)}"


# ─────────────────────────────────────────────────────────────────────────────
# S3 backup fetch
# ─────────────────────────────────────────────────────────────────────────────

def _make_s3_client(profile: Optional[str], region: str):
    """Return a boto3 S3 client, importing boto3 lazily."""
    try:
        import boto3
    except ImportError:
        sys.exit(
            "boto3 is required to fetch from S3.\n"
            "Install it with:  pip install boto3"
        )
    if profile:
        return boto3.Session(profile_name=profile, region_name=region).client("s3")
    return boto3.Session(region_name=region).client("s3")


def _derive_bucket(profile: Optional[str], region: str) -> str:
    """Derive bucket name from the AWS account ID (same formula as Terraform)."""
    try:
        import boto3
    except ImportError:
        sys.exit("boto3 is required: pip install boto3")
    kw = {"region_name": region}
    if profile:
        sts = boto3.Session(profile_name=profile, **kw).client("sts")
    else:
        sts = boto3.Session(**kw).client("sts")
    try:
        account_id = sts.get_caller_identity()["Account"]
    except Exception as exc:
        sys.exit(f"Could not determine AWS account ID: {exc}")
    return f"study-amigo-backups-{account_id}"


def _list_s3_backups(s3, bucket: str) -> List[Dict]:
    """
    Return a list of available backup slot dicts, sorted newest-first.
    Each dict has keys: week, day, timestamp, user_db_count, last_modified,
    complete (bool — True when both admin.db.gz and user_dbs.tar.gz exist
    and are non-empty).
    """
    from botocore.exceptions import ClientError

    # First pass: collect all objects keyed by slot prefix
    slot_objects: Dict[str, Dict] = {}   # "week-N/day" -> {filename: size}
    slot_meta: Dict[str, Dict]    = {}   # "week-N/day" -> meta dict
    slot_mtime: Dict[str, object] = {}   # "week-N/day" -> LastModified

    try:
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix="backups/")
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code == "NoSuchBucket":
            return []
        raise

    for page in pages:
        for obj in page.get("Contents", []):
            parts = obj["Key"].split("/")
            # Expect: backups / week-N / day / filename
            if len(parts) != 4:
                continue
            _, week_part, day, fname = parts
            try:
                week = int(week_part.split("-")[1])
            except (IndexError, ValueError):
                continue
            if week not in WEEK_SLOTS or day not in DAYS_OF_WEEK:
                continue

            slot_key = f"week-{week}/{day}"
            slot_objects.setdefault(slot_key, {})
            slot_objects[slot_key][fname] = obj["Size"]

            if fname == "meta.json":
                slot_mtime[slot_key] = obj["LastModified"]
                try:
                    resp = s3.get_object(Bucket=bucket, Key=obj["Key"])
                    slot_meta[slot_key] = json.loads(resp["Body"].read())
                except Exception:
                    slot_meta[slot_key] = {}

    slots: List[Dict] = []
    for slot_key, files in slot_objects.items():
        if "meta.json" not in files:
            continue   # slot has no meta.json — ignore
        week_str, day = slot_key.split("/")
        week = int(week_str.split("-")[1])
        meta = slot_meta.get(slot_key, {})

        admin_size = files.get("admin.db.gz", 0)
        udb_size   = files.get("user_dbs.tar.gz", 0)
        complete   = admin_size > 0 and udb_size > 0

        slots.append({
            "week":          week,
            "day":           day,
            "timestamp":     meta.get("timestamp", "unknown"),
            "user_db_count": meta.get("user_db_count", "?"),
            "last_modified": slot_mtime.get(slot_key),
            "complete":      complete,
            "admin_size":    admin_size,
            "udb_size":      udb_size,
        })

    slots.sort(key=lambda x: x["last_modified"], reverse=True)
    return slots


def _print_s3_listing(slots: List[Dict]) -> None:
    if not slots:
        print("  (Nenhum backup encontrado no bucket.)")
        return
    print(f"\n  {'#':<4} {'Slot':<22} {'Timestamp (UTC)':<24} {'BDs':>5}  {'Status'}")
    print(f"  {'─'*65}")
    for i, s in enumerate(slots, 1):
        slot   = f"week-{s['week']}/{s['day']}"
        status = "OK" if s["complete"] else "INCOMPLETO"
        print(
            f"  {i:<4} {slot:<22} {s['timestamp']:<24} "
            f"{str(s['user_db_count']):>5}  {status}"
        )
    print()


def _resolve_s3_slot(
    slots: List[Dict],
    latest: bool,
    week: Optional[int],
    day: Optional[str],
    list_slots: bool,
) -> Dict:
    """
    Pick a slot from the available list according to the CLI flags.
    Returns the selected slot dict (may be incomplete — caller validates).
    """
    if not slots:
        sys.exit("Nenhum backup encontrado no S3.")

    if list_slots:
        _print_s3_listing(slots)
        try:
            choice = input("  Digite o número do backup a usar (ou Ctrl+C para cancelar): ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(slots):
                sys.exit(f"Escolha inválida: {choice}")
            return slots[idx]
        except (KeyboardInterrupt, EOFError):
            print("\n  Cancelado.")
            sys.exit(0)

    if week is not None and day is not None:
        d = day.lower()
        match = [s for s in slots if s["week"] == week and s["day"] == d]
        if not match:
            _print_s3_listing(slots)
            sys.exit(f"Slot week-{week}/{d} não encontrado no S3.")
        return match[0]

    # Default: most recent
    return slots[0]


def fetch_from_s3(
    bucket: str,
    profile: Optional[str],
    region: str,
    latest: bool,
    week: Optional[int],
    day: Optional[str],
    list_slots: bool,
    dest_dir: Path,
) -> Optional[Tuple[Path, Path]]:
    """
    Download the selected S3 backup slot, decompress the archives into
    dest_dir, and return (admin_db_path, user_dbs_dir).

    Returns None if the bucket is unreachable or contains no backups yet
    (so the caller can offer an SSH fallback).
    """
    from botocore.exceptions import ClientError, NoCredentialsError

    s3 = _make_s3_client(profile, region)

    print(f"\n  Listando backups em s3://{bucket}/backups/ …")
    try:
        slots = _list_s3_backups(s3, bucket)
    except NoCredentialsError:
        sys.exit(
            "Credenciais AWS não encontradas.\n"
            "Use --profile ou configure as variáveis de ambiente AWS_*."
        )
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code == "AccessDenied":
            sys.exit(
                f"Acesso negado ao bucket '{bucket}'.\n"
                "Verifique o perfil AWS e as permissões IAM."
            )
        print(f"  Aviso: erro ao acessar S3: {exc}", file=sys.stderr)
        return None

    if not slots:
        print("  Nenhum backup disponível no bucket ainda.")
        return None

    sel = _resolve_s3_slot(slots, latest, week, day, list_slots)
    w, d = sel["week"], sel["day"]

    # ── Validate slot completeness ────────────────────────────────────────
    if not sel["complete"]:
        slot_label = f"week-{w}/{d}"
        if week is not None and day is not None:
            # User explicitly requested this slot — abort clearly
            print(
                f"\n  ERRO: O slot {slot_label} está incompleto "
                f"(admin.db.gz: {sel['admin_size']} bytes, "
                f"user_dbs.tar.gz: {sel['udb_size']} bytes).\n"
                "  O backup pode ter falhado no meio. "
                "Use --list-slots para ver os slots disponíveis.",
                file=sys.stderr,
            )
            return None

        # Auto-select: skip this slot and look for the first complete one
        print(
            f"  Aviso: slot {slot_label} está incompleto "
            f"(admin: {sel['admin_size']} B, user_dbs: {sel['udb_size']} B) — ignorando."
        )
        complete_slots = [s for s in slots if s["complete"]]
        if not complete_slots:
            print("  Nenhum slot completo encontrado no bucket.")
            return None
        sel = complete_slots[0]
        w, d = sel["week"], sel["day"]
        print(f"  Usando próximo slot completo: week-{w}/{d}  ({sel['timestamp']})")
    else:
        print(f"  Backup selecionado: week-{w}/{d}  ({sel['timestamp']})")

    # ── Download archives ─────────────────────────────────────────────────
    for fname in ("admin.db.gz", "user_dbs.tar.gz"):
        key   = f"backups/week-{w}/{d}/{fname}"
        local = dest_dir / fname
        print(f"  Baixando s3://{bucket}/{key} …")
        try:
            s3.download_file(bucket, key, str(local))
        except ClientError as exc:
            sys.exit(f"Falha no download de {key}: {exc}")
        print(f"    → {local}  ({local.stat().st_size // 1024} KB)")

    # ── Decompress admin.db.gz ────────────────────────────────────────────
    print("  Descomprimindo admin.db.gz …")
    admin_db = dest_dir / "admin.db"
    with gzip.open(str(dest_dir / "admin.db.gz"), "rb") as gz_in:
        admin_db.write_bytes(gz_in.read())

    # ── Extract user_dbs.tar.gz ───────────────────────────────────────────
    # The archive was created with:  tar -czf … -C "${APP_DIR}" user_dbs
    # so entries are  user_dbs/<filename>.  Extracting to dest_dir produces
    # dest_dir/user_dbs/<filename> — the same layout expected by the analysis.
    print("  Extraindo user_dbs.tar.gz …")
    user_dbs_dir = dest_dir / "user_dbs"
    user_dbs_dir.mkdir(exist_ok=True)
    with tarfile.open(str(dest_dir / "user_dbs.tar.gz"), "r:gz") as tar:
        safe_members = [
            m for m in tar.getmembers()
            if m.name.startswith("user_dbs/") and ".." not in m.name
        ]
        tar.extractall(path=str(dest_dir), members=safe_members)

    db_files = list(user_dbs_dir.glob("*.db")) + list(user_dbs_dir.glob("*.anki2"))
    print(f"  {len(db_files)} banco(s) de dados de usuários extraídos.")
    return admin_db, user_dbs_dir


# ─────────────────────────────────────────────────────────────────────────────
# SSH / Docker fetch
# ─────────────────────────────────────────────────────────────────────────────

def check_active_sessions(
    host: str,
    ssh_key: str,
    ssh_user: str,
    remote_path: str,
    minutes: int = 10,
) -> int:
    """
    Return the number of Flask session files modified within the last `minutes`
    minutes on the remote server.

    Flask-Session (filesystem backend) updates a session file's mtime on every
    request, so a recently-modified file means a user made a request in that
    window — a reliable proxy for "someone is actively using the app right now".

    Returns 0 if the check cannot be performed (SSH error, missing directory).
    """
    session_dir = f"{remote_path}/flask_session"
    ssh_args = [
        "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=15",
        "-o", "BatchMode=yes",
    ]
    user_host = f"{ssh_user}@{host}"
    cmd = ["ssh"] + ssh_args + [
        user_host,
        f"find {session_dir} -maxdepth 1 -type f -mmin -{minutes} 2>/dev/null | wc -l",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def _run(cmd: List[str], check=True, capture=False) -> subprocess.CompletedProcess:
    """Run a command, printing it first."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )


def fetch_databases(
    host: str,
    ssh_key: str,
    remote_path: str,
    container: str,
    dest_dir: Path,
) -> Tuple[Path, Path]:
    """
    SSH into the EC2 instance, copy databases from the running Docker container
    to a local temp directory, and return (admin_db_path, user_dbs_dir).

    Strategy: because the server volume is bind-mounted at $remote_path →
    /app inside the container, the files are directly accessible on the host
    at $remote_path/admin.db and $remote_path/user_dbs/. We just scp them.
    """
    ssh_args = ["-i", ssh_key, "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=15"]
    user_host = f"{DEFAULT_SSH_USER}@{host}"

    admin_remote = f"{remote_path}/admin.db"
    # No trailing slash: scp -r copies the directory itself into dest_dir,
    # producing dest_dir/user_dbs/  (not a nested dest_dir/user_dbs/user_dbs/).
    user_dbs_remote = f"{remote_path}/user_dbs"

    print("\n[1/2] Copiando admin.db …")
    _run(["scp"] + ssh_args + [
        f"{user_host}:{admin_remote}",
        str(dest_dir / "admin.db"),
    ])

    print("[2/2] Copiando user_dbs/ …")
    _run(["scp", "-r"] + ssh_args + [
        f"{user_host}:{user_dbs_remote}",
        str(dest_dir),
    ])

    user_dbs_dir = dest_dir / "user_dbs"
    if not user_dbs_dir.exists():
        sys.exit(
            f"Expected {user_dbs_dir} after scp but it does not exist. "
            f"Contents of temp dir: {list(dest_dir.iterdir())}"
        )
    db_files = list(user_dbs_dir.glob("*.db"))
    print(f"  {len(db_files)} banco(s) de dados de usuários baixados.")
    return dest_dir / "admin.db", user_dbs_dir


# ─────────────────────────────────────────────────────────────────────────────
# Database analysis
# ─────────────────────────────────────────────────────────────────────────────

def load_users(admin_db: Path) -> Dict[int, Dict]:
    """Return {user_id: {'username': …, 'name': …}} from admin.db."""
    if not admin_db.exists():
        sys.exit(f"admin.db not found at {admin_db}")
    conn = sqlite3.connect(str(admin_db))
    rows = conn.execute("SELECT user_id, username, name FROM users").fetchall()
    conn.close()
    return {r[0]: {"username": r[1], "name": r[2]} for r in rows}


def find_user_db(user_dbs_dir: Path, username: str) -> Optional[Path]:
    """
    The DB file naming in this project can be either:
      - <username>.anki2   (original scheme per generate_user_timeline.py)
      - user_<id>.db       (scheme shown in AWS_DOCKER_DEPLOY.md)
    We try both.
    """
    # Prefer <username>.anki2
    p1 = user_dbs_dir / f"{username}.anki2"
    if p1.exists():
        return p1
    return None  # caller will fall back to scanning by user_id


def find_user_db_by_id(user_dbs_dir: Path, user_id: int) -> Optional[Path]:
    p = user_dbs_dir / f"user_{user_id}.db"
    if p.exists():
        return p
    return None


def analyse_user_db(
    db_path: Path,
    start_dt: datetime,
    end_dt: datetime,
) -> Dict:
    """
    Return per-day counts of reviews and card creations for one user.

    revlog.id is in **milliseconds** since epoch — reviews.
    cards.id  is in **milliseconds** since epoch — card creation time.
    notes.id  is in **milliseconds** since epoch — note creation time.

    We exclude sample/seed cards (id <= 1700000000000 * 1000) following the
    convention in generate_user_timeline.py (which excludes note_id <= 1700000000000
    for seconds; translate to ms here).
    """
    start_ms = int(start_dt.timestamp() * MS)
    end_ms   = int(end_dt.timestamp()   * MS)

    # Seed cutoff: notes/cards created at or before ~2023-11-14 are sample data.
    SEED_CUTOFF_MS = 1_700_000_000_000  # milliseconds
    # Deck ID 2 is always "Verbal Tenses" — the pre-loaded sample deck.
    # Cards in that deck were created by the server at registration time and
    # must NOT be counted as student-created cards. They ARE still counted
    # in reviews (students review them normally).
    VERBAL_TENSES_DECK_ID = 2

    result: Dict = {
        "reviews_by_day": defaultdict(int),   # "YYYY-MM-DD" -> count
        "creations_by_day": defaultdict(int),
        "total_reviews": 0,
        "total_creations": 0,
        "active_days": set(),
        "ease_dist": defaultdict(int),        # ease 1-4
        "avg_time_ms": 0,                     # average review time
        "reviews_by_hour": defaultdict(int),  # 0-23 (UTC) -> count
        "creations_by_hour": defaultdict(int),# 0-23 (UTC) -> count
    }

    try:
        conn = sqlite3.connect(str(db_path))
    except Exception as e:
        print(f"    Aviso: não foi possível abrir {db_path}: {e}")
        return result

    try:
        # ── Reviews (revlog) ──────────────────────────────────────────────
        rows = conn.execute(
            """
            SELECT id, ease, time
            FROM   revlog
            WHERE  id >= ? AND id <= ?
            """,
            (start_ms, end_ms),
        ).fetchall()

        total_time = 0
        for (rev_id, ease, time_ms) in rows:
            dt = datetime.fromtimestamp(rev_id / MS, tz=timezone.utc)
            day = dt.strftime("%Y-%m-%d")
            result["reviews_by_day"][day] += 1
            result["reviews_by_hour"][dt.hour] += 1
            result["active_days"].add(day)
            result["ease_dist"][ease] += 1
            total_time += time_ms

        result["total_reviews"] = sum(result["reviews_by_day"].values())
        if result["total_reviews"]:
            result["avg_time_ms"] = total_time // result["total_reviews"]

        # ── Card creations (cards.id in ms, exclude seed cards) ───────────
        # Exclude ALL cards in deck 2 ("Verbal Tenses") from new-card counts.
        # Those cards are created by the server at registration time using
        # current_time_ms as the ID — so their IDs are NOT fixed/old; they
        # are as recent as the user's registration date. A timestamp-based
        # cutoff therefore cannot distinguish them. Deck ID 2 is always the
        # pre-loaded sample deck; students never add their own cards there.
        rows = conn.execute(
            """
            SELECT id
            FROM   cards
            WHERE  id >= ? AND id <= ?
              AND  did != ?
            """,
            (start_ms, end_ms, VERBAL_TENSES_DECK_ID),
        ).fetchall()

        for (card_id,) in rows:
            dt = datetime.fromtimestamp(card_id / MS, tz=timezone.utc)
            day = dt.strftime("%Y-%m-%d")
            result["creations_by_day"][day] += 1
            result["creations_by_hour"][dt.hour] += 1
            result["active_days"].add(day)

        result["total_creations"] = sum(result["creations_by_day"].values())

    except Exception as e:
        print(f"    Aviso: erro na consulta em {db_path}: {e}")
    finally:
        conn.close()

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Aggregate & rank
# ─────────────────────────────────────────────────────────────────────────────

def engagement_score(stats: Dict, total_days_in_window: int) -> float:
    """
    Composite score that rewards:
      - consistent daily activity (active_days / window_days, weighted heavily)
      - total volume (reviews + creations, log-scaled so power users don't dwarf everyone)
      - quality of reviews (penalise high 'Again' (ease=1) ratio slightly)
    """
    import math

    active = len(stats["active_days"])
    consistency = active / max(total_days_in_window, 1)  # 0..1

    volume = stats["total_reviews"] + stats["total_creations"]
    volume_score = math.log1p(volume) / math.log1p(500)  # normalise; 500 = reference

    # Again ratio penalty: if >40% of reviews are ease=1, slightly lower score
    total_rev = stats["total_reviews"]
    again_ratio = stats["ease_dist"].get(1, 0) / max(total_rev, 1)
    quality = max(0.5, 1.0 - again_ratio)

    return (consistency * 0.55) + (volume_score * 0.35) + (quality * 0.10)


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

def print_separator(char="─", width=80):
    print(char * width)


def print_daily_summary(
    start_dt: datetime,
    end_dt: datetime,
    all_user_stats: Dict[int, Dict],
    users: Dict[int, Dict],
):
    """Print aggregated per-day table across all users."""
    # Collect all days in window
    delta = end_dt.date() - start_dt.date()
    all_days = [
        (start_dt.date() + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(delta.days + 1)
    ]

    reviews_per_day: Dict[str, int] = defaultdict(int)
    creations_per_day: Dict[str, int] = defaultdict(int)
    active_users_per_day: Dict[str, set] = defaultdict(set)

    for uid, stats in all_user_stats.items():
        for day, cnt in stats["reviews_by_day"].items():
            reviews_per_day[day] += cnt
            active_users_per_day[day].add(uid)
        for day, cnt in stats["creations_by_day"].items():
            creations_per_day[day] += cnt
            active_users_per_day[day].add(uid)

    print_separator("═")
    print("  RESUMO DE ATIVIDADE DIÁRIA")
    print_separator("═")
    print(f"  {'Data':<12}  {'Revisões':>9}  {'Novos Cards':>12}  {'Alunos Ativos':>14}")
    print_separator()

    total_rev = total_cre = total_user_days = 0
    for day in all_days:
        r = reviews_per_day.get(day, 0)
        c = creations_per_day.get(day, 0)
        u = len(active_users_per_day.get(day, set()))
        total_rev += r
        total_cre += c
        total_user_days += u
        marker = " ◀ hoje" if day == datetime.now(timezone.utc).strftime("%Y-%m-%d") else ""
        print(f"  {day:<12}  {r:>9,}  {c:>12,}  {u:>14,}{marker}")

    print_separator()
    print(f"  {'TOTAL':<12}  {total_rev:>9,}  {total_cre:>12,}  {total_user_days:>14,} aluno-dias")
    print()


def print_top10(
    all_user_stats: Dict[int, Dict],
    users: Dict[int, Dict],
    total_days_in_window: int,
):
    """Print Top-10 most consistent & engaged students."""
    ranked = []
    for uid, stats in all_user_stats.items():
        if stats["total_reviews"] + stats["total_creations"] == 0:
            continue
        score = engagement_score(stats, total_days_in_window)
        ranked.append((uid, score, stats))

    ranked.sort(key=lambda x: -x[1])

    print_separator("═")
    print("  TOP-10 ALUNOS MAIS CONSISTENTES E ENGAJADOS")
    print_separator("═")

    header = (
        f"  {'#':<3}  {'Nome Completo':<28}  "
        f"{'Dias':>5}  {'Revisões':>9}  {'Novos Cards':>13}  "
        f"{'Tempo Médio':>11}  {'Score':>6}"
    )
    print(header)
    print_separator()

    for rank, (uid, score, stats) in enumerate(ranked[:10], start=1):
        uinfo = users.get(uid, {"name": "?", "username": "?"})
        name = uinfo["name"][:28]
        active = len(stats["active_days"])
        reviews = stats["total_reviews"]
        creations = stats["total_creations"]
        avg_s = stats["avg_time_ms"] / 1000
        avg_fmt = f"{avg_s:.1f}s" if avg_s < 60 else f"{avg_s/60:.1f}m"

        print(
            f"  {rank:<3}  {name:<28}  "
            f"{active:>5}  {reviews:>9,}  {creations:>13,}  "
            f"{avg_fmt:>11}  {score:>6.3f}"
        )

    if not ranked:
        print("  (nenhuma atividade encontrada neste período)")
    print()


def print_per_user_breakdown(
    all_user_stats: Dict[int, Dict],
    users: Dict[int, Dict],
    total_days_in_window: int,
    top_n: int = 10,
):
    """Show detailed breakdown for the top-N most active users."""
    ranked = sorted(
        [(uid, s) for uid, s in all_user_stats.items()
         if s["total_reviews"] + s["total_creations"] > 0],
        key=lambda x: -(x[1]["total_reviews"] + x[1]["total_creations"]),
    )

    print_separator("═")
    print(f"  DETALHAMENTO POR ALUNO  (top {min(top_n, len(ranked))} por volume)")
    print_separator("═")

    for uid, stats in ranked[:top_n]:
        uinfo = users.get(uid, {"name": "?", "username": "?"})
        score = engagement_score(stats, total_days_in_window)
        ease = stats["ease_dist"]
        total_rev = stats["total_reviews"]

        print(f"\n  {uinfo['name']}")
        print(f"    Revisões:       {total_rev:,}")
        print(f"    Novos cards:   {stats['total_creations']:,}")
        print(f"    Dias ativos:    {len(stats['active_days'])} / {total_days_in_window}")
        print(f"    Tempo médio:    {stats['avg_time_ms']/1000:.1f}s")
        if total_rev:
            print(
                f"    Distribuição:   Errou={ease.get(1,0)} ({ease.get(1,0)*100//total_rev}%)  "
                f"Difícil={ease.get(2,0)}  Bom={ease.get(3,0)}  Fácil={ease.get(4,0)}"
            )
        print(f"    Engajamento:    {score:.3f}")
    print()


def _resolve_tz_offset(tz_name: str) -> Tuple[float, str]:
    """
    Return (utc_offset_hours, display_label) for the given IANA timezone name.

    Uses zoneinfo (stdlib, Python ≥ 3.9). Falls back to UTC=0 with a warning
    on older interpreters or unknown timezone strings.
    The offset reflects the timezone's current wall-clock offset including DST.
    Non-integer offsets (e.g. India UTC+5:30) are kept as floats; the hour
    shift applied to the buckets rounds to the nearest whole hour.
    """
    if tz_name.upper() == "UTC":
        return 0.0, "UTC"
    if not _HAS_ZONEINFO:
        print(
            f"  Aviso: zoneinfo não disponível (Python < 3.9). "
            f"Ignorando --timezone '{tz_name}'; usando UTC.",
            file=sys.stderr,
        )
        return 0.0, "UTC"
    try:
        tz = _ZoneInfo(tz_name)
        offset_secs = datetime.now(tz).utcoffset().total_seconds()
        offset_h = offset_secs / 3600
        sign = "+" if offset_h >= 0 else ""
        label = f"{tz_name}  (UTC{sign}{offset_h:g}h)"
        return offset_h, label
    except Exception as exc:
        print(
            f"  Aviso: timezone desconhecido '{tz_name}' ({exc}). Usando UTC.",
            file=sys.stderr,
        )
        return 0.0, "UTC"


def _shift_hour_buckets(by_hour: Dict[int, int], offset_h: float) -> Dict[int, int]:
    """Shift UTC hour buckets by offset_h (rounded to nearest whole hour)."""
    shift = round(offset_h)
    shifted: Dict[int, int] = defaultdict(int)
    for h, cnt in by_hour.items():
        shifted[(h + shift) % 24] += cnt
    return shifted


def print_top_hours(
    all_user_stats: Dict[int, Dict],
    top_n: int = 5,
    timezone_name: str = "UTC",
) -> None:
    """
    Print the top-N most popular hours of the day for reviews and card
    creations, aggregated across all users within the analysis window.

    Raw data is always stored in UTC. Pass timezone_name (IANA name, e.g.
    'America/Sao_Paulo') to display hours converted to that timezone.
    """
    reviews_by_hour: Dict[int, int] = defaultdict(int)
    creations_by_hour: Dict[int, int] = defaultdict(int)

    for stats in all_user_stats.values():
        for h, cnt in stats["reviews_by_hour"].items():
            reviews_by_hour[h] += cnt
        for h, cnt in stats["creations_by_hour"].items():
            creations_by_hour[h] += cnt

    offset_h, tz_label = _resolve_tz_offset(timezone_name)
    if offset_h != 0.0:
        reviews_by_hour   = _shift_hour_buckets(reviews_by_hour,   offset_h)
        creations_by_hour = _shift_hour_buckets(creations_by_hour, offset_h)

    total_reviews   = sum(reviews_by_hour.values())
    total_creations = sum(creations_by_hour.values())

    def bar(count: int, total: int, width: int = 20) -> str:
        filled = round(width * count / total) if total else 0
        return "█" * filled + "░" * (width - filled)

    print_separator("═")
    print(f"  TOP {top_n} HORÁRIOS DO DIA — REVISÕES  ({tz_label})")
    print_separator("═")
    if total_reviews == 0:
        print("  (sem dados de revisão no período)")
    else:
        ranked = sorted(reviews_by_hour.items(), key=lambda x: -x[1])
        print(f"  {'#':<3}  {'Horário':<13}  {'Revisões':>9}  {'% Total':>7}  {'':20}")
        print_separator()
        for rank, (hour, cnt) in enumerate(ranked[:top_n], start=1):
            pct = cnt * 100 / total_reviews
            slot = f"{hour:02d}:00–{(hour+1)%24:02d}:00"
            print(f"  {rank:<3}  {slot:<13}  {cnt:>9,}  {pct:>6.1f}%  {bar(cnt, total_reviews)}")
    print()

    print_separator("═")
    print(f"  TOP {top_n} HORÁRIOS DO DIA — CRIAÇÃO DE CARDS  ({tz_label})")
    print_separator("═")
    if total_creations == 0:
        print("  (sem dados de criação no período)")
    else:
        ranked = sorted(creations_by_hour.items(), key=lambda x: -x[1])
        print(f"  {'#':<3}  {'Horário':<13}  {'Criações':>9}  {'% Total':>7}  {'':20}")
        print_separator()
        for rank, (hour, cnt) in enumerate(ranked[:top_n], start=1):
            pct = cnt * 100 / total_creations
            slot = f"{hour:02d}:00–{(hour+1)%24:02d}:00"
            print(f"  {rank:<3}  {slot:<13}  {cnt:>9,}  {pct:>6.1f}%  {bar(cnt, total_creations)}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Analyse flashcard activity across all users. "
            "By default, fetches databases from the latest S3 backup."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Time window ────────────────────────────────────────────────────────
    parser.add_argument(
        "--interval",
        choices=["24h", "week", "2weeks", "3weeks", "month", "custom"],
        default="week",
        help="Analysis window (default: week)",
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="Custom start date (inclusive)")
    parser.add_argument("--end",   metavar="YYYY-MM-DD", help="Custom end date (inclusive)")

    # ── S3 source (default) ────────────────────────────────────────────────
    s3_group = parser.add_argument_group(
        "S3 backup source (default — preferred over SSH)"
    )
    s3_group.add_argument(
        "--bucket", default=None, metavar="BUCKET",
        help=(
            "S3 bucket name (e.g. study-amigo-backups-645069181643). "
            "If omitted, derived automatically from the AWS account ID."
        ),
    )
    s3_group.add_argument(
        "--profile", default=DEFAULT_AWS_PROFILE, metavar="PROFILE",
        help=f"AWS CLI profile for S3 access (default: {DEFAULT_AWS_PROFILE})",
    )
    s3_group.add_argument(
        "--region", default=DEFAULT_AWS_REGION, metavar="REGION",
        help=f"AWS region (default: {DEFAULT_AWS_REGION})",
    )
    s3_group.add_argument(
        "--latest", action="store_true",
        help="Use the most-recent S3 backup slot (default when no --week/--day are given)",
    )
    s3_group.add_argument(
        "--week", type=int, choices=WEEK_SLOTS, metavar="N",
        help="S3 backup week slot to use (1-4)",
    )
    s3_group.add_argument(
        "--day", choices=DAYS_OF_WEEK, metavar="DAY",
        help="S3 backup day to use (monday..sunday)",
    )
    s3_group.add_argument(
        "--list-slots", action="store_true",
        help="List available S3 backup slots interactively before analysis",
    )

    # ── SSH source (legacy / live production) ─────────────────────────────
    ssh_group = parser.add_argument_group(
        "SSH source (live production — used when --host is provided)"
    )
    ssh_group.add_argument(
        "--host", default=None,
        help="EC2 Elastic IP or hostname; activates SSH fetch instead of S3",
    )
    ssh_group.add_argument("--key",   default=DEFAULT_SSH_KEY,
                           help=f"SSH private key path (default: {DEFAULT_SSH_KEY})")
    ssh_group.add_argument("--user",  default=DEFAULT_SSH_USER,
                           help=f"SSH user (default: {DEFAULT_SSH_USER})")
    ssh_group.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH,
                           help=f"Server directory on EC2 (default: {DEFAULT_REMOTE_PATH})")
    ssh_group.add_argument("--container", default=DEFAULT_CONTAINER,
                           help=f"Docker container name (default: {DEFAULT_CONTAINER})")

    # ── Local-only source ─────────────────────────────────────────────────
    local_group = parser.add_argument_group("Local source (skip all network access)")
    local_group.add_argument(
        "--local-only", action="store_true",
        help="Analyse databases already present locally; requires --admin-db and --user-db-dir",
    )
    local_group.add_argument("--admin-db",    default=None,
                             help="Local path to admin.db (with --local-only)")
    local_group.add_argument("--user-db-dir", default=None,
                             help="Local path to user_dbs/ dir (with --local-only)")

    # ── Cache ──────────────────────────────────────────────────────────────
    parser.add_argument(
        "--cache-dir", default=None, metavar="DIR",
        help=(
            "Persist fetched databases in DIR instead of a temp folder. "
            "Subsequent runs skip the download when data is already there. "
            "Use --refresh to force a new download."
        ),
    )
    parser.add_argument(
        "--refresh", action="store_true",
        help="Force re-download even when --cache-dir already has data",
    )

    # ── Output ─────────────────────────────────────────────────────────────
    parser.add_argument("--top", type=int, default=10,
                        help="How many users to show in the ranking (default: 10)")
    parser.add_argument("--no-breakdown", action="store_true",
                        help="Skip the per-user detailed breakdown section")
    parser.add_argument(
        "--timezone", default="UTC", metavar="TZ",
        help=(
            "IANA timezone for the hour-of-day report "
            "(e.g. America/Sao_Paulo, America/New_York, Europe/Lisbon). "
            "Default: UTC. Requires Python ≥ 3.9."
        ),
    )

    args = parser.parse_args()

    # ── Resolve time window ────────────────────────────────────────────────
    start_dt, end_dt = resolve_interval(args.interval, args.start, args.end)
    total_days = max(1, (end_dt.date() - start_dt.date()).days + 1)

    print()
    print_separator("═")
    print("  StudyAmigo — Monitor de Atividade")
    print_separator("═")
    print(f"  Período : {interval_label(start_dt, end_dt)}")
    print(f"  Dias    : {total_days}")
    print()

    # ── Determine data source & fetch databases ────────────────────────────
    tmp_dir = None

    if args.local_only:
        # ── Local mode ────────────────────────────────────────────────────
        if not args.admin_db or not args.user_db_dir:
            sys.exit(
                "--local-only requires --admin-db <path> and --user-db-dir <path>"
            )
        admin_db     = Path(args.admin_db)
        user_dbs_dir = Path(args.user_db_dir)
        print(f"  Fonte: local  ({admin_db.parent})")

    elif args.host:
        # ── SSH mode (explicit --host) ─────────────────────────────────────
        print(f"  Fonte: SSH → {args.host}")
        if args.cache_dir:
            fetch_dir = Path(args.cache_dir)
            fetch_dir.mkdir(parents=True, exist_ok=True)
        else:
            tmp_dir   = Path(tempfile.mkdtemp(prefix="activity_monitor_"))
            fetch_dir = tmp_dir

        cached_admin    = fetch_dir / "admin.db"
        cached_user_dbs = fetch_dir / "user_dbs"
        already_cached  = (
            cached_admin.exists()
            and cached_user_dbs.is_dir()
            and any(cached_user_dbs.glob("*.db"))
        )

        if already_cached and not args.refresh:
            db_count = len(list(cached_user_dbs.glob("*.db")))
            print(f"  Usando cache em {fetch_dir}  ({db_count} BDs de usuários)")
            print("  (use --refresh para forçar novo download)")
        else:
            if already_cached and args.refresh:
                print(f"  --refresh solicitado; baixando novamente em {fetch_dir}")

            print("  Verificando sessões ativas nos últimos 10 minutos …")
            active = check_active_sessions(
                host=args.host,
                ssh_key=args.key,
                ssh_user=args.user,
                remote_path=args.remote_path,
            )
            if active > 0:
                print(f"\n  ⚠  ATENÇÃO: {active} sessão(ões) ativa(s) detectada(s)!")
                print("     Usuários podem estar em plena revisão agora.")
                print("     O download copia os arquivos SQLite ao vivo, o que pode")
                print("     capturar um estado inconsistente do banco de dados.\n")
                answer = input("  Deseja continuar com o download mesmo assim? [s/N] ").strip().lower()
                if answer not in ("s", "sim", "y", "yes"):
                    print("\n  Download cancelado. Tente novamente mais tarde.")
                    if tmp_dir:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                    sys.exit(0)
                print()
            else:
                print("  Nenhuma sessão ativa. Prosseguindo com o download.\n")

            try:
                fetch_databases(
                    host=args.host,
                    ssh_key=args.key,
                    remote_path=args.remote_path,
                    container=args.container,
                    dest_dir=fetch_dir,
                )
            except subprocess.CalledProcessError as e:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                sys.exit(f"\nFalha no SSH/SCP: {e}")

        admin_db     = cached_admin
        user_dbs_dir = cached_user_dbs

    else:
        # ── S3 mode (default) ─────────────────────────────────────────────
        # Derive bucket name if not supplied
        bucket = args.bucket
        if not bucket:
            print("  --bucket não fornecido; derivando nome do bucket via STS …")
            bucket = _derive_bucket(args.profile, args.region)
            print(f"  Bucket: {bucket}")

        print(f"  Fonte: S3  ({bucket})")

        if args.cache_dir:
            fetch_dir = Path(args.cache_dir)
            fetch_dir.mkdir(parents=True, exist_ok=True)
        else:
            tmp_dir   = Path(tempfile.mkdtemp(prefix="activity_monitor_"))
            fetch_dir = tmp_dir

        cached_admin    = fetch_dir / "admin.db"
        cached_user_dbs = fetch_dir / "user_dbs"
        already_cached  = (
            cached_admin.exists()
            and cached_user_dbs.is_dir()
            and (
                any(cached_user_dbs.glob("*.db"))
                or any(cached_user_dbs.glob("*.anki2"))
            )
        )

        if already_cached and not args.refresh and not args.list_slots:
            db_count = (
                len(list(cached_user_dbs.glob("*.db")))
                + len(list(cached_user_dbs.glob("*.anki2")))
            )
            print(f"  Usando cache em {fetch_dir}  ({db_count} BDs de usuários)")
            print("  (use --refresh para forçar novo download)")
            admin_db     = cached_admin
            user_dbs_dir = cached_user_dbs
        else:
            if already_cached and args.refresh:
                print(f"  --refresh solicitado; baixando novamente em {fetch_dir}")

            result = fetch_from_s3(
                bucket     = bucket,
                profile    = args.profile,
                region     = args.region,
                latest     = args.latest,
                week       = args.week,
                day        = args.day,
                list_slots = args.list_slots,
                dest_dir   = fetch_dir,
            )

            if result is None:
                # No S3 backup available — offer SSH fallback
                print(
                    "\n  Nenhum backup disponível no S3 ainda.\n"
                    "  Deseja buscar os bancos de dados diretamente da produção via SSH?\n"
                    f"  (Host padrão: 54.152.109.26, chave: {DEFAULT_SSH_KEY})"
                )
                answer = input("\n  Buscar da produção via SSH? [s/N] ").strip().lower()
                if answer not in ("s", "sim", "y", "yes"):
                    print("\n  Operação cancelada.")
                    if tmp_dir:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                    sys.exit(0)

                ssh_host = input(
                    f"  IP do EC2 [{DEFAULT_SSH_KEY.split('/')[-1]}] "
                    "(Enter = 54.152.109.26): "
                ).strip() or "54.152.109.26"

                print("  Verificando sessões ativas …")
                active = check_active_sessions(
                    host=ssh_host,
                    ssh_key=DEFAULT_SSH_KEY,
                    ssh_user=DEFAULT_SSH_USER,
                    remote_path=DEFAULT_REMOTE_PATH,
                )
                if active > 0:
                    print(f"\n  ⚠  {active} sessão(ões) ativa(s). Continuar mesmo assim? [s/N] ", end="")
                    if input().strip().lower() not in ("s", "sim", "y", "yes"):
                        if tmp_dir:
                            shutil.rmtree(tmp_dir, ignore_errors=True)
                        sys.exit(0)

                try:
                    fetch_databases(
                        host=ssh_host,
                        ssh_key=DEFAULT_SSH_KEY,
                        remote_path=DEFAULT_REMOTE_PATH,
                        container=DEFAULT_CONTAINER,
                        dest_dir=fetch_dir,
                    )
                except subprocess.CalledProcessError as e:
                    if tmp_dir:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                    sys.exit(f"\nFalha no SSH/SCP: {e}")

                admin_db     = fetch_dir / "admin.db"
                user_dbs_dir = fetch_dir / "user_dbs"
            else:
                admin_db, user_dbs_dir = result

    # ── Load user list ─────────────────────────────────────────────────────
    print("\nCarregando usuários do admin.db …")
    users = load_users(admin_db)
    print(f"  {len(users)} usuário(s) encontrado(s).")

    # ── Analyse each user ──────────────────────────────────────────────────
    print(f"\nAnalisando bancos de dados em {user_dbs_dir} …")
    all_user_stats: Dict[int, Dict] = {}

    for uid, uinfo in sorted(users.items()):
        db_path = find_user_db(user_dbs_dir, uinfo["username"])
        if db_path is None:
            db_path = find_user_db_by_id(user_dbs_dir, uid)
        if db_path is None:
            print(f"  [{uid}] {uinfo['username']} — banco de dados não encontrado, ignorando")
            continue

        print(f"  [{uid}] {uinfo['username']} ({uinfo['name']}) — {db_path.name}")
        stats = analyse_user_db(db_path, start_dt, end_dt)
        all_user_stats[uid] = stats

    if not all_user_stats:
        print("\nNenhum banco de dados de usuário encontrado. Sem dados para reportar.")
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    # ── Reports ────────────────────────────────────────────────────────────
    print()
    print_daily_summary(start_dt, end_dt, all_user_stats, users)
    print_top10(all_user_stats, users, total_days)

    if not args.no_breakdown:
        print_per_user_breakdown(all_user_stats, users, total_days, top_n=args.top)

    print_top_hours(all_user_stats, top_n=5, timezone_name=args.timezone)

    # ── Cleanup ────────────────────────────────────────────────────────────
    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print("  (arquivos temporários removidos)")
    elif args.cache_dir:
        print(f"  (bancos de dados mantidos em cache: {args.cache_dir})")


if __name__ == "__main__":
    main()
