#!/usr/bin/env python3
"""
consolidate_grades.py
Resolves duplicate accounts and assigns final 0-10 grades for E01.

Decisions applied (confirmed by instructor):
1. Madson (5066)        → use account 46 (329 reviews, grade=78.7)
2. Ana Luiza (4011)     → user_id 62 (Luiza., grade=78.7) is her real account
3. Cauã Jorge (4016)    → user_id 54 (Cauã Nzth, grade=50.3) is his real account
4. Ana Julia (4006)     → user_id 57 (anajulisot, grade=56.7); Daniel to be verified later
5. Philipe Emanuel (79) → real student, keep grade=83.9 (no student_id, flag for manual entry)

Usage:
    python placement_exam/planning_E01/scripts/consolidate_grades.py
"""

import csv
import math
import sys
from pathlib import Path

INPUT_CSV  = Path("placement_exam/planning_E01/E01_grades_20260330.csv")
OUTPUT_CSV = Path("placement_exam/planning_E01/E01_final_grades.csv")

# ---------------------------------------------------------------------------
# Duplicate-account resolution map
# key   = user_id to KEEP (authoritative account)
# value = dict with overrides to apply (e.g. student_id if missing)
# ---------------------------------------------------------------------------
KEEP = {
    # Madson: official account 46 already has student_id 5066 — just drop 84
    46: {},
    # Ana Luiza 4011: account 62 has the real activity
    62: {"student_id": "4011", "name": "Ana Luiza Camilo da Silva",
         "course": "Metrologia", "tier": "Tier 1", "path": "B",
         "email": "analuiza101115@gmail.com"},
    # Cauã Jorge 4016: account 54 has the real activity
    54: {"student_id": "4016", "name": "Cauã Jorge de Nazareth Marins",
         "course": "Metrologia", "tier": "Tier 1", "path": "B",
         "email": "cjomaislindao@gmail.com"},
    # Ana Julia 4006: account 57 has the real activity
    57: {"student_id": "4006", "name": "Ana Julia de souza oliveira",
         "course": "Metrologia", "tier": "Tier 1", "path": "A",
         "email": "anajuliaoliveiratorres99@gmail.com"},
    # Philipe Emanuel: real student, no student_id yet — keep as-is, flag it
    79: {},
}

# user_ids to DROP entirely (superseded duplicates)
DROP = {
    84,   # madsonfs  — superseded by 46 (Madson)
    50,   # Luiza     — superseded by 62 (Ana Luiza)
    89,   # Daniel    — student_id 4006 reassigned to Ana Julia; Daniel TBD
    59,   # Henrique  — duplicate of João Ricardo 47
    # Rogério duplicates (only 73 kept — it's the roster match for 5091)
    66, 70, 87,
    # Matheus duplicates (keep 71)
    44, 69,
    # Bruno duplicates (keep 104 which has student_id 5021)
    40, 91,
    # Arthur Alves duplicate (keep 32 which has student_id 3006)
    49,
    # Emanuel duplicate (keep 99)
    98,
    # Anthony Lucas duplicate (keep 92)
    88,
    # Daniel duplicate (keep 103 — more activity; 89 was student_id holder but reassigned)
    # 103 kept, 89 dropped above
}

# user_ids that were NO_ACCOUNT placeholders now resolved above — remove them
# (4011 resolved to 62, 4016 resolved to 54, 4006 resolved to 57)
DROP_STUDENT_IDS_PLACEHOLDER = {"4011", "4016", "4006"}


def grade_to_10(grade_str):
    """Convert 0-100 grade string to 0-10 rounded to 1 decimal."""
    try:
        v = float(grade_str)
        if math.isnan(v):
            return "0.0"
        return f"{v / 10:.1f}"
    except (ValueError, TypeError):
        return "0.0"


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    output_rows = []
    for row in rows:
        uid_str = row.get("user_id", "").strip()
        sid_str = row.get("student_id", "").strip()

        # Drop superseded duplicate accounts
        try:
            uid = int(uid_str) if uid_str else None
        except ValueError:
            uid = None

        if uid in DROP:
            continue

        # Drop NO_ACCOUNT placeholders that have been resolved to real accounts
        if not uid_str and sid_str in DROP_STUDENT_IDS_PLACEHOLDER:
            continue

        # Apply overrides for kept accounts
        if uid in KEEP and KEEP[uid]:
            overrides = KEEP[uid]
            for field, value in overrides.items():
                csv_field = {
                    "student_id": "student_id",
                    "name":       "name",
                    "course":     "course",
                    "tier":       "tier",
                    "path":       "path",
                    "email":      "email",
                }.get(field)
                if csv_field:
                    row[csv_field] = value

        # Add nota_final column (0-10)
        row["nota_final"] = grade_to_10(row.get("grade", "0"))

        output_rows.append(row)

    # Sort: students with activity first (by grade desc), then zeros
    def sort_key(r):
        try:
            return -float(r.get("grade") or 0)
        except ValueError:
            return 0

    output_rows.sort(key=sort_key)

    out_fields = (fieldnames or []) + ["nota_final"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Written: {OUTPUT_CSV}  ({len(output_rows)} students)")

    # Summary report
    print("\n=== ATENÇÃO — revisão manual necessária ===")
    print("• Daniel André de Oliveira (4006 era dele, agora atribuído a Ana Julia)")
    print("  → user_id 103 (Daniel A., grade=62.9) aguarda student_id correto")
    print("• Philipe Emanuel de Souza Meireles (user_id 79, grade=83.9)")
    print("  → aluno real confirmado, mas sem student_id no roster")
    print("• Rogério (5091): grade=36.2 com apenas 6 reviews — revisar se é mesmo ele")


if __name__ == "__main__":
    main()
