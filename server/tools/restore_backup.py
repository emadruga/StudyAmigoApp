#!/usr/bin/env python3
"""
restore_backup.py — StudyAmigo S3 Backup Restore Tool

Two execution modes:

  LOCAL mode  (run directly on the EC2 instance — recommended):
      Uses the attached IAM instance profile. Stops the server container,
      replaces admin.db and user_dbs/, fixes permissions, and restarts.

      python3 /opt/study-amigo/server/tools/restore_backup.py \\
          --bucket study-amigo-backups-<ACCOUNT_ID> \\
          [--week N] [--day DAY | --latest] [--dry-run]

  REMOTE mode (run from your Mac — orchestrates restore over SSH):
      Downloads the backup locally, SCPs files to EC2, then runs the
      container stop/replace/start sequence over SSH.

      python3 server/tools/restore_backup.py \\
          --bucket study-amigo-backups-<ACCOUNT_ID> \\
          --remote --host 54.152.109.26 --ssh-key ~/.ssh/study-amigo-aws \\
          [--profile study-amigo] \\
          [--week N] [--day DAY | --latest] [--dry-run]

Options:
    --bucket  BUCKET   S3 bucket name (required)
    --week    N        Week slot to restore (1-4)
    --day     DAY      Day of week to restore (monday..sunday)
    --latest           Restore the most recently written slot
    --list             List all available backups and exit
    --dry-run          Show what would happen without making any changes
    --remote           Orchestrate over SSH (Mac → EC2)
    --host    IP       EC2 IP or hostname (remote mode)
    --ssh-key PATH     Path to SSH private key (remote mode)
    --profile PROFILE  AWS CLI profile (remote mode from Mac)
    --region  REGION   AWS region (default: us-east-1)
    --app-dir PATH     Application directory on EC2 (default: /opt/study-amigo)
    --compose FILE     Docker Compose file path (default: <app-dir>/docker-compose.yml)
"""

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAYS_OF_WEEK   = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEK_SLOTS     = [1, 2, 3, 4]
DEFAULT_APP    = "/opt/study-amigo"
DEFAULT_COMPOSE = "{app_dir}/docker-compose.yml"

# ANSI colours
def _tty():
    return sys.stdout.isatty()

RED    = "\033[31m" if _tty() else ""
GREEN  = "\033[32m" if _tty() else ""
YELLOW = "\033[33m" if _tty() else ""
BOLD   = "\033[1m"  if _tty() else ""
RESET  = "\033[0m"  if _tty() else ""


def step(msg: str) -> None:
    print(f"\n{BOLD}==> {msg}{RESET}")


def info(msg: str) -> None:
    print(f"    {msg}")


def warn(msg: str) -> None:
    print(f"    {YELLOW}WARNING: {msg}{RESET}")


def die(msg: str) -> None:
    print(f"\n{RED}ERROR: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

def make_s3(args: argparse.Namespace):
    kw: dict = {"region_name": args.region}
    if hasattr(args, "profile") and args.profile:
        kw["profile_name"] = args.profile
        return boto3.Session(**kw).client("s3")
    return boto3.Session(region_name=args.region).client("s3")


def list_available(s3, bucket: str) -> list[dict]:
    """Return list of slot dicts with meta, sorted newest-first."""
    slots = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix="backups/"):
        for obj in page.get("Contents", []):
            parts = obj["Key"].split("/")
            if len(parts) != 4 or parts[3] != "meta.json":
                continue
            _, week_part, day, _ = parts
            try:
                week = int(week_part.split("-")[1])
            except (IndexError, ValueError):
                continue
            if week not in WEEK_SLOTS or day not in DAYS_OF_WEEK:
                continue

            try:
                resp = s3.get_object(Bucket=bucket, Key=obj["Key"])
                meta = json.loads(resp["Body"].read())
            except (ClientError, json.JSONDecodeError):
                meta = {}

            slots.append({
                "week":          week,
                "day":           day,
                "timestamp":     meta.get("timestamp", "unknown"),
                "user_db_count": meta.get("user_db_count", "?"),
                "admin_size":    meta.get("admin_db_compressed_size", "?"),
                "udb_size":      meta.get("user_dbs_compressed_size", "?"),
                "last_modified": obj["LastModified"],
                "meta":          meta,
            })

    slots.sort(key=lambda x: x["last_modified"], reverse=True)
    return slots


def print_listing(slots: list[dict]) -> None:
    if not slots:
        print("No backups found.")
        return

    print(f"\n{'#':<3} {'Slot':<22} {'Timestamp (UTC)':<22} {'admin.db.gz':>12} "
          f"{'user_dbs.tar.gz':>15} {'User DBs':>9}")
    print("─" * 90)

    for i, s in enumerate(slots, 1):
        slot = f"week-{s['week']}/{s['day']}"
        print(f"{i:<3} {slot:<22} {s['timestamp']:<22} "
              f"{s['admin_size']:>12} {s['udb_size']:>15} {str(s['user_db_count']):>9}")


def resolve_slot(s3, bucket: str, args: argparse.Namespace) -> tuple[int, str]:
    """
    Determine which (week, day) slot to restore from the CLI flags.
    Returns (week, day).
    """
    slots = list_available(s3, bucket)
    if not slots:
        die("No backups found in the bucket.")

    if args.latest:
        s = slots[0]
        info(f"Latest backup: week-{s['week']}/{s['day']}  ({s['timestamp']})")
        return s["week"], s["day"]

    if args.week and args.day:
        w = int(args.week)
        d = args.day.lower()
        if w not in WEEK_SLOTS:
            die(f"--week must be 1-4, got {w}")
        if d not in DAYS_OF_WEEK:
            die(f"--day must be one of {DAYS_OF_WEEK}, got {d}")
        # Verify the slot actually exists
        match = [s for s in slots if s["week"] == w and s["day"] == d]
        if not match:
            die(f"Slot week-{w}/{d} not found in S3. Run --list to see available slots.")
        info(f"Selected backup: week-{w}/{d}  ({match[0]['timestamp']})")
        return w, d

    # Neither --latest nor both --week + --day — show listing and prompt
    print_listing(slots)
    print()
    try:
        choice = input("Enter slot number to restore (or Ctrl+C to abort): ").strip()
        idx = int(choice) - 1
        if idx < 0 or idx >= len(slots):
            die(f"Invalid choice: {choice}")
        s = slots[idx]
        info(f"Selected: week-{s['week']}/{s['day']}  ({s['timestamp']})")
        return s["week"], s["day"]
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)


def download_slot(s3, bucket: str, week: int, day: str, dest: Path) -> dict[str, Path]:
    """Download admin.db.gz and user_dbs.tar.gz to dest/. Return file paths."""
    paths: dict[str, Path] = {}
    for fname in ("admin.db.gz", "user_dbs.tar.gz"):
        key   = f"backups/week-{week}/{day}/{fname}"
        local = dest / fname
        info(f"Downloading s3://{bucket}/{key} ...")
        try:
            s3.download_file(bucket, key, str(local))
        except ClientError as exc:
            die(f"Failed to download {key}: {exc}")
        info(f"  → {local}  ({local.stat().st_size // 1024} KB)")
        paths[fname] = local
    return paths


# ---------------------------------------------------------------------------
# Local restore (runs on EC2)
# ---------------------------------------------------------------------------

def restore_local(s3, bucket: str, week: int, day: str, args: argparse.Namespace) -> None:
    app_dir     = Path(args.app_dir)
    server_dir  = app_dir / "server"
    compose_file = Path(args.compose.format(app_dir=app_dir))
    admin_db    = server_dir / "admin.db"
    user_dbs    = server_dir / "user_dbs"

    step("Pre-flight checks")
    if not server_dir.exists():
        die(f"Server directory not found: {server_dir}")
    if not compose_file.exists():
        die(f"Docker Compose file not found: {compose_file}")
    info("OK")

    if args.dry_run:
        print(f"\n{YELLOW}[DRY RUN] No changes will be made.{RESET}")

    with tempfile.TemporaryDirectory(prefix="studyamigo-restore-") as tmp:
        tmp_path = Path(tmp)

        step(f"Downloading backup: week-{week}/{day}")
        paths = download_slot(s3, bucket, week, day, tmp_path)

        if args.dry_run:
            info("[DRY RUN] Would stop server container, replace files, restart.")
            return

        step("Stopping server container")
        _run(["sudo", "docker", "compose",
              "-f", str(compose_file), "stop", "server"])

        step("Backing up current databases → /tmp/studyamigo-pre-restore/")
        pre_backup = Path("/tmp/studyamigo-pre-restore")
        pre_backup.mkdir(exist_ok=True)
        if admin_db.exists():
            shutil.copy2(admin_db, pre_backup / "admin.db")
            info(f"  Saved admin.db  ({admin_db.stat().st_size // 1024} KB)")
        if user_dbs.exists():
            pre_udb = pre_backup / "user_dbs"
            if pre_udb.exists():
                shutil.rmtree(pre_udb)
            shutil.copytree(user_dbs, pre_udb)
            count = len(list(user_dbs.glob("*.db")))
            info(f"  Saved user_dbs/ ({count} databases)")

        step("Restoring admin.db")
        admin_gz = paths["admin.db.gz"]
        with gzip.open(admin_gz, "rb") as gz_in:
            data = gz_in.read()
        admin_db.write_bytes(data)
        os.chmod(admin_db, 0o644)
        info(f"  admin.db restored ({len(data) // 1024} KB uncompressed)")

        step("Restoring user_dbs/")
        if user_dbs.exists():
            shutil.rmtree(user_dbs)
        user_dbs.mkdir(mode=0o755)
        with tarfile.open(paths["user_dbs.tar.gz"], "r:gz") as tf:
            # Security: only extract user_dbs/* members
            safe_members = [
                m for m in tf.getmembers()
                if m.name.startswith("user_dbs/") and ".." not in m.name
            ]
            tf.extractall(path=server_dir, members=safe_members)
        count = len(list(user_dbs.glob("*.db")))
        info(f"  {count} user databases restored")

        step("Fixing file ownership (ubuntu:ubuntu = 1000:1000)")
        _run(["sudo", "chown", "ubuntu:ubuntu", str(admin_db)])
        _run(["sudo", "chown", "-R", "ubuntu:ubuntu", str(user_dbs)])

        step("Restarting server container")
        _run(["sudo", "docker", "compose",
              "-f", str(compose_file), "start", "server"])

        step("Verifying container started")
        import time
        time.sleep(3)
        result = subprocess.run(
            ["sudo", "docker", "compose", "-f", str(compose_file), "ps", "server"],
            capture_output=True, text=True
        )
        if "Up" in result.stdout or "running" in result.stdout.lower():
            print(f"\n{GREEN}{BOLD}✓ Restore complete. Server container is running.{RESET}")
        else:
            warn("Container may not have started cleanly. Check logs:")
            warn(f"  sudo docker compose -f {compose_file} logs --tail=30 server")

        info(f"\nPre-restore snapshot saved to: {pre_backup}")
        info("Remove it when no longer needed: sudo rm -rf /tmp/studyamigo-pre-restore")


# ---------------------------------------------------------------------------
# Remote restore (orchestrates via SSH from Mac)
# ---------------------------------------------------------------------------

def restore_remote(s3, bucket: str, week: int, day: str, args: argparse.Namespace) -> None:
    host     = args.host
    ssh_key  = os.path.expanduser(args.ssh_key)
    user     = getattr(args, "ssh_user", "ubuntu")
    app_dir  = args.app_dir
    compose  = args.compose.format(app_dir=app_dir)

    ssh_base = ["ssh", "-i", ssh_key,
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                f"{user}@{host}"]

    step("Pre-flight: verifying SSH connectivity")
    _run([*ssh_base, "echo ok"], capture=True)
    info("SSH OK")

    if args.dry_run:
        print(f"\n{YELLOW}[DRY RUN] No changes will be made.{RESET}")

    with tempfile.TemporaryDirectory(prefix="studyamigo-restore-") as tmp:
        tmp_path = Path(tmp)

        step(f"Downloading backup: week-{week}/{day}")
        paths = download_slot(s3, bucket, week, day, tmp_path)

        if args.dry_run:
            info("[DRY RUN] Would SCP archives to EC2 and run restore.")
            return

        step("Stopping server container on EC2")
        _run([*ssh_base, f"sudo docker compose -f {compose} stop server"])

        step("Uploading admin.db.gz to EC2 /tmp/")
        scp_base = ["scp", "-i", ssh_key, "-o", "StrictHostKeyChecking=no"]
        _run([*scp_base, str(paths["admin.db.gz"]),
              f"{user}@{host}:/tmp/restore-admin.db.gz"])

        step("Uploading user_dbs.tar.gz to EC2 /tmp/")
        _run([*scp_base, str(paths["user_dbs.tar.gz"]),
              f"{user}@{host}:/tmp/restore-user_dbs.tar.gz"])

        step("Restoring files on EC2")
        restore_cmd = (
            f"set -euo pipefail; "
            # Backup current dbs
            f"sudo mkdir -p /tmp/studyamigo-pre-restore; "
            f"[ -f {app_dir}/server/admin.db ] && "
            f"  sudo cp {app_dir}/server/admin.db /tmp/studyamigo-pre-restore/admin.db || true; "
            f"[ -d {app_dir}/server/user_dbs ] && "
            f"  sudo cp -r {app_dir}/server/user_dbs /tmp/studyamigo-pre-restore/ || true; "
            # Restore admin.db
            f"gunzip -c /tmp/restore-admin.db.gz | sudo tee {app_dir}/server/admin.db > /dev/null; "
            # Restore user_dbs
            f"sudo rm -rf {app_dir}/server/user_dbs; "
            f"sudo mkdir -p {app_dir}/server/user_dbs; "
            f"sudo tar -xzf /tmp/restore-user_dbs.tar.gz -C {app_dir}/server user_dbs/; "
            # Fix ownership
            f"sudo chown ubuntu:ubuntu {app_dir}/server/admin.db; "
            f"sudo chown -R ubuntu:ubuntu {app_dir}/server/user_dbs; "
            # Cleanup
            f"rm -f /tmp/restore-admin.db.gz /tmp/restore-user_dbs.tar.gz"
        )
        _run([*ssh_base, restore_cmd])

        step("Restarting server container")
        _run([*ssh_base, f"sudo docker compose -f {compose} start server"])

        import time
        time.sleep(3)
        result = subprocess.run(
            [*ssh_base, f"sudo docker compose -f {compose} ps server"],
            capture_output=True, text=True
        )
        if "Up" in result.stdout or "running" in result.stdout.lower():
            print(f"\n{GREEN}{BOLD}✓ Remote restore complete. Server container is running.{RESET}")
        else:
            warn("Container may not have started cleanly. Check logs on EC2:")
            warn(f"  ssh -i {ssh_key} {user}@{host} 'sudo docker compose -f {compose} logs --tail=30 server'")


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    info(f"$ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
    )
    if result.returncode != 0:
        if capture:
            die(f"Command failed (exit {result.returncode}):\n{result.stderr}")
        sys.exit(result.returncode)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Restore a StudyAmigo database backup from S3.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--bucket",   required=True, help="S3 backup bucket name")
    p.add_argument("--week",     type=int,       help="Week slot to restore (1-4)")
    p.add_argument("--day",                      help="Day of week (monday..sunday)")
    p.add_argument("--latest",   action="store_true",
                   help="Restore the most recently written backup")
    p.add_argument("--list",     action="store_true",
                   help="List available backups and exit")
    p.add_argument("--dry-run",  action="store_true",
                   help="Show what would happen without making changes")

    # Remote mode
    remote = p.add_argument_group("Remote mode (Mac → EC2 over SSH)")
    remote.add_argument("--remote",   action="store_true", help="Enable remote mode")
    remote.add_argument("--host",     default="54.152.109.26", help="EC2 IP / hostname")
    remote.add_argument("--ssh-key",  default="~/.ssh/study-amigo-aws",
                        help="SSH private key path")
    remote.add_argument("--ssh-user", default="ubuntu", help="SSH username (default: ubuntu)")
    remote.add_argument("--profile",  default=None,
                        help="AWS CLI profile (needed in remote mode on Mac)")

    # Common
    p.add_argument("--region",   default="us-east-1", help="AWS region")
    p.add_argument("--app-dir",  default=DEFAULT_APP,
                   help=f"Application directory on EC2 (default: {DEFAULT_APP})")
    p.add_argument("--compose",  default=DEFAULT_COMPOSE,
                   help="Docker Compose file path (use {app_dir} as placeholder)")

    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        s3 = make_s3(args)
    except NoCredentialsError:
        die("No AWS credentials found. Use --profile or run on EC2 with instance profile.")

    # --- List mode
    if args.list:
        slots = list_available(s3, args.bucket)
        print_listing(slots)
        return 0

    # --- Resolve which slot to restore
    week, day = resolve_slot(s3, args.bucket, args)

    print(f"\n{BOLD}Restore plan:{RESET}")
    print(f"  Bucket  : {args.bucket}")
    print(f"  Slot    : week-{week}/{day}")
    print(f"  Mode    : {'REMOTE (SSH → EC2)' if args.remote else 'LOCAL (on EC2)'}")
    print(f"  App dir : {args.app_dir}")
    if args.dry_run:
        print(f"  {YELLOW}DRY RUN — no changes will be made{RESET}")

    # Confirmation (skip in dry-run)
    if not args.dry_run:
        try:
            confirm = input(
                f"\n{YELLOW}This will STOP the server container and OVERWRITE production "
                f"databases.{RESET}\nType 'yes' to proceed: "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 0
        if confirm.lower() != "yes":
            print("Aborted.")
            return 0

    if args.remote:
        if not args.host:
            die("--host is required in remote mode")
        restore_remote(s3, args.bucket, week, day, args)
    else:
        restore_local(s3, args.bucket, week, day, args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
