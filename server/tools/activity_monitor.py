#!/usr/bin/env python3
"""
Activity Monitor — StudyAmigo

Connects to the running Docker containers on the remote EC2 instance via SSH,
copies the admin.db and all user_dbs/*.db files locally to a temp directory,
then analyses card reviews and card creations per day across all users for a
chosen time window.

Also prints a Top-10 "Most Consistent & Engaged Students" ranking.

Usage (run from your local machine):
    python activity_monitor.py --interval 24h
    python activity_monitor.py --interval week
    python activity_monitor.py --interval 2weeks
    python activity_monitor.py --interval 3weeks
    python activity_monitor.py --interval month
    python activity_monitor.py --interval custom --start 2025-12-01 --end 2026-01-15

    # Point at a different host / key:
    python activity_monitor.py --interval week \\
        --host 3.88.12.34 \\
        --key ~/.ssh/study-amigo-aws \\
        --remote-path /opt/study-amigo/server

    # Skip SSH fetch and analyse databases already present locally:
    python activity_monitor.py --interval week --local-only \\
        --admin-db /tmp/activity_monitor_dbs/admin.db \\
        --user-db-dir /tmp/activity_monitor_dbs/user_dbs
"""

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SSH_USER = "ubuntu"
DEFAULT_SSH_KEY = os.path.expanduser("~/.ssh/study-amigo-aws")
DEFAULT_REMOTE_PATH = "/opt/study-amigo/server"
DEFAULT_CONTAINER = "flashcard_server"

# In-container paths (relative to /app, which is mounted from $REMOTE_PATH)
CONTAINER_ADMIN_DB = "/app/admin.db"
CONTAINER_USER_DBS = "/app/user_dbs"

# revlog.id is in milliseconds; cards.id is in milliseconds too
MS = 1_000

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
        if not start or not end:
            sys.exit("--interval custom requires --start YYYY-MM-DD and --end YYYY-MM-DD")
        start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(end, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc
        )
        return start_dt, end_dt

    sys.exit(f"Unknown interval '{interval}'. Choose: 24h, week, 2weeks, 3weeks, month, custom")


def interval_label(start_dt: datetime, end_dt: datetime) -> str:
    fmt = "%Y-%m-%d %H:%M UTC"
    return f"{start_dt.strftime(fmt)}  →  {end_dt.strftime(fmt)}"


# ─────────────────────────────────────────────────────────────────────────────
# SSH / Docker fetch
# ─────────────────────────────────────────────────────────────────────────────

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
            day = datetime.fromtimestamp(rev_id / MS, tz=timezone.utc).strftime("%Y-%m-%d")
            result["reviews_by_day"][day] += 1
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
            day = datetime.fromtimestamp(card_id / MS, tz=timezone.utc).strftime("%Y-%m-%d")
            result["creations_by_day"][day] += 1
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


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Analyse flashcard activity across all users. "
            "Connects via SSH to fetch databases from the Docker container."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Time window
    parser.add_argument(
        "--interval",
        choices=["24h", "week", "2weeks", "3weeks", "month", "custom"],
        default="week",
        help="Analysis window (default: week)",
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="Custom start date (inclusive)")
    parser.add_argument("--end",   metavar="YYYY-MM-DD", help="Custom end date (inclusive)")

    # SSH connection
    parser.add_argument("--host",  default=None,
                        help="EC2 Elastic IP or hostname (required unless --local-only)")
    parser.add_argument("--key",   default=DEFAULT_SSH_KEY,
                        help=f"SSH private key path (default: {DEFAULT_SSH_KEY})")
    parser.add_argument("--user",  default=DEFAULT_SSH_USER,
                        help=f"SSH user (default: {DEFAULT_SSH_USER})")
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH,
                        help=f"Path to server directory on EC2 (default: {DEFAULT_REMOTE_PATH})")
    parser.add_argument("--container", default=DEFAULT_CONTAINER,
                        help=f"Docker container name (default: {DEFAULT_CONTAINER})")

    # Local-only mode
    parser.add_argument("--local-only", action="store_true",
                        help="Skip SSH fetch; analyse databases already present locally")
    parser.add_argument("--admin-db",   default=None,
                        help="Local path to admin.db (used with --local-only)")
    parser.add_argument("--user-db-dir", default=None,
                        help="Local path to user_dbs/ dir (used with --local-only)")

    # Cache
    parser.add_argument("--cache-dir", default=None, metavar="DIR",
                        help=(
                            "Persist fetched databases in DIR instead of a temp folder. "
                            "On subsequent runs the download is skipped if databases "
                            "already exist there. Use --refresh to force a new download."
                        ))
    parser.add_argument("--refresh", action="store_true",
                        help="Force re-download even when --cache-dir already has data")

    # Output options
    parser.add_argument("--top", type=int, default=10,
                        help="How many users to show in the ranking (default: 10)")
    parser.add_argument("--no-breakdown", action="store_true",
                        help="Skip the per-user detailed breakdown section")

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

    # ── Fetch or locate databases ─────────────────────────────────────────
    tmp_dir = None          # set only when we own a temp dir to clean up later
    if args.local_only:
        if not args.admin_db or not args.user_db_dir:
            sys.exit(
                "--local-only requires --admin-db <path> and --user-db-dir <path>"
            )
        admin_db = Path(args.admin_db)
        user_dbs_dir = Path(args.user_db_dir)
    else:
        if not args.host:
            sys.exit(
                "Provide --host <EC2-IP> to fetch databases via SSH, "
                "or use --local-only with --admin-db and --user-db-dir."
            )

        # Decide where to store the databases
        if args.cache_dir:
            fetch_dir = Path(args.cache_dir)
            fetch_dir.mkdir(parents=True, exist_ok=True)
        else:
            tmp_dir = Path(tempfile.mkdtemp(prefix="activity_monitor_"))
            fetch_dir = tmp_dir

        # Check if cached data is already present (and --refresh not requested)
        cached_admin = fetch_dir / "admin.db"
        cached_user_dbs = fetch_dir / "user_dbs"
        already_cached = (
            cached_admin.exists()
            and cached_user_dbs.is_dir()
            and any(cached_user_dbs.glob("*.db"))
        )

        if already_cached and not args.refresh:
            db_count = len(list(cached_user_dbs.glob("*.db")))
            print(f"  Usando cache em {fetch_dir}  ({db_count} BDs de usuários)")
            print(f"  (use --refresh para forçar novo download)")
        else:
            if already_cached and args.refresh:
                print(f"  --refresh solicitado; baixando novamente em {fetch_dir}")
            else:
                print(f"  Diretório de destino: {fetch_dir}")
            print()
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

        admin_db = cached_admin
        user_dbs_dir = cached_user_dbs

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

    # ── Cleanup ────────────────────────────────────────────────────────────
    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"  (arquivos temporários removidos)")
    elif args.cache_dir:
        print(f"  (bancos de dados mantidos em cache: {args.cache_dir})")


if __name__ == "__main__":
    main()
