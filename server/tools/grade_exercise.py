#!/usr/bin/env python3
"""
grade_exercise.py — StudyAmigo Exercise Grader

Computes individual student grades for a single exercise (E01, E02, …) using
the four-component formula defined in ASSESSMENT_COMPONENT_COMPUTATION.md:

    Grade = 0.25 × V  +  0.25 × C  +  0.30 × Q  +  0.20 × E

Components:
    V — Volume      (25 %): review count + card-creation count (min-max, p95 cap)
    C — Consistency (25 %): participation × anti-cramming distribution
    Q — Quality     (30 %): retention rate × maturity (ivl ≥ 21 d)
    E — Engagement  (20 %): review-time quality × ease-factor health

When --no-card-creation is set (e.g. E01, where the deck is pre-loaded and
students do not create cards), card counts are excluded from the Volume
component and the formula collapses to V = reviews_sub.

A placement-exam roster CSV (--roster) is cross-referenced to identify
students who completed the placement exam but never opened Study Amigo.

DATA SOURCE (same options as activity_monitor.py):

  S3 backup (default):
    python grade_exercise.py --interval custom --start 2026-03-01 --end 2026-03-23 \\
        --label E01 --no-card-creation \\
        --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \\
        --bucket study-amigo-backups-645069181643 --profile study-amigo

  Local databases:
    python grade_exercise.py --interval custom --start 2026-03-01 --end 2026-03-23 \\
        --label E01 --no-card-creation \\
        --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \\
        --local-only \\
        --admin-db ~/.cache/studyamigo/20260323/admin.db \\
        --user-db-dir ~/.cache/studyamigo/20260323/user_dbs

  SSH (live production):
    python grade_exercise.py --interval custom --start 2026-03-01 --end 2026-03-23 \\
        --label E01 --no-card-creation \\
        --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \\
        --host 54.152.109.26

OUTPUT:
    Prints a summary to stdout and writes a CSV to <label>_grades_<date>.csv
    (override with --output).
"""

import argparse
import csv
import difflib
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

import numpy as np

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _HAS_ZONEINFO = True
except ImportError:
    _ZoneInfo = None          # type: ignore[assignment,misc]
    _HAS_ZONEINFO = False


# ─────────────────────────────────────────────────────────────────────────────
# Constants (shared with activity_monitor.py)
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SSH_USER    = "ubuntu"
DEFAULT_SSH_KEY     = os.path.expanduser("~/.ssh/study-amigo-aws")
DEFAULT_REMOTE_PATH = "/opt/study-amigo/server"
DEFAULT_CONTAINER   = "flashcard_server"
DEFAULT_AWS_REGION  = "us-east-1"
DEFAULT_AWS_PROFILE = "study-amigo"

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday",
                "saturday", "sunday"]
WEEK_SLOTS   = [1, 2, 3, 4]

MS = 1_000   # revlog.id is in milliseconds

# Cards in the pre-loaded "Verbal Tenses" deck (deck id 2) are never counted
# as student-created cards — they are seeded at registration time.
VERBAL_TENSES_DECK_ID = 2

# Engagement thresholds (calibrated from E07 data — ASSESSMENT_COMPONENT_COMPUTATION.md § 4.1)
TIME_LOWER_MS  = 2_000    # below this: mechanical click
TIME_UPPER_MS  = 60_000   # at exactly this: Anki timer timeout artifact — exclude

# Ease factor range (cards.factor × 1000)
EASE_MIN  = 1_300
EASE_MAX  = 3_500

# Maturity threshold
MATURE_IVL = 21  # days


# ─────────────────────────────────────────────────────────────────────────────
# Time-window helpers  (identical to activity_monitor.py)
# ─────────────────────────────────────────────────────────────────────────────

def resolve_interval(interval: str, start: Optional[str], end: Optional[str]) -> Tuple[datetime, datetime]:
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
            datetime.strptime(end, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc)
            if end
            else now.replace(hour=23, minute=59, second=59)
        )
        return start_dt, end_dt
    sys.exit(f"Unknown interval '{interval}'. Choose: 24h, week, 2weeks, 3weeks, month, custom")


def interval_label(start_dt: datetime, end_dt: datetime) -> str:
    fmt = "%Y-%m-%d"
    return f"{start_dt.strftime(fmt)} → {end_dt.strftime(fmt)}"


# ─────────────────────────────────────────────────────────────────────────────
# S3 backup fetch  (copied verbatim from activity_monitor.py)
# ─────────────────────────────────────────────────────────────────────────────

_REF_EPOCH = 1_741_910_400


def _make_s3_client(profile: Optional[str], region: str):
    try:
        import boto3
    except ImportError:
        sys.exit("boto3 is required: pip install boto3")
    if profile:
        return boto3.Session(profile_name=profile, region_name=region).client("s3")
    return boto3.Session(region_name=region).client("s3")


def _derive_bucket(profile: Optional[str], region: str) -> str:
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
    from botocore.exceptions import ClientError
    slot_objects: Dict[str, Dict] = {}
    slot_meta:    Dict[str, Dict] = {}
    slot_mtime:   Dict[str, object] = {}
    try:
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix="backups/")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchBucket":
            return []
        raise
    for page in pages:
        for obj in page.get("Contents", []):
            parts = obj["Key"].split("/")
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
            continue
        week_str, day = slot_key.split("/")
        week = int(week_str.split("-")[1])
        meta = slot_meta.get(slot_key, {})
        admin_size = files.get("admin.db.gz", 0)
        udb_size   = files.get("user_dbs.tar.gz", 0)
        slots.append({
            "week": week, "day": day,
            "timestamp": meta.get("timestamp", "unknown"),
            "user_db_count": meta.get("user_db_count", "?"),
            "last_modified": slot_mtime.get(slot_key),
            "complete": admin_size > 0 and udb_size > 0,
            "admin_size": admin_size, "udb_size": udb_size,
        })
    slots.sort(key=lambda x: x["last_modified"], reverse=True)
    return slots


def _resolve_s3_slot(slots, latest, week, day, list_slots) -> Dict:
    if not slots:
        sys.exit("Nenhum backup encontrado no S3.")
    if list_slots:
        for i, s in enumerate(slots, 1):
            slot = f"week-{s['week']}/{s['day']}"
            status = "OK" if s["complete"] else "INCOMPLETO"
            print(f"  {i:<4} {slot:<22} {s['timestamp']:<24} {status}")
        try:
            choice = input("  Número do backup: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(slots):
                sys.exit(f"Escolha inválida: {choice}")
            return slots[idx]
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
    if week is not None and day is not None:
        match = [s for s in slots if s["week"] == week and s["day"] == day.lower()]
        if not match:
            sys.exit(f"Slot week-{week}/{day} não encontrado.")
        return match[0]
    return slots[0]


def fetch_from_s3(bucket, profile, region, latest, week, day, list_slots, dest_dir) -> Optional[Tuple[Path, Path]]:
    from botocore.exceptions import ClientError, NoCredentialsError
    s3 = _make_s3_client(profile, region)
    print(f"\n  Listando backups em s3://{bucket}/backups/ …")
    try:
        slots = _list_s3_backups(s3, bucket)
    except NoCredentialsError:
        sys.exit("Credenciais AWS não encontradas.")
    except ClientError as exc:
        print(f"  Aviso: erro ao acessar S3: {exc}", file=sys.stderr)
        return None
    if not slots:
        print("  Nenhum backup disponível.")
        return None
    sel = _resolve_s3_slot(slots, latest, week, day, list_slots)
    w, d = sel["week"], sel["day"]
    if not sel["complete"]:
        complete_slots = [s for s in slots if s["complete"]]
        if not complete_slots:
            print("  Nenhum slot completo encontrado.")
            return None
        sel = complete_slots[0]
        w, d = sel["week"], sel["day"]
    print(f"  Backup: week-{w}/{d}  ({sel['timestamp']})")
    for fname in ("admin.db.gz", "user_dbs.tar.gz"):
        key   = f"backups/week-{w}/{d}/{fname}"
        local = dest_dir / fname
        print(f"  Baixando {key} …")
        try:
            s3.download_file(bucket, key, str(local))
        except ClientError as exc:
            sys.exit(f"Falha no download de {key}: {exc}")
    admin_db = dest_dir / "admin.db"
    with gzip.open(str(dest_dir / "admin.db.gz"), "rb") as gz_in:
        admin_db.write_bytes(gz_in.read())
    user_dbs_dir = dest_dir / "user_dbs"
    user_dbs_dir.mkdir(exist_ok=True)
    with tarfile.open(str(dest_dir / "user_dbs.tar.gz"), "r:gz") as tar:
        safe = [m for m in tar.getmembers()
                if m.name.startswith("user_dbs/") and ".." not in m.name]
        tar.extractall(path=str(dest_dir), members=safe)
    return admin_db, user_dbs_dir


def fetch_databases(host, ssh_key, remote_path, container, dest_dir) -> Tuple[Path, Path]:
    ssh_args = ["-i", ssh_key, "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15"]
    user_host = f"{DEFAULT_SSH_USER}@{host}"
    print("\n[1/2] Copiando admin.db …")
    subprocess.run(["scp"] + ssh_args + [f"{user_host}:{remote_path}/admin.db",
                    str(dest_dir / "admin.db")], check=True)
    print("[2/2] Copiando user_dbs/ …")
    subprocess.run(["scp", "-r"] + ssh_args + [f"{user_host}:{remote_path}/user_dbs",
                    str(dest_dir)], check=True)
    user_dbs_dir = dest_dir / "user_dbs"
    if not user_dbs_dir.exists():
        sys.exit(f"user_dbs not found after scp in {dest_dir}")
    return dest_dir / "admin.db", user_dbs_dir


# ─────────────────────────────────────────────────────────────────────────────
# Admin DB
# ─────────────────────────────────────────────────────────────────────────────

def load_users(admin_db: Path) -> Dict[int, Dict]:
    """Return {user_id: {'username': …, 'name': …}}."""
    if not admin_db.exists():
        sys.exit(f"admin.db not found at {admin_db}")
    conn = sqlite3.connect(str(admin_db))
    rows = conn.execute("SELECT user_id, username, name FROM users").fetchall()
    conn.close()
    return {r[0]: {"username": r[1], "name": r[2]} for r in rows}


def find_user_db_by_id(user_dbs_dir: Path, user_id: int) -> Optional[Path]:
    p = user_dbs_dir / f"user_{user_id}.db"
    if p.exists():
        return p
    # Also try .anki2 by username — not used here, ID-based is canonical
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Roster loading & name matching
# ─────────────────────────────────────────────────────────────────────────────

def load_roster(roster_path: Path) -> List[Dict]:
    """
    Parse the placement-exam roster CSV.

    Expected columns (case-insensitive):
        Course, ID, Name, Email, Path, Suggested Tier
    Returns a list of dicts with keys: course, student_id, name, email, path, tier
    """
    if not roster_path.exists():
        sys.exit(f"Roster not found: {roster_path}")
    students = []
    with open(roster_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalise header keys to lowercase
        for row in reader:
            norm = {k.strip().lower(): v.strip() for k, v in row.items()}
            students.append({
                "course":     norm.get("course", ""),
                "student_id": norm.get("id", ""),
                "name":       norm.get("name", ""),
                "email":      norm.get("email", ""),
                "path":       norm.get("path", ""),
                "tier":       norm.get("suggested tier", norm.get("tier", "")),
                # matched admin user_id — filled in during matching
                "user_id":    None,
            })
    return students


def _normalise_name(s: str) -> str:
    """Lowercase, strip accents roughly, remove punctuation — for fuzzy matching."""
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # strip combining chars
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def match_roster_to_admin(roster: List[Dict], users: Dict[int, Dict]) -> None:
    """
    Mutate roster entries in-place, setting 'user_id' to the best-matching
    admin DB user using a greedy one-to-one stable assignment.

    Strategy:
    1. Compute all (roster_student, admin_uid, score) triples.
    2. Sort descending by score.
    3. Greedily assign: each admin uid can be claimed by at most one roster
       student; each roster student gets at most one uid.
    4. Accept only if score >= MATCH_THRESHOLD.

    Duplicate accounts (same person, multiple user_ids in admin DB) are NOT
    deduplicated here — all of them are left available.  The grading step later
    picks the account with the most non-cram reviews for each matched student.
    To allow this, duplicate admin users with an identical normalised name are
    treated as a single "slot" that can be claimed once; all uids sharing that
    normalised name are then assigned to the winning roster student.
    """
    MATCH_THRESHOLD = 0.55

    # Build normalised name → list of uids (handles duplicate accounts)
    admin_norm_to_uids: Dict[str, List[int]] = defaultdict(list)
    for uid, info in users.items():
        admin_norm_to_uids[_normalise_name(info["name"])].append(uid)

    # All unique admin "name slots" (one entry per distinct normalised name)
    admin_slots = list(admin_norm_to_uids.keys())

    # Compute all pairwise similarities
    triples: List[Tuple[float, int, str]] = []  # (score, roster_index, admin_slot)
    for i, student in enumerate(roster):
        target = _normalise_name(student["name"])
        for slot in admin_slots:
            score = difflib.SequenceMatcher(None, target, slot).ratio()
            if score >= MATCH_THRESHOLD:
                triples.append((score, i, slot))

    # Greedy one-to-one assignment (highest scores first)
    triples.sort(key=lambda t: -t[0])
    assigned_roster: set = set()
    assigned_slots:  set = set()

    for score, i, slot in triples:
        if i in assigned_roster or slot in assigned_slots:
            continue
        # Assign ALL uids sharing this normalised admin name to roster[i]
        # (covers duplicate accounts — grading will pick the best one)
        uids = admin_norm_to_uids[slot]
        roster[i]["user_id"]       = uids[0]    # primary uid
        roster[i]["_matched_uids"] = uids        # all duplicate uids
        assigned_roster.add(i)
        assigned_slots.add(slot)

    # Students with no assignment remain user_id = None


# ─────────────────────────────────────────────────────────────────────────────
# Per-student grading queries
# ─────────────────────────────────────────────────────────────────────────────

def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * MS)


def grade_user_db(
    db_path: Path,
    start_dt: datetime,
    end_dt: datetime,
    grade_card_creation: bool,
) -> Dict:
    """
    Query one student's .db file and return raw metrics needed for grading.

    Keys returned:
        total_reviews_raw   — all revlog rows in window (no type filter)
        total_reviews       — non-cram reviews (type != 3)
        cards_created       — non-Verbal-Tenses cards created in window
                              (0 when grade_card_creation=False)
        review_days         — distinct UTC days with non-cram reviews
        last_day_reviews    — non-cram reviews on end_dt's calendar day
        ret_total           — type IN (1,2) non-cram reviews
        ret_ok              — of those, ease >= 3
        mature_cards        — cards with ivl >= 21 reviewed in window
        total_reviewed_cards— distinct cards reviewed in window
        time_total          — reviews with time < 60000 (cram excluded)
        time_engaged        — of those, time >= 2000
        mean_factor         — avg cards.factor for reviewed cards
        time_data_missing   — bool: all non-cram reviews have time=0
    """
    start_ms   = _ms(start_dt)
    end_ms     = _ms(end_dt)
    last_day_start_ms = _ms(
        end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    )

    zero: Dict = {
        "total_reviews_raw": 0,
        "total_reviews": 0,
        "cards_created": 0,
        "review_days": 0,
        "last_day_reviews": 0,
        "ret_total": 0,
        "ret_ok": 0,
        "mature_cards": 0,
        "total_reviewed_cards": 0,
        "time_total": 0,
        "time_engaged": 0,
        "mean_factor": 2500.0,
        "time_data_missing": False,
    }

    try:
        conn = sqlite3.connect(str(db_path))
    except Exception as e:
        print(f"    Aviso: não foi possível abrir {db_path}: {e}", file=sys.stderr)
        return zero

    try:
        cur = conn.cursor()

        # ── Volume: total non-cram reviews ────────────────────────────────
        r = cur.execute(
            "SELECT COUNT(*) FROM revlog WHERE id BETWEEN ? AND ? AND type != 3",
            (start_ms, end_ms),
        ).fetchone()
        total_reviews = r[0] if r else 0

        # ── Volume: raw review count (for reference) ──────────────────────
        r = cur.execute(
            "SELECT COUNT(*) FROM revlog WHERE id BETWEEN ? AND ?",
            (start_ms, end_ms),
        ).fetchone()
        total_reviews_raw = r[0] if r else 0

        # ── Volume: card creations (excluded when grade_card_creation=False) ─
        cards_created = 0
        if grade_card_creation:
            r = cur.execute(
                "SELECT COUNT(*) FROM cards WHERE id BETWEEN ? AND ? AND did != ?",
                (start_ms, end_ms, VERBAL_TENSES_DECK_ID),
            ).fetchone()
            cards_created = r[0] if r else 0

        # ── Consistency: review days ───────────────────────────────────────
        r = cur.execute(
            """SELECT COUNT(DISTINCT DATE(id / 1000, 'unixepoch'))
               FROM revlog
               WHERE id BETWEEN ? AND ? AND type != 3""",
            (start_ms, end_ms),
        ).fetchone()
        review_days = r[0] if r else 0

        # ── Consistency: last-day reviews ─────────────────────────────────
        r = cur.execute(
            "SELECT COUNT(*) FROM revlog WHERE id BETWEEN ? AND ? AND type != 3",
            (last_day_start_ms, end_ms),
        ).fetchone()
        last_day_reviews = r[0] if r else 0

        # ── Quality: retention (type 1 = review, 2 = relearn only) ────────
        r = cur.execute(
            """SELECT COUNT(*),
                      SUM(CASE WHEN ease >= 3 THEN 1 ELSE 0 END)
               FROM revlog
               WHERE id BETWEEN ? AND ? AND type IN (1, 2)""",
            (start_ms, end_ms),
        ).fetchone()
        ret_total = r[0] if r else 0
        ret_ok    = (r[1] or 0) if r else 0

        # ── Quality: maturity (reviewed cards with ivl >= 21) ─────────────
        # Use fallback: cards reviewed in window (E01 is review-only, no creation)
        r = cur.execute(
            """SELECT COUNT(DISTINCT c.id),
                      SUM(CASE WHEN c.ivl >= ? THEN 1 ELSE 0 END)
               FROM cards c
               WHERE c.id IN (
                   SELECT DISTINCT cid FROM revlog
                   WHERE id BETWEEN ? AND ?
               )""",
            (MATURE_IVL, start_ms, end_ms),
        ).fetchone()
        total_reviewed_cards = r[0] if r else 0
        mature_cards         = (r[1] or 0) if r else 0

        # ── Engagement: time quality ───────────────────────────────────────
        r = cur.execute(
            """SELECT COUNT(*) FILTER (WHERE time < ?),
                      COUNT(*) FILTER (WHERE time >= ? AND time < ?)
               FROM revlog
               WHERE id BETWEEN ? AND ? AND type != 3""",
            (TIME_UPPER_MS, TIME_LOWER_MS, TIME_UPPER_MS, start_ms, end_ms),
        ).fetchone()
        time_total   = r[0] if r else 0
        time_engaged = r[1] if r else 0

        # ── Engagement: detect zero-time (older Anki clients) ─────────────
        r = cur.execute(
            "SELECT CASE WHEN MAX(time) = 0 THEN 1 ELSE 0 END FROM revlog WHERE type != 3",
        ).fetchone()
        time_data_missing = bool(r[0]) if r and r[0] is not None else False

        # ── Engagement: mean ease factor ──────────────────────────────────
        r = cur.execute(
            """SELECT AVG(c.factor) FROM cards c
               WHERE c.id IN (
                   SELECT DISTINCT cid FROM revlog
                   WHERE id BETWEEN ? AND ?
               )""",
            (start_ms, end_ms),
        ).fetchone()
        mean_factor = r[0] if (r and r[0] is not None) else 2500.0

    except Exception as e:
        print(f"    Aviso: erro na consulta em {db_path}: {e}", file=sys.stderr)
        conn.close()
        return zero
    finally:
        conn.close()

    return {
        "total_reviews_raw":   total_reviews_raw,
        "total_reviews":       total_reviews,
        "cards_created":       cards_created,
        "review_days":         review_days,
        "last_day_reviews":    last_day_reviews,
        "ret_total":           ret_total,
        "ret_ok":              ret_ok,
        "mature_cards":        mature_cards,
        "total_reviewed_cards": total_reviewed_cards,
        "time_total":          time_total,
        "time_engaged":        time_engaged,
        "mean_factor":         mean_factor,
        "time_data_missing":   time_data_missing,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Score computation
# ─────────────────────────────────────────────────────────────────────────────

def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _minmax_sub(value: float, all_values: List[float]) -> float:
    """Normalize value to [0, 100] using class-level min-max with p95 cap."""
    if not all_values:
        return 0.0
    lo = float(np.min(all_values))
    hi = float(np.percentile(all_values, 95))
    if hi == lo:
        return 100.0 if value >= hi else 0.0
    return float(np.clip((value - lo) / (hi - lo) * 100, 0, 100))


def compute_scores(
    raw: Dict,
    grade_card_creation: bool,
    # Pre-computed class-level normalization vectors (non-zero active students only)
    all_reviews: List[float],
    all_cards: List[float],
) -> Dict:
    """
    Given raw metrics for one student and class-level vectors, return:
        V, C, Q, E, grade  (all in [0, 100])
        plus retention_pct, maturity_pct, time_sub, ease_sub, cramming_ratio
    """
    # ── Volume ────────────────────────────────────────────────────────────
    reviews_sub = _minmax_sub(raw["total_reviews"], all_reviews)

    if grade_card_creation and all_cards:
        cards_sub = _minmax_sub(raw["cards_created"], all_cards)
        V = 0.40 * cards_sub + 0.60 * reviews_sub
    else:
        cards_sub = 0.0
        V = reviews_sub

    # ── Consistency ───────────────────────────────────────────────────────
    participation = 100.0 if raw["total_reviews"] > 0 else 0.0

    total_rev = raw["total_reviews"]
    if total_rev > 0:
        cramming_ratio = raw["last_day_reviews"] / total_rev
    else:
        cramming_ratio = 0.0
    distribution_sub = _clip((1.0 - cramming_ratio) * 100.0)

    C = 0.50 * participation + 0.50 * distribution_sub

    # ── Quality ───────────────────────────────────────────────────────────
    if raw["ret_total"] > 0:
        retention_pct = raw["ret_ok"] / raw["ret_total"] * 100.0
    else:
        retention_pct = 0.0

    if raw["total_reviewed_cards"] > 0:
        maturity_pct = raw["mature_cards"] / raw["total_reviewed_cards"] * 100.0
    else:
        maturity_pct = 0.0

    Q = _clip(0.70 * retention_pct + 0.30 * maturity_pct)

    # ── Engagement ────────────────────────────────────────────────────────
    if raw["time_data_missing"]:
        time_sub = None  # will use ease-only formula
    elif raw["time_total"] > 0:
        time_sub = raw["time_engaged"] / raw["time_total"] * 100.0
    else:
        time_sub = 0.0

    ease_sub = _clip(
        (raw["mean_factor"] - EASE_MIN) / (EASE_MAX - EASE_MIN) * 100.0
    )

    if time_sub is None:
        E = ease_sub
        time_sub_display = float("nan")
    else:
        E = 0.50 * time_sub + 0.50 * ease_sub
        time_sub_display = time_sub

    # ── Final grade ───────────────────────────────────────────────────────
    grade = 0.25 * V + 0.25 * C + 0.30 * Q + 0.20 * E

    return {
        "V": round(V, 1),
        "C": round(C, 1),
        "Q": round(Q, 1),
        "E": round(E, 1),
        "grade": round(grade, 1),
        "reviews_sub": round(reviews_sub, 1),
        "cards_sub": round(cards_sub, 1),
        "participation": round(participation, 1),
        "cramming_ratio": round(cramming_ratio, 3),
        "distribution_sub": round(distribution_sub, 1),
        "retention_pct": round(retention_pct, 1),
        "maturity_pct": round(maturity_pct, 1),
        "time_sub": round(time_sub_display, 1) if not (time_sub is None) else None,
        "ease_sub": round(ease_sub, 1),
        "time_data_missing": raw["time_data_missing"],
    }


def grade_letter(score: float) -> str:
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


# ─────────────────────────────────────────────────────────────────────────────
# Suspicious-behaviour flags
# ─────────────────────────────────────────────────────────────────────────────

def behaviour_flags(raw: Dict, scores: Dict) -> List[str]:
    flags = []
    # 100% retention with >= 30 type-1/2 reviews (very unlikely without cheating)
    if raw["ret_total"] >= 30 and scores["retention_pct"] >= 100.0:
        flags.append("RET100")
    # Low time sub (< 30%) with >= 20 reviews
    ts = scores.get("time_sub")
    if ts is not None and not (ts != ts) and ts < 30.0 and raw["total_reviews"] >= 20:
        flags.append("LOW_TIME")
    # Very high cram ratio (> 80%)
    if scores["cramming_ratio"] > 0.80 and raw["total_reviews"] >= 20:
        flags.append("CRAM")
    return flags


# ─────────────────────────────────────────────────────────────────────────────
# Printing helpers
# ─────────────────────────────────────────────────────────────────────────────

SEP = "─" * 110
SEP2 = "═" * 110


def _fmt_nan(v, fmt=".1f") -> str:
    if v is None or (isinstance(v, float) and v != v):
        return "  n/a"
    return f"{v:{fmt}}"


def print_section(title: str):
    print()
    print(SEP2)
    print(f"  {title}")
    print(SEP2)


def print_ranked_table(rows: List[Dict], title: str, top_n: int, reverse: bool = True):
    """
    rows: list of result dicts, each with keys: name, student_id, course, tier,
          grade, V, C, Q, E, total_reviews, review_days, retention_pct,
          maturity_pct, flags_str
    """
    print_section(title)
    hdr = (
        f"  {'#':<3}  {'Nome':<34}  {'ID':>5}  {'Curso':<22}  {'Tier':<6}"
        f"  {'Rev':>5}  {'Dias':>4}  {'Ret%':>5}  {'Mat%':>5}"
        f"  {'V':>5}  {'C':>5}  {'Q':>5}  {'E':>5}  {'Nota':>5}  {'L':<1}  Flags"
    )
    print(hdr)
    print(SEP)
    sorted_rows = sorted(rows, key=lambda r: r["grade"], reverse=reverse)[:top_n]
    for i, r in enumerate(sorted_rows, 1):
        name = r["name"][:34]
        crs  = r["course"][:22]
        print(
            f"  {i:<3}  {name:<34}  {r['student_id']:>5}  {crs:<22}  {r['tier']:<6}"
            f"  {r['total_reviews']:>5}  {r['review_days']:>4}"
            f"  {r['retention_pct']:>5.1f}  {r['maturity_pct']:>5.1f}"
            f"  {r['V']:>5.1f}  {r['C']:>5.1f}  {r['Q']:>5.1f}  {r['E']:>5.1f}"
            f"  {r['grade']:>5.1f}  {grade_letter(r['grade']):<1}  {r['flags_str']}"
        )


def print_inactive_table(inactive: List[Dict]):
    print_section("ALUNOS SEM ATIVIDADE NO STUDY AMIGO")
    sub_no_acct  = [s for s in inactive if s["user_id"] is None]
    sub_no_revs  = [s for s in inactive if s["user_id"] is not None]

    if sub_no_acct:
        print(f"\n  Sem conta cadastrada ({len(sub_no_acct)} aluno(s)):\n")
        print(f"  {'ID':>5}  {'Nome':<38}  {'Curso':<24}  {'Tier':<8}  Email")
        print("  " + "─" * 100)
        for s in sorted(sub_no_acct, key=lambda x: x["student_id"]):
            print(f"  {s['student_id']:>5}  {s['name']:<38}  {s['course']:<24}"
                  f"  {s['tier']:<8}  {s['email']}")

    if sub_no_revs:
        print(f"\n  Conta existente, sem revisões ({len(sub_no_revs)} aluno(s)):\n")
        print(f"  {'ID':>5}  {'Nome':<38}  {'Curso':<24}  {'Tier':<8}  Email")
        print("  " + "─" * 100)
        for s in sorted(sub_no_revs, key=lambda x: x["student_id"]):
            print(f"  {s['student_id']:>5}  {s['name']:<38}  {s['course']:<24}"
                  f"  {s['tier']:<8}  {s['email']}")

    print(f"\n  Total sem atividade: {len(inactive)} aluno(s) "
          f"({len(sub_no_acct)} sem conta, {len(sub_no_revs)} sem revisões)")


# ─────────────────────────────────────────────────────────────────────────────
# CSV output
# ─────────────────────────────────────────────────────────────────────────────

CSV_FIELDS = [
    "student_id", "name", "course", "tier", "path",
    "email", "user_id", "username",
    "total_reviews", "total_reviews_raw", "cards_created", "review_days",
    "last_day_reviews", "cramming_ratio",
    "ret_total", "ret_ok", "retention_pct",
    "total_reviewed_cards", "mature_cards", "maturity_pct",
    "time_total", "time_engaged", "time_sub", "ease_sub", "mean_factor",
    "time_data_missing",
    "V", "C", "Q", "E", "grade", "grade_letter",
    "flags",
]


def write_csv(output_path: Path, results: List[Dict]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"\n  CSV gravado em: {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compute individual student grades for a StudyAmigo exercise. "
            "Reads from S3 backup (default), SSH, or local databases."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Exercise settings ──────────────────────────────────────────────────
    parser.add_argument(
        "--label", default="E??", metavar="LABEL",
        help="Exercise label, e.g. E01, E02 (used in output filenames and headers)",
    )
    parser.add_argument(
        "--no-card-creation", action="store_true",
        help=(
            "Exclude card-creation counts from the Volume component. "
            "Use for exercises where the deck is pre-loaded (e.g. E01)."
        ),
    )
    parser.add_argument(
        "--roster", default=None, metavar="CSV",
        help=(
            "Path to the placement-exam roster CSV. When provided, students in "
            "the roster who have no activity are listed separately."
        ),
    )

    # ── Time window ────────────────────────────────────────────────────────
    parser.add_argument(
        "--interval",
        choices=["24h", "week", "2weeks", "3weeks", "month", "custom"],
        default="week",
        help="Analysis window (default: week). Use 'custom' with --start / --end.",
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="Custom start date (inclusive)")
    parser.add_argument("--end",   metavar="YYYY-MM-DD", help="Custom end date (inclusive, default: today)")

    # ── S3 source (default) ────────────────────────────────────────────────
    s3g = parser.add_argument_group("S3 backup source (default)")
    s3g.add_argument("--bucket",     default=None,               metavar="BUCKET")
    s3g.add_argument("--profile",    default=DEFAULT_AWS_PROFILE, metavar="PROFILE")
    s3g.add_argument("--region",     default=DEFAULT_AWS_REGION,  metavar="REGION")
    s3g.add_argument("--latest",     action="store_true")
    s3g.add_argument("--week",       type=int, choices=WEEK_SLOTS, metavar="N")
    s3g.add_argument("--day",        choices=DAYS_OF_WEEK,         metavar="DAY")
    s3g.add_argument("--list-slots", action="store_true")

    # ── SSH source ─────────────────────────────────────────────────────────
    sshg = parser.add_argument_group("SSH source (live production)")
    sshg.add_argument("--host",        default=None)
    sshg.add_argument("--key",         default=DEFAULT_SSH_KEY)
    sshg.add_argument("--user",        default=DEFAULT_SSH_USER)
    sshg.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH)
    sshg.add_argument("--container",   default=DEFAULT_CONTAINER)

    # ── Local source ───────────────────────────────────────────────────────
    locg = parser.add_argument_group("Local source (no network)")
    locg.add_argument("--local-only",  action="store_true")
    locg.add_argument("--admin-db",    default=None)
    locg.add_argument("--user-db-dir", default=None)

    # ── Cache ──────────────────────────────────────────────────────────────
    parser.add_argument("--cache-dir", default=None, metavar="DIR")
    parser.add_argument("--refresh",   action="store_true")

    # ── Output ─────────────────────────────────────────────────────────────
    parser.add_argument(
        "--output", default=None, metavar="FILE",
        help="CSV output path (default: <label>_grades_<YYYYMMDD>.csv)",
    )
    parser.add_argument(
        "--top", type=int, default=10,
        help="How many students to show in Top / Bottom tables (default: 10)",
    )

    args = parser.parse_args()

    grade_card_creation = not args.no_card_creation

    # ── Resolve time window ────────────────────────────────────────────────
    start_dt, end_dt = resolve_interval(args.interval, args.start, args.end)
    total_days = max(1, (end_dt.date() - start_dt.date()).days + 1)

    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    output_path = Path(args.output) if args.output else Path(f"{args.label}_grades_{today_str}.csv")

    print()
    print(SEP2)
    print(f"  StudyAmigo — Avaliação de Exercício  [{args.label}]")
    print(SEP2)
    print(f"  Período   : {interval_label(start_dt, end_dt)}  ({total_days} dias)")
    print(f"  Criação   : {'incluída' if grade_card_creation else 'excluída (--no-card-creation)'}")
    print(f"  Fórmula   : Grade = 0.25×V + 0.25×C + 0.30×Q + 0.20×E")
    print(f"  Q         : 0.70 × Retenção + 0.30 × Maturidade (ivl ≥ {MATURE_IVL}d)")
    print()

    # ── Fetch databases ────────────────────────────────────────────────────
    tmp_dir = None

    if args.local_only:
        if not args.admin_db or not args.user_db_dir:
            sys.exit("--local-only requires --admin-db and --user-db-dir")
        admin_db     = Path(args.admin_db)
        user_dbs_dir = Path(args.user_db_dir)
        print(f"  Fonte: local  ({admin_db.parent})")

    elif args.host:
        print(f"  Fonte: SSH → {args.host}")
        fetch_dir = Path(args.cache_dir) if args.cache_dir else Path(tempfile.mkdtemp(prefix="grade_ex_"))
        if not args.cache_dir:
            tmp_dir = fetch_dir
        fetch_dir.mkdir(parents=True, exist_ok=True)
        cached_admin    = fetch_dir / "admin.db"
        cached_user_dbs = fetch_dir / "user_dbs"
        if not (cached_admin.exists() and cached_user_dbs.is_dir()) or args.refresh:
            try:
                fetch_databases(args.host, args.key, args.remote_path,
                                args.container, fetch_dir)
            except subprocess.CalledProcessError as e:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                sys.exit(f"SSH/SCP falhou: {e}")
        admin_db     = cached_admin
        user_dbs_dir = cached_user_dbs

    else:
        bucket = args.bucket
        if not bucket:
            print("  Derivando nome do bucket via STS …")
            bucket = _derive_bucket(args.profile, args.region)
        print(f"  Fonte: S3  ({bucket})")
        fetch_dir = Path(args.cache_dir) if args.cache_dir else Path(tempfile.mkdtemp(prefix="grade_ex_"))
        if not args.cache_dir:
            tmp_dir = fetch_dir
        fetch_dir.mkdir(parents=True, exist_ok=True)
        cached_admin    = fetch_dir / "admin.db"
        cached_user_dbs = fetch_dir / "user_dbs"
        already_cached  = (cached_admin.exists() and cached_user_dbs.is_dir()
                           and any(cached_user_dbs.glob("*.db")))
        if not already_cached or args.refresh:
            result = fetch_from_s3(bucket, args.profile, args.region,
                                   args.latest, args.week, args.day,
                                   args.list_slots, fetch_dir)
            if result is None:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                sys.exit("Não foi possível obter os dados do S3.")
        else:
            print(f"  Usando cache em {fetch_dir}")
        admin_db     = cached_admin
        user_dbs_dir = cached_user_dbs

    # ── Load users ─────────────────────────────────────────────────────────
    users = load_users(admin_db)
    print(f"\n  {len(users)} usuário(s) em admin.db")

    # ── Load roster (optional) ─────────────────────────────────────────────
    roster: List[Dict] = []
    if args.roster:
        roster = load_roster(Path(args.roster))
        match_roster_to_admin(roster, users)
        print(f"  {len(roster)} aluno(s) no roster  ({args.roster})")

    # ── Collect raw metrics for every user with a DB ───────────────────────
    print("\n  Analisando bancos de dados …")

    raw_by_uid: Dict[int, Dict] = {}
    for uid in users:
        db_path = find_user_db_by_id(user_dbs_dir, uid)
        if db_path is None:
            continue
        raw_by_uid[uid] = grade_user_db(db_path, start_dt, end_dt, grade_card_creation)

    active_uids = {uid for uid, raw in raw_by_uid.items() if raw["total_reviews"] > 0}
    print(f"  {len(raw_by_uid)} banco(s) encontrado(s), {len(active_uids)} com atividade no período")

    # ── Class-level normalization vectors (active students only) ──────────
    all_reviews = [raw_by_uid[uid]["total_reviews"] for uid in active_uids]
    all_cards   = [raw_by_uid[uid]["cards_created"]  for uid in active_uids] if grade_card_creation else []

    if all_reviews:
        print(f"\n  Normalização de Volume:")
        print(f"    Revisões  — mín={min(all_reviews)}, p95={np.percentile(all_reviews, 95):.0f}, máx={max(all_reviews)}")
        if all_cards:
            print(f"    Criações  — mín={min(all_cards)}, p95={np.percentile(all_cards, 95):.0f}, máx={max(all_cards)}")

    # ── Score every user ──────────────────────────────────────────────────
    all_results: List[Dict] = []
    for uid, raw in raw_by_uid.items():
        uinfo = users[uid]
        if raw["total_reviews"] == 0:
            # Zero grade — inactive
            scores = {
                "V": 0.0, "C": 0.0, "Q": 0.0, "E": 0.0, "grade": 0.0,
                "reviews_sub": 0.0, "cards_sub": 0.0,
                "participation": 0.0, "cramming_ratio": 0.0, "distribution_sub": 0.0,
                "retention_pct": 0.0, "maturity_pct": 0.0,
                "time_sub": None, "ease_sub": 0.0, "time_data_missing": False,
            }
        else:
            scores = compute_scores(raw, grade_card_creation, all_reviews, all_cards)

        flags   = behaviour_flags(raw, scores) if raw["total_reviews"] > 0 else []
        ts_val  = scores["time_sub"]
        ts_disp = ts_val if ts_val is not None else float("nan")

        all_results.append({
            # identity
            "user_id":  uid,
            "username": uinfo["username"],
            "name":     uinfo["name"],
            "student_id": "",   # filled from roster match below
            "course":    "",
            "tier":      "",
            "path":      "",
            "email":     "",
            # raw
            "total_reviews":      raw["total_reviews"],
            "total_reviews_raw":  raw["total_reviews_raw"],
            "cards_created":      raw["cards_created"],
            "review_days":        raw["review_days"],
            "last_day_reviews":   raw["last_day_reviews"],
            "cramming_ratio":     scores["cramming_ratio"],
            "ret_total":          raw["ret_total"],
            "ret_ok":             raw["ret_ok"],
            "retention_pct":      scores["retention_pct"],
            "total_reviewed_cards": raw["total_reviewed_cards"],
            "mature_cards":       raw["mature_cards"],
            "maturity_pct":       scores["maturity_pct"],
            "time_total":         raw["time_total"],
            "time_engaged":       raw["time_engaged"],
            "time_sub":           ts_disp,
            "ease_sub":           scores["ease_sub"],
            "mean_factor":        round(raw["mean_factor"], 1),
            "time_data_missing":  raw["time_data_missing"],
            # scores
            "V": scores["V"], "C": scores["C"], "Q": scores["Q"], "E": scores["E"],
            "grade": scores["grade"],
            "grade_letter": grade_letter(scores["grade"]),
            "flags": " ".join(flags),
            "flags_str": " ".join(flags),
        })

    # ── Merge roster metadata into results ─────────────────────────────────
    # Build uid→roster map (for the primary/best account per roster student)
    uid_to_roster: Dict[int, Dict] = {}
    if roster:
        for s in roster:
            if s["user_id"] is None:
                continue
            # All admin uids matched to this student (covers duplicate accounts)
            cands = s.get("_matched_uids", [s["user_id"]])
            # Pick the one with the most non-cram reviews in the window
            best_uid = max(
                (uid for uid in cands if uid in raw_by_uid),
                key=lambda uid: raw_by_uid[uid]["total_reviews"],
                default=s["user_id"],
            )
            uid_to_roster[best_uid] = s

    for r in all_results:
        if r["user_id"] in uid_to_roster:
            s = uid_to_roster[r["user_id"]]
            r["student_id"] = s["student_id"]
            r["course"]     = s["course"]
            r["tier"]       = s["tier"]
            r["path"]       = s["path"]
            r["email"]      = s["email"]

    # ── Identify inactive roster students ─────────────────────────────────
    inactive_roster: List[Dict] = []
    if roster:
        for s in roster:
            matched_uids = s.get("_matched_uids", ([s["user_id"]] if s["user_id"] else []))
            # No match at all → no account
            if not matched_uids:
                inactive_roster.append(s)
                continue
            # Matched: check if ANY of the matched uids has reviews
            any_active = any(
                raw_by_uid.get(uid, {}).get("total_reviews", 0) > 0
                for uid in matched_uids
            )
            if not any_active:
                inactive_roster.append(s)

    # ── Filter: only roster students for ranked tables (when roster given) ─
    if roster:
        ranked_pool = [r for r in all_results
                       if r["student_id"] and r["total_reviews"] > 0]
    else:
        ranked_pool = [r for r in all_results if r["total_reviews"] > 0]

    # ── Summary stats ──────────────────────────────────────────────────────
    print_section(f"SUMÁRIO — {args.label}  |  {interval_label(start_dt, end_dt)}")

    n_active = len(ranked_pool)
    n_inactive = len(inactive_roster) if roster else 0
    n_roster = len(roster) if roster else len(all_results)

    if ranked_pool:
        grades = [r["grade"] for r in ranked_pool]
        print(f"  Exercício      : {args.label}")
        print(f"  Período        : {interval_label(start_dt, end_dt)}  ({total_days} dias)")
        print(f"  Turma          : {n_roster} alunos no roster  |  {n_active} ativos  |  {n_inactive} sem atividade")
        print(f"  Revisões       : mín={min(r['total_reviews'] for r in ranked_pool)}"
              f"  méd={sum(r['total_reviews'] for r in ranked_pool)/n_active:.0f}"
              f"  máx={max(r['total_reviews'] for r in ranked_pool)}")
        print(f"  Nota média     : {sum(grades)/len(grades):.1f}")
        print(f"  Nota mediana   : {float(np.median(grades)):.1f}")
        print(f"  Nota máxima    : {max(grades):.1f}")
        print(f"  Nota mínima    : {min(grades):.1f}")

        by_letter = defaultdict(int)
        for g in grades:
            by_letter[grade_letter(g)] += 1
        dist = "  ".join(f"{l}={by_letter[l]}" for l in ["A","B","C","D","F"])
        print(f"  Distribuição   : {dist}")

        # Per-course summary
        if any(r["course"] for r in ranked_pool):
            courses = sorted({r["course"] for r in ranked_pool if r["course"]})
            print(f"\n  {'Curso':<26}  {'Ativos':>6}  {'Nota méd':>8}  {'Rev méd':>7}")
            print("  " + "─" * 55)
            for crs in courses:
                crs_rows = [r for r in ranked_pool if r["course"] == crs]
                crs_grades = [r["grade"] for r in crs_rows]
                crs_revs   = [r["total_reviews"] for r in crs_rows]
                print(f"  {crs:<26}  {len(crs_rows):>6}  {sum(crs_grades)/len(crs_grades):>8.1f}"
                      f"  {sum(crs_revs)/len(crs_revs):>7.0f}")

        # Suspicious-flag summary
        flagged = [r for r in ranked_pool if r["flags_str"]]
        if flagged:
            print(f"\n  ⚠  {len(flagged)} aluno(s) com flags de comportamento suspeito:")
            for r in sorted(flagged, key=lambda x: x["grade"], reverse=True):
                print(f"     [{r['student_id'] or r['user_id']}] {r['name'][:36]}  — {r['flags_str']}")

    # ── Top N ──────────────────────────────────────────────────────────────
    if ranked_pool:
        print_ranked_table(ranked_pool, f"TOP {args.top} — {args.label}", args.top, reverse=True)
        print_ranked_table(ranked_pool, f"BOTTOM {args.top} — {args.label}", args.top, reverse=False)

    # ── Inactive roster students ───────────────────────────────────────────
    if inactive_roster:
        print_inactive_table(inactive_roster)
    elif roster:
        print("\n  Todos os alunos do roster tiveram pelo menos uma revisão.")

    # ── Write CSV ──────────────────────────────────────────────────────────
    # Include all users (active + inactive from admin DB) plus roster-only
    # entries with zero grade for roster students that had no activity
    csv_rows = list(all_results)
    # Add roster-only rows for students with no account
    for s in inactive_roster:
        if s["user_id"] is None:
            csv_rows.append({f: "" for f in CSV_FIELDS} | {
                "student_id": s["student_id"],
                "name":       s["name"],
                "course":     s["course"],
                "tier":       s["tier"],
                "path":       s["path"],
                "email":      s["email"],
                "user_id":    "",
                "username":   "",
                "total_reviews": 0,
                "grade": 0.0,
                "grade_letter": "F",
                "flags": "NO_ACCOUNT",
                "flags_str": "NO_ACCOUNT",
                **{k: 0 for k in ["total_reviews_raw","cards_created","review_days",
                                   "last_day_reviews","ret_total","ret_ok",
                                   "total_reviewed_cards","mature_cards",
                                   "time_total","time_engaged"]},
                "cramming_ratio": 0.0, "retention_pct": 0.0, "maturity_pct": 0.0,
                "time_sub": "", "ease_sub": 0.0, "mean_factor": 0.0,
                "time_data_missing": False,
                "V": 0.0, "C": 0.0, "Q": 0.0, "E": 0.0,
            })

    write_csv(output_path, csv_rows)

    # Cleanup temp dir
    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print()
    print(SEP2)
    print(f"  Concluído.  Grade = 0.25×V + 0.25×C + 0.30×Q + 0.20×E  [{args.label}]")
    print(SEP2)
    print()


if __name__ == "__main__":
    main()
