#!/usr/bin/env python3
"""
add_email_to_admin_db.py

Fase 1 of SAv1.5 migration:
  1. Adds an `email` column (UNIQUE, nullable) to the `users` table in admin.db
  2. Populates email for each mapped student from email_mapping_v1.5.csv

Operates ONLY on a local backup DB. Never touches production.

Usage:
    python server_v2/scripts/add_email_to_admin_db.py [--db PATH] [--csv PATH] [--dry-run]

Defaults:
    --db   ~/.cache/studyamigo/20260415/admin.db
    --csv  server_v2/bases/email_mapping_v1.5.csv
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path.home() / ".cache/studyamigo/20260415/admin.db"
DEFAULT_CSV = Path(__file__).parent.parent / "bases" / "email_mapping_v1.5.csv"


def add_email_column(conn: sqlite3.Connection, dry_run: bool) -> bool:
    """Add email column if it doesn't already exist. Returns True if added."""
    cur = conn.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if "email" in columns:
        print("[INFO] Column 'email' already exists — skipping ALTER TABLE.")
        return False
    if dry_run:
        print("[DRY-RUN] Would run: ALTER TABLE users ADD COLUMN email TEXT")
        print("[DRY-RUN] Would run: CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL")
        return True
    conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
    conn.execute(
        "CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL"
    )
    conn.commit()
    print("[OK] Added column 'email' + unique index to users table.")
    return True


def populate_emails(conn: sqlite3.Connection, csv_path: Path, dry_run: bool):
    """Update each row with the email and canonical name from the CSV mapping."""
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r["email"].strip()]  # skip blank trailing lines

    print(f"[INFO] {len(rows)} mappings found in CSV.")

    updated = 0
    skipped = 0
    errors = []

    for row in rows:
        email = row["email"].strip()
        user_id = int(row["prod_user_id"].strip())
        nome = row["nome"].strip()

        # Verify user_id exists in DB
        cur = conn.execute("SELECT user_id, name FROM users WHERE user_id = ?", (user_id,))
        db_row = cur.fetchone()
        if db_row is None:
            errors.append(f"  user_id={user_id} ({nome}) NOT FOUND in DB")
            continue

        # Check if already up-to-date (skip in dry-run: email column may not exist yet)
        if not dry_run:
            cur = conn.execute("SELECT email, name FROM users WHERE user_id = ?", (user_id,))
            existing_email, existing_name = cur.fetchone()
            if existing_email == email and existing_name == nome:
                skipped += 1
                continue

        if dry_run:
            db_name = db_row[1]
            name_marker = "" if db_name == nome else f"  [name: '{db_name}' → '{nome}']"
            print(f"[DRY-RUN] UPDATE users SET email='{email}', name='{nome}' WHERE user_id={user_id}{name_marker}")
        else:
            try:
                conn.execute(
                    "UPDATE users SET email = ?, name = ? WHERE user_id = ?",
                    (email, nome, user_id),
                )
                updated += 1
            except sqlite3.IntegrityError as e:
                errors.append(f"  user_id={user_id} ({nome}) email='{email}' — INTEGRITY ERROR: {e}")

    if not dry_run:
        conn.commit()

    print(f"[RESULT] updated={updated}  skipped(already set)={skipped}  errors={len(errors)}")
    if errors:
        print("[ERRORS]")
        for e in errors:
            print(e)
        sys.exit(1)


def verify(conn: sqlite3.Connection, csv_path: Path):
    """Print a verification report."""
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r["email"].strip()]

    print("\n[VERIFY] Checking all emails and names in DB...")
    mismatches = []
    for row in rows:
        email = row["email"].strip()
        nome = row["nome"].strip()
        user_id = int(row["prod_user_id"].strip())
        cur = conn.execute("SELECT email, name FROM users WHERE user_id = ?", (user_id,))
        db_row = cur.fetchone()
        db_email = db_row[0] if db_row else None
        db_name = db_row[1] if db_row else None
        if db_email != email:
            mismatches.append(f"  user_id={user_id}: email expected='{email}' got='{db_email}'")
        if db_name != nome:
            mismatches.append(f"  user_id={user_id}: name expected='{nome}' got='{db_name}'")

    if mismatches:
        print(f"[FAIL] {len(mismatches)} mismatches:")
        for m in mismatches:
            print(m)
        sys.exit(1)
    else:
        print(f"[OK] All {len(rows)} emails and names verified correctly.")

    # Also report unmapped users (email still NULL)
    cur = conn.execute("SELECT user_id, username, name FROM users WHERE email IS NULL ORDER BY user_id")
    null_rows = cur.fetchall()
    if null_rows:
        print(f"\n[INFO] {len(null_rows)} users without email (expected for non-student accounts):")
        for r in null_rows:
            print(f"  user_id={r[0]}  username={r[1]}  name={r[2]}")


def main():
    parser = argparse.ArgumentParser(description="Add and populate email column in backup admin.db")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to admin.db backup")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to email_mapping_v1.5.csv")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"[ERROR] DB not found: {args.db}")
        sys.exit(1)
    if not args.csv.exists():
        print(f"[ERROR] CSV not found: {args.csv}")
        sys.exit(1)

    print(f"[INFO] DB : {args.db}")
    print(f"[INFO] CSV: {args.csv}")
    print(f"[INFO] dry-run: {args.dry_run}\n")

    conn = sqlite3.connect(args.db)
    try:
        add_email_column(conn, args.dry_run)
        populate_emails(conn, args.csv, args.dry_run)
        if not args.dry_run:
            verify(conn, args.csv)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
