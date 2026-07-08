#!/usr/bin/env python3
"""
create_semester_timeline.py — Gera linha do tempo semestral de um aluno

Lê um JSON de configuração com os exercícios do semestre (datas de início/fim),
localiza automaticamente os snapshots e account_maps, e gera um relatório .md
com métricas exercício a exercício para um aluno específico.

Uso:
    python create_semester_timeline.py \\
        --config semester_config_2026_1.json \\
        --student-id 3006

    python create_semester_timeline.py \\
        --config semester_config_2026_1.json \\
        --student-name "Arthur"

    # Gerar para todos os alunos do roster:
    python create_semester_timeline.py \\
        --config semester_config_2026_1.json \\
        --output-dir ./timelines/
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Import grading functions from grade_exercise_v2 ──────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_GRADER_DIR = _SCRIPT_DIR.parent / "planning_E02" / "scripts"
sys.path.insert(0, str(_GRADER_DIR))

import grade_exercise_v2 as grader  # noqa: E402

# Re-export constants for clarity
EASE_MIN = grader.EASE_MIN
EASE_MAX = grader.EASE_MAX
MATURE_IVL = grader.MATURE_IVL
VERBAL_TENSES_DECK_ID = grader.VERBAL_TENSES_DECK_ID
MS = grader.MS


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot discovery
# ─────────────────────────────────────────────────────────────────────────────

def list_snapshots(snapshot_base: Path) -> List[str]:
    """Return sorted list of YYYYMMDD snapshot directories."""
    candidates = []
    for name in os.listdir(snapshot_base):
        full = snapshot_base / name
        if full.is_dir() and re.match(r"^\d{8}$", name):
            candidates.append(name)
    return sorted(candidates)


def _slugify_name(name: str) -> str:
    """Convert a full name to a filename-safe slug.

    'Arthur Alves do Nascimento' -> 'arthur-alves-do-nascimento'
    """
    # Remove accents
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace spaces/non-alnum with hyphens, collapse multiples
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    return slug


def find_best_snapshot(snapshot_base: Path, target_date: str) -> Optional[str]:
    """
    Find the snapshot closest to (and >= ) the day after target_date.
    target_date is YYYY-MM-DD (the exercise end date).
    Falls back to the most recent snapshot if none is after target.
    """
    snapshots = list_snapshots(snapshot_base)
    if not snapshots:
        return None

    # We want a snapshot taken AFTER the exercise ended
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_yyyymmdd = (target_dt + timedelta(days=1)).strftime("%Y%m%d")

    # Find first snapshot >= target_yyyymmdd
    for s in snapshots:
        if s >= target_yyyymmdd:
            return s

    # No snapshot after target — use the most recent available
    return snapshots[-1]


def find_account_map(exercise_label: str, project_root: Path) -> Optional[Path]:
    """Look for account_map.csv in placement_exam/planning_<label>/bases/."""
    path = project_root / "placement_exam" / f"planning_{exercise_label}" / "bases" / "account_map.csv"
    return path if path.exists() else None


# ─────────────────────────────────────────────────────────────────────────────
# Additional per-student queries (beyond grade_user_db)
# ─────────────────────────────────────────────────────────────────────────────

def count_notes_created(db_path: Path, start_dt: datetime, end_dt: datetime) -> int:
    """Count notes created in [start, end] period."""
    start_ms = int(start_dt.timestamp() * MS)
    end_ms = int(end_dt.timestamp() * MS)
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM notes WHERE id BETWEEN ? AND ?",
            (start_ms, end_ms),
        )
        result = cur.fetchone()[0]
        conn.close()
        return result
    except Exception:
        return 0


def get_activity_detail(
    db_path: Path, start_dt: datetime, end_dt: datetime
) -> List[Dict]:
    """
    Return per-day, per-deck activity breakdown.
    Each entry: {day, deck_name, deck_id, revs, ok}
    """
    start_ms = int(start_dt.timestamp() * MS)
    end_ms = int(end_dt.timestamp() * MS)
    details = []
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        # Load deck names
        cur.execute("SELECT decks FROM col")
        row = cur.fetchone()
        decks = json.loads(row[0]) if row else {}

        cur.execute("""
            SELECT DATE(r.id/1000, 'unixepoch', 'localtime') AS dia,
                   c.did,
                   COUNT(r.id) AS total,
                   SUM(CASE WHEN r.ease >= 2 THEN 1 ELSE 0 END) AS ok
            FROM revlog r
            JOIN cards c ON c.id = r.cid
            WHERE r.type != 3 AND r.id BETWEEN ? AND ?
            GROUP BY 1, 2
            ORDER BY 1
        """, (start_ms, end_ms))

        for dia, did, total, ok in cur.fetchall():
            deck_name = decks.get(str(did), {}).get("name", f"DID {did}")
            details.append({
                "day": dia,
                "deck_name": deck_name,
                "deck_id": did,
                "revs": total,
                "ok": ok or 0,
            })
        conn.close()
    except Exception:
        pass
    return details


# ─────────────────────────────────────────────────────────────────────────────
# Student lookup
# ─────────────────────────────────────────────────────────────────────────────

def find_student_in_roster(
    roster: List[Dict],
    student_id: Optional[int] = None,
    student_name: Optional[str] = None,
) -> List[Dict]:
    """Filter roster by student_id or partial name match."""
    if student_id is not None:
        return [s for s in roster if str(s["student_id"]) == str(student_id)]

    if student_name is not None:
        needle = student_name.lower()
        return [s for s in roster if needle in s["name"].lower()]

    return roster  # all students


# ─────────────────────────────────────────────────────────────────────────────
# Grade calculation (using class-level normalization)
# ─────────────────────────────────────────────────────────────────────────────

def process_all_students_for_exercise(
    users: Dict[int, Dict],
    user_dbs_dir: Path,
    start_dt: datetime,
    end_dt: datetime,
    grade_card_creation: bool,
) -> Dict[int, Dict]:
    """
    Process ALL students in a snapshot to get raw metrics.
    Returns {user_id: raw_metrics}.
    """
    raw_by_uid = {}
    for uid in users:
        db_path = grader.find_user_db_by_id(user_dbs_dir, uid)
        if db_path is None:
            continue
        raw_by_uid[uid] = grader.grade_user_db(db_path, start_dt, end_dt, grade_card_creation)
    return raw_by_uid


def compute_class_vectors(
    raw_by_uid: Dict[int, Dict],
    grade_card_creation: bool,
) -> Tuple[List[float], List[float]]:
    """Extract class-level normalization vectors from all active students."""
    active_uids = {uid for uid, raw in raw_by_uid.items() if raw["total_reviews"] > 0}
    all_reviews = [raw_by_uid[uid]["total_reviews"] for uid in active_uids]
    all_cards = (
        [raw_by_uid[uid]["cards_created"] for uid in active_uids]
        if grade_card_creation else []
    )
    return all_reviews, all_cards


# ─────────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_pct(val: float) -> str:
    if val == 0.0:
        return "—"
    return f"{val:.0f}%"


def _fmt_date_br(dt_str: str) -> str:
    """Convert YYYY-MM-DD to DD/MM."""
    parts = dt_str.split("-")
    return f"{parts[2]}/{parts[1]}"


def render_markdown(
    student: Dict,
    exercises_config: List[Dict],
    exercise_results: List[Dict],
) -> str:
    """Generate the full Markdown timeline report for one student."""
    lines = []
    name = student["name"]
    course = student.get("course", "")
    tier = student.get("tier", "")
    sid = student.get("student_id", "")
    email = student.get("email", "")
    today = datetime.now().strftime("%d/%m/%Y")

    lines.append(f"# Linha do Tempo Semestral — {name} ({course}, {tier})")
    lines.append("")
    lines.append(f"**Student ID:** {sid} | **E-mail:** {email}")
    lines.append(f"**Data de geração:** {today}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Cronograma oficial
    lines.append("## Cronograma oficial")
    lines.append("")
    lines.append("| Exercício | Início | Fim | Duração |")
    lines.append("|---|---|---|---|")
    for ex in exercises_config:
        start = datetime.strptime(ex["start"], "%Y-%m-%d")
        end = datetime.strptime(ex["end"], "%Y-%m-%d")
        duration = (end - start).days + 1
        lines.append(
            f"| {ex['label']} "
            f"| {start.strftime('%d/%m/%Y')} "
            f"| {end.strftime('%d/%m/%Y')} "
            f"| {duration} dias |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resumo por exercício
    lines.append("## Resumo por exercício")
    lines.append("")
    lines.append("| Ex | Período | Revs | Cria | Dias | Ret% | Mat% | V | C | Q | E | **Nota** | L | Flags |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    for r in exercise_results:
        periodo = f"{_fmt_date_br(r['start'])}–{_fmt_date_br(r['end'])}"
        ret_str = _fmt_pct(r["retention_pct"]) if r["total_reviews"] > 0 else "—"
        mat_str = _fmt_pct(r["maturity_pct"]) if r["total_reviews"] > 0 else "—"
        flags_str = r.get("flags_str", "")
        lines.append(
            f"| {r['label']} "
            f"| {periodo} "
            f"| {r['total_reviews']} "
            f"| {r['cards_created']} "
            f"| {r['review_days']} "
            f"| {ret_str} "
            f"| {mat_str} "
            f"| {r['V']:.1f} "
            f"| {r['C']:.1f} "
            f"| {r['Q']:.1f} "
            f"| {r['E']:.1f} "
            f"| **{r['grade']:.1f}** "
            f"| {r['grade_letter']} "
            f"| {flags_str} |"
        )

    lines.append("")

    # Produção consolidada
    lines.append("## Produção consolidada")
    lines.append("")
    lines.append("| Ex | Dias totais | Dias c/ atividade | Cards criados | Cards revisados |")
    lines.append("|---|---|---|---|---|")

    for r in exercise_results:
        if r["label"] == "E01":
            continue  # E01 is review-only, skip from production table
        lines.append(
            f"| {r['label']} "
            f"| {r['period_days']} "
            f"| {r['review_days']} "
            f"| {r['cards_created']} "
            f"| {r['total_reviews']} |"
        )

    lines.append("")

    # Observações por exercício
    lines.append("## Observações")
    lines.append("")

    for r in exercise_results:
        obs_parts = []
        periodo = f"{_fmt_date_br(r['start'])}–{_fmt_date_br(r['end'])}"
        lines.append(f"### {r['label']} — {periodo} | Nota: {r['grade']:.1f} ({r['grade_letter']})")
        lines.append("")

        if r["total_reviews"] == 0:
            obs_parts.append("- Sem atividade no período.")
        else:
            obs_parts.append(f"- {r['total_reviews']} revisões em {r['review_days']} dia(s) de {r['period_days']} disponíveis.")
            if r["cards_created"] > 0:
                obs_parts.append(f"- {r['cards_created']} cartões criados.")

        # Activity details
        if r.get("activity_detail"):
            obs_parts.append("- Atividade por dia/deck:")
            for d in r["activity_detail"]:
                obs_parts.append(f"  - {d['day']}: {d['revs']} revs ({d['ok']} OK) — {d['deck_name']}")

        # Flags
        flags = r.get("flags_str", "")
        if "CRAM" in flags:
            ratio = r.get("cramming_ratio", 0)
            obs_parts.append(f"- **CRAM** detectado: {ratio:.0%} das revisões no último dia.")
        if "RET100" in flags:
            obs_parts.append(f"- **RET100**: {r['ret_total']} revisões type=1/2 com 100% retenção.")
        if "RET100_CAP" in flags:
            obs_parts.append(f"- **RET100_CAP** aplicado: nota capada em 40.0.")
        if "LOW_TIME" in flags:
            obs_parts.append(f"- **LOW_TIME**: tempo de revisão abaixo de 30%.")

        if r.get("review_only"):
            obs_parts.append("- Exercício somente de revisão (deck Verbal Tenses pré-carregado).")

        for part in obs_parts:
            lines.append(part)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Gerado automaticamente por `create_semester_timeline.py` em {today}.*")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Gera linha do tempo semestral de um aluno no StudyAmigo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--config", required=True, metavar="JSON",
        help="JSON com exercícios do semestre (label, start, end, review_only).",
    )
    parser.add_argument(
        "--student-id", type=int, default=None,
        help="Filtrar por student_id do roster.",
    )
    parser.add_argument(
        "--student-name", default=None,
        help="Filtrar por nome (busca parcial, case-insensitive).",
    )
    parser.add_argument(
        "--output", default=None, metavar="FILE",
        help="Caminho do .md de saída (default: timeline_<id>_<slug-nome>.md).",
    )
    parser.add_argument(
        "--output-dir", default=None, metavar="DIR",
        help="Diretório para gerar um .md por aluno (quando sem --student-id/--student-name).",
    )
    parser.add_argument(
        "--snapshot-base", default=os.path.expanduser("~/.cache/studyamigo"),
        help="Diretório base dos snapshots (default: ~/.cache/studyamigo).",
    )
    args = parser.parse_args()

    # ── Load config ──────────────────────────────────────────────────────────
    config_path = Path(args.config)
    if not config_path.exists():
        sys.exit(f"Config não encontrado: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    exercises_config = config["exercises"]
    roster_path = Path(config["roster"])

    # Resolve relative paths from project root (StudyAmigoApp/)
    project_root = _SCRIPT_DIR.parent.parent  # scripts/ → placement_exam/ → StudyAmigoApp/
    if not roster_path.is_absolute():
        roster_path = project_root / roster_path

    snapshot_base = Path(args.snapshot_base)

    # ── Load roster ──────────────────────────────────────────────────────────
    roster = grader.load_roster(roster_path)

    # ── Find target students ─────────────────────────────────────────────────
    targets = find_student_in_roster(roster, args.student_id, args.student_name)
    if not targets:
        sys.exit(
            f"Nenhum aluno encontrado"
            + (f" com student_id={args.student_id}" if args.student_id else "")
            + (f" com nome contendo '{args.student_name}'" if args.student_name else "")
        )

    if len(targets) > 1 and args.student_name:
        print(f"  Encontrados {len(targets)} aluno(s) com nome contendo '{args.student_name}':")
        for t in targets:
            print(f"    [{t['student_id']}] {t['name']} — {t['course']}")
        print()

    # ── Process each exercise ────────────────────────────────────────────────
    print(f"\n  Processando {len(exercises_config)} exercício(s) para {len(targets)} aluno(s)...\n")

    # Cache: for each exercise, store the class-level data
    exercise_class_data = {}  # label → {raw_by_uid, all_reviews, all_cards, users, roster_matched}

    for ex_cfg in exercises_config:
        label = ex_cfg["label"]
        start_str = ex_cfg["start"]
        end_str = ex_cfg["end"]
        review_only = ex_cfg.get("review_only", False)
        grade_card_creation = not review_only

        # Find snapshot
        snap = find_best_snapshot(snapshot_base, end_str)
        if snap is None:
            print(f"  AVISO: nenhum snapshot encontrado para {label} (end={end_str}) — pulando")
            continue

        snap_dir = snapshot_base / snap
        admin_db = snap_dir / "admin.db"
        user_dbs_dir = snap_dir / "user_dbs"

        if not admin_db.exists():
            print(f"  AVISO: admin.db não encontrado em {snap_dir} — pulando {label}")
            continue

        print(f"  {label}: snapshot={snap}, período={start_str} → {end_str}", end="")

        # Load users and match roster
        users = grader.load_users(admin_db)

        # Deep copy roster for this exercise (match is done in-place)
        import copy
        roster_copy = copy.deepcopy(roster)
        grader.match_roster_to_admin(roster_copy, users)

        # Apply account_map if found
        acct_map_path = find_account_map(label, project_root)
        if acct_map_path:
            account_map = grader.load_account_map(acct_map_path)
            grader.apply_account_map(roster_copy, users, account_map)
            print(f", account_map={len(account_map)} entries", end="")

        # Time window — use NAIVE datetimes (system local timezone).
        # datetime.timestamp() on naive datetimes uses the local timezone,
        # which correctly converts "2026-04-12 23:59:59 BRT" to the right
        # UTC timestamp. Using tzinfo=timezone.utc would miss evening reviews
        # (e.g., 21:42 BRT = 00:42 UTC next day → outside the UTC boundary).
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59
        )

        # Process ALL students for class-level normalization
        raw_by_uid = process_all_students_for_exercise(
            users, user_dbs_dir, start_dt, end_dt, grade_card_creation
        )

        all_reviews, all_cards = compute_class_vectors(raw_by_uid, grade_card_creation)
        active_count = sum(1 for raw in raw_by_uid.values() if raw["total_reviews"] > 0)
        print(f", {active_count} alunos ativos")

        exercise_class_data[label] = {
            "raw_by_uid": raw_by_uid,
            "all_reviews": all_reviews,
            "all_cards": all_cards,
            "users": users,
            "roster": roster_copy,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "grade_card_creation": grade_card_creation,
            "review_only": review_only,
            "snapshot": snap,
            "user_dbs_dir": user_dbs_dir,
        }

    # ── Generate timeline for each target student ────────────────────────────
    for student in targets:
        exercise_results = []

        for ex_cfg in exercises_config:
            label = ex_cfg["label"]
            if label not in exercise_class_data:
                continue

            edata = exercise_class_data[label]
            start_dt = edata["start_dt"]
            end_dt = edata["end_dt"]
            grade_card_creation = edata["grade_card_creation"]
            roster_copy = edata["roster"]

            # Find this student in the exercise's roster copy
            student_match = [
                s for s in roster_copy
                if str(s["student_id"]) == str(student["student_id"])
            ]
            if not student_match:
                continue
            sm = student_match[0]

            # Find the best user_id for this student
            matched_uids = sm.get("_matched_uids", [sm["user_id"]] if sm["user_id"] else [])
            if not matched_uids:
                # Student has no account — zero grade
                exercise_results.append(_zero_result(ex_cfg, edata))
                continue

            # Pick uid with most reviews
            best_uid = max(
                (uid for uid in matched_uids if uid in edata["raw_by_uid"]),
                key=lambda uid: edata["raw_by_uid"][uid]["total_reviews"],
                default=matched_uids[0],
            )

            raw = edata["raw_by_uid"].get(best_uid)
            if raw is None:
                exercise_results.append(_zero_result(ex_cfg, edata))
                continue

            # Compute scores using class-level vectors
            if raw["total_reviews"] > 0:
                scores = grader.compute_scores(
                    raw, grade_card_creation,
                    edata["all_reviews"], edata["all_cards"],
                )
                flags = grader.behaviour_flags(raw, scores)

                # RET100_CAP penalty
                if "RET100" in flags and scores["maturity_pct"] < 10.0:
                    scores["grade"] = min(scores["grade"], 40.0)
                    if "RET100_CAP" not in flags:
                        flags.append("RET100_CAP")
            else:
                scores = {
                    "V": 0.0, "C": 0.0, "Q": 0.0, "E": 0.0, "grade": 0.0,
                    "retention_pct": 0.0, "maturity_pct": 0.0,
                    "cramming_ratio": 0.0,
                }
                flags = []

            # Notes created (may need era-specific snapshot)
            db_path = grader.find_user_db_by_id(edata["user_dbs_dir"], best_uid)
            notes_created = 0
            activity_detail = []
            if db_path:
                notes_created = count_notes_created(db_path, start_dt, end_dt)
                activity_detail = get_activity_detail(db_path, start_dt, end_dt)

            # cards_created: from grader raw (excludes Verbal Tenses deck).
            # For review_only exercises, raw["cards_created"] is already 0.
            cards_created = raw["cards_created"]

            period_days = (end_dt.date() - start_dt.date()).days + 1

            exercise_results.append({
                "label": label,
                "start": ex_cfg["start"],
                "end": ex_cfg["end"],
                "period_days": period_days,
                "snapshot": edata["snapshot"],
                "review_only": edata["review_only"],
                "total_reviews": raw["total_reviews"],
                "cards_created": cards_created,
                "review_days": raw["review_days"],
                "retention_pct": scores.get("retention_pct", 0.0),
                "maturity_pct": scores.get("maturity_pct", 0.0),
                "cramming_ratio": scores.get("cramming_ratio", 0.0),
                "ret_total": raw["ret_total"],
                "V": scores["V"],
                "C": scores["C"],
                "Q": scores["Q"],
                "E": scores["E"],
                "grade": scores["grade"],
                "grade_letter": grader.grade_letter(scores["grade"]),
                "flags": flags,
                "flags_str": " ".join(flags),
                "activity_detail": activity_detail,
            })

        # Render markdown
        md_content = render_markdown(student, exercises_config, exercise_results)

        # Output
        if args.output:
            output_path = Path(args.output)
        elif args.output_dir:
            out_dir = Path(args.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            slug = _slugify_name(student["name"])
            output_path = out_dir / f"timeline_{student['student_id']}_{slug}.md"
        else:
            slug = _slugify_name(student["name"])
            output_path = Path(f"timeline_{student['student_id']}_{slug}.md")

        if len(targets) == 1 or args.output_dir:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"\n  Gerado: {output_path}")
        else:
            # Multiple students without output_dir: print to stdout
            print(md_content)
            print("\n" + "=" * 80 + "\n")

    print("\n  Concluído.\n")


def _zero_result(ex_cfg: Dict, edata: Dict) -> Dict:
    """Return a zero-grade result for a student with no activity."""
    period_days = (edata["end_dt"].date() - edata["start_dt"].date()).days + 1
    return {
        "label": ex_cfg["label"],
        "start": ex_cfg["start"],
        "end": ex_cfg["end"],
        "period_days": period_days,
        "snapshot": edata["snapshot"],
        "review_only": edata.get("review_only", False),
        "total_reviews": 0,
        "cards_created": 0,
        "review_days": 0,
        "retention_pct": 0.0,
        "maturity_pct": 0.0,
        "cramming_ratio": 0.0,
        "ret_total": 0,
        "V": 0.0, "C": 0.0, "Q": 0.0, "E": 0.0,
        "grade": 0.0,
        "grade_letter": "F",
        "flags": [],
        "flags_str": "",
        "activity_detail": [],
    }


if __name__ == "__main__":
    main()
