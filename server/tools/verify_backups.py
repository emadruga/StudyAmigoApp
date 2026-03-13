#!/usr/bin/env python3
"""
verify_backups.py — StudyAmigo S3 Backup Verifier

Connects to the backup S3 bucket and produces a 28-slot grid showing the
status of every backup (week-1..4 × monday..sunday).

Usage (from your Mac):
    python3 server/tools/verify_backups.py --bucket study-amigo-backups-<ACCOUNT_ID>

    # specify a non-default AWS profile
    python3 server/tools/verify_backups.py \\
        --bucket study-amigo-backups-123456789012 \\
        --profile study-amigo

    # also download and verify gzip integrity of each archive
    python3 server/tools/verify_backups.py \\
        --bucket study-amigo-backups-123456789012 \\
        --verify-integrity

Exit codes:
    0  — all 28 slots are present and healthy
    1  — one or more slots are missing or corrupt
"""

import argparse
import gzip
import io
import json
import sys
import tarfile
from datetime import datetime, timezone, timedelta

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEK_SLOTS   = [1, 2, 3, 4]
REQUIRED_FILES = {"admin.db.gz", "user_dbs.tar.gz", "meta.json"}

# Reference: Saturday 2026-03-14 00:00:00 UTC — start of week-slot 1
REF_EPOCH = 1741910400

# ANSI colours (disabled automatically if not a TTY)
def _is_tty() -> bool:
    return sys.stdout.isatty()

RED    = "\033[31m" if _is_tty() else ""
GREEN  = "\033[32m" if _is_tty() else ""
YELLOW = "\033[33m" if _is_tty() else ""
CYAN   = "\033[36m" if _is_tty() else ""
BOLD   = "\033[1m"  if _is_tty() else ""
RESET  = "\033[0m"  if _is_tty() else ""


# ---------------------------------------------------------------------------
# Slot helpers
# ---------------------------------------------------------------------------

def current_week_slot() -> tuple[int, str]:
    """Return (week_slot 1..4, day_of_week) for right now."""
    import time
    now = int(time.time())
    days_since = max(0, (now - REF_EPOCH) // 86400)
    slot = (days_since // 7) % 4 + 1
    dow  = datetime.now(timezone.utc).strftime("%A").lower()
    return slot, dow


def slot_label(week: int, day: str, current_week: int, current_day: str) -> str:
    if week == current_week and day == current_day:
        return f"{BOLD}{CYAN}► week-{week}/{day}{RESET}"
    return f"  week-{week}/{day}"


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

def list_bucket_index(s3_client, bucket: str) -> dict:
    """
    Walk s3://bucket/backups/ and return a nested dict:
        index[week_slot][day] = {
            'admin.db.gz':     {'size': int, 'last_modified': datetime},
            'user_dbs.tar.gz': {...},
            'meta.json':       {...},
        }
    """
    index: dict = {}

    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix="backups/")

    for page in pages:
        for obj in page.get("Contents", []):
            # key format: backups/week-{N}/{day}/{filename}
            parts = obj["Key"].split("/")
            if len(parts) != 4:
                continue
            _, week_part, day, filename = parts
            if not week_part.startswith("week-"):
                continue
            try:
                week = int(week_part.split("-")[1])
            except (IndexError, ValueError):
                continue
            if week not in WEEK_SLOTS or day not in DAYS_OF_WEEK:
                continue

            index.setdefault(week, {}).setdefault(day, {})[filename] = {
                "size":          obj["Size"],
                "last_modified": obj["LastModified"],
            }

    return index


def fetch_meta(s3_client, bucket: str, week: int, day: str) -> dict | None:
    """Download and parse meta.json for a given slot. Returns None on failure."""
    key = f"backups/week-{week}/{day}/meta.json"
    try:
        resp = s3_client.get_object(Bucket=bucket, Key=key)
        return json.loads(resp["Body"].read())
    except ClientError:
        return None


def verify_gzip(s3_client, bucket: str, week: int, day: str, filename: str) -> tuple[bool, str]:
    """
    Download filename and verify it is a valid gzip/tar archive.
    Returns (ok: bool, message: str).
    """
    key = f"backups/week-{week}/{day}/{filename}"
    try:
        resp   = s3_client.get_object(Bucket=bucket, Key=key)
        data   = resp["Body"].read()
        buf    = io.BytesIO(data)

        if filename.endswith(".tar.gz"):
            with tarfile.open(fileobj=buf, mode="r:gz") as tf:
                members = tf.getnames()
            return True, f"{len(members)} entries in tar"
        elif filename.endswith(".gz"):
            with gzip.open(buf) as gz:
                gz.read(1024)   # read a chunk to validate
            return True, "gzip OK"
        else:
            return True, "no integrity check"

    except (gzip.BadGzipFile, tarfile.TarError, EOFError) as exc:
        return False, f"CORRUPT: {exc}"
    except ClientError as exc:
        return False, f"S3 error: {exc}"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.0f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} GB"


def age_str(dt: datetime) -> str:
    """Return a human-readable age like '2 d 3 h ago'."""
    now   = datetime.now(timezone.utc)
    delta = now - dt
    total = int(delta.total_seconds())
    if total < 3600:
        return f"{total // 60} min ago"
    if total < 86400:
        h = total // 3600
        m = (total % 3600) // 60
        return f"{h} h {m} min ago"
    d = total // 86400
    h = (total % 86400) // 3600
    return f"{d} d {h} h ago"


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    # --- Build S3 client
    session_kwargs: dict = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region

    session  = boto3.Session(**session_kwargs)
    s3       = session.client("s3")

    print(f"\n{BOLD}StudyAmigo Backup Verifier{RESET}")
    print(f"Bucket : {CYAN}{args.bucket}{RESET}")
    if args.verify_integrity:
        print(f"Mode   : {YELLOW}integrity check enabled (downloads archives){RESET}")
    print()

    # --- Fetch index
    try:
        index = list_bucket_index(s3, args.bucket)
    except NoCredentialsError:
        print(f"{RED}ERROR: No AWS credentials found. "
              f"Use --profile or set AWS_PROFILE / AWS_DEFAULT_PROFILE.{RESET}")
        return 1
    except ClientError as exc:
        print(f"{RED}ERROR: {exc}{RESET}")
        return 1

    current_week, current_day = current_week_slot()

    # --- Print header
    col_w = 14
    print(f"{'Slot':<32} {'Status':<12} {'admin.db.gz':>{col_w}} "
          f"{'user_dbs.tar.gz':>{col_w}} {'Age':<18} {'Timestamp'}")
    print("─" * 110)

    total      = 0
    ok_count   = 0
    fail_count = 0

    for week in WEEK_SLOTS:
        for day in DAYS_OF_WEEK:
            total += 1
            slot_files = index.get(week, {}).get(day, {})
            missing    = REQUIRED_FILES - set(slot_files.keys())
            label      = slot_label(week, day, current_week, current_day)

            if missing:
                # Slot entirely absent or partially uploaded
                if not slot_files:
                    status = f"{YELLOW}EMPTY{RESET}"
                else:
                    status = f"{RED}PARTIAL{RESET}"
                print(f"{label:<50} {status:<20} {'—':>{col_w}} {'—':>{col_w}} {'—':<18} —")
                fail_count += 1
                continue

            # All 3 files present — gather sizes and age
            adm_size = human_size(slot_files["admin.db.gz"]["size"])
            udb_size = human_size(slot_files["user_dbs.tar.gz"]["size"])
            mod_time = slot_files["meta.json"]["last_modified"]
            age      = age_str(mod_time)

            # Try to read timestamp from meta.json
            meta      = fetch_meta(s3, args.bucket, week, day)
            ts_str    = meta.get("timestamp", "?") if meta else "?"
            db_count  = meta.get("user_db_count", "?") if meta else "?"

            status    = f"{GREEN}OK{RESET}"
            integrity_notes = []

            if args.verify_integrity:
                for fname in ("admin.db.gz", "user_dbs.tar.gz"):
                    ok, msg = verify_gzip(s3, args.bucket, week, day, fname)
                    if ok:
                        integrity_notes.append(f"{fname}: {msg}")
                    else:
                        status = f"{RED}CORRUPT{RESET}"
                        integrity_notes.append(f"{RED}{fname}: {msg}{RESET}")
                        fail_count += 1

            if status.startswith(GREEN) or status.startswith("\033[32m"):
                ok_count += 1

            print(f"{label:<50} {status:<20} {adm_size:>{col_w}} "
                  f"{udb_size:>{col_w}} {age:<18} {ts_str}  ({db_count} user dbs)")

            if integrity_notes:
                for note in integrity_notes:
                    print(f"    {'':32} {note}")

        # Blank line between weeks for readability
        print()

    # --- Summary
    print("─" * 110)
    if fail_count == 0:
        print(f"{GREEN}{BOLD}All {ok_count}/{total} slots OK.{RESET}")
    else:
        print(f"{YELLOW}{BOLD}{ok_count}/{total} slots OK, "
              f"{RED}{fail_count} slots missing/corrupt.{RESET}")

    print(f"\nCurrent slot: {BOLD}week-{current_week}/{current_day}{RESET}")

    next_rotation = _next_rotation()
    print(f"Next rotation (Saturday midnight UTC): "
          f"{BOLD}{next_rotation.strftime('%Y-%m-%d %H:%M UTC')}{RESET}\n")

    return 0 if fail_count == 0 else 1


def _next_rotation() -> datetime:
    """Return the datetime of the next Saturday 00:00 UTC."""
    now = datetime.now(timezone.utc)
    days_ahead = (5 - now.weekday()) % 7   # weekday(): Saturday = 5
    if days_ahead == 0:
        days_ahead = 7
    return (now + timedelta(days=days_ahead)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify StudyAmigo S3 backups — prints a 28-slot status grid.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--bucket", required=True,
        help="S3 bucket name (e.g. study-amigo-backups-123456789012). "
             "Get it with: cd server/aws_terraform && terraform output backup_bucket",
    )
    parser.add_argument(
        "--profile", default=None,
        help="AWS CLI profile to use (default: AWS_PROFILE env var or instance profile)",
    )
    parser.add_argument(
        "--region", default="us-east-1",
        help="AWS region (default: us-east-1)",
    )
    parser.add_argument(
        "--verify-integrity", action="store_true",
        help="Download each archive and verify gzip/tar integrity (slower but thorough)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(run(parse_args()))
