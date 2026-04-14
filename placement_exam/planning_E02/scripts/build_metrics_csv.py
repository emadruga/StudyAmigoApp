#!/usr/bin/env python3
"""
build_metrics_csv.py — Gera CSV comparativo das 4 métricas de avaliação E01 vs E02

Para cada aluno do roster gera uma linha com:
  - Identificação: student_id, name, course, tier, path
  - Por exercício (E01 e E02), as 4 componentes e suas sub-métricas:
      V  — Volume:      total_reviews, cards_created, V (0–100)
      C  — Consistency: review_days, cramming_ratio, C (0–100)
      Q  — Quality:     retention_pct, maturity_pct, Q (0–100)
      E  — Engagement:  time_sub, ease_sub, mean_factor, E (0–100)
  - Nota final de cada exercício (escala 0–10)

Uso:
  python placement_exam/planning_E02/scripts/build_metrics_csv.py \\
      --e01    placement_exam/planning_E01/E01_final_grades.csv \\
      --e02    placement_exam/planning_E02/output/E02_final_grades.csv \\
      --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \\
      --output placement_exam/planning_E02/output/E01_E02_metrics.csv
"""

import argparse
import csv
import difflib
import re
import sys
from pathlib import Path

FUZZY_THRESHOLD = 0.72


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _norm(name: str) -> str:
    name = name.lower().strip()
    for src, dst in [
        ("á","a"),("à","a"),("ã","a"),("â","a"),
        ("é","e"),("ê","e"),("í","i"),
        ("ó","o"),("ô","o"),("õ","o"),
        ("ú","u"),("ü","u"),("ç","c"),
    ]:
        name = name.replace(src, dst)
    return re.sub(r"[^a-z0-9 ]", "", name)


def load_grades(path: Path) -> tuple[dict, dict]:
    """Retorna (by_id, by_name) para um CSV de notas."""
    by_id: dict = {}
    by_name: dict = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sid = row.get("student_id", "").strip()
            name = row.get("name", "").strip()
            if sid and sid not in ("", "NO_ACCOUNT"):
                # Se já existe, manter a com maior nota (conta secundária com mais revisões)
                if sid not in by_id or float(row["grade"]) > float(by_id[sid]["grade"]):
                    by_id[sid] = row
            if name:
                key = _norm(name)
                if key not in by_name or float(row["grade"]) > float(by_name[key]["grade"]):
                    by_name[key] = row
    return by_id, by_name


def find_row(sid, name: str, by_id: dict, by_name: dict):
    """Busca por ID exato, depois por nome fuzzy."""
    k = str(sid).strip() if sid else ""
    if k and k in by_id:
        return by_id[k]
    key = _norm(name)
    best_score, best_row = 0.0, None
    for cand, row in by_name.items():
        s = difflib.SequenceMatcher(None, key, cand).ratio()
        if s > best_score:
            best_score, best_row = s, row
    return best_row if best_score >= FUZZY_THRESHOLD else None


def _f(row, col, default=""):
    """Extrai coluna de um dict de CSV; retorna default se ausente/vazio."""
    if row is None:
        return default
    v = row.get(col, "").strip()
    return v if v else default


def _grade_0_10(row) -> str:
    """Nota 0–100 → 0–10 com 1 decimal."""
    if row is None:
        return ""
    try:
        return str(round(float(row["grade"]) / 10, 1))
    except (KeyError, ValueError):
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# CSV output columns
# ─────────────────────────────────────────────────────────────────────────────
# Colunas de identificação
ID_COLS = ["student_id", "name", "course", "tier", "path"]

# Sub-métricas brutas + componente por exercício
# Fórmula: Grade = 0.25×V + 0.25×C + 0.30×Q + 0.20×E
METRIC_COLS = [
    # V — Volume
    "total_reviews",        # revisões no período (cram excluídas)
    "cards_created",        # cards criados (apenas E02+)
    "V",                    # componente V (0–100)
    # C — Consistency
    "review_days",          # dias distintos com revisão
    "cramming_ratio",       # proporção de revisões no último dia
    "C",                    # componente C (0–100)
    # Q — Quality
    "retention_pct",        # % revisões corretas (tipo 1/2)
    "maturity_pct",         # % cards com ivl ≥ 21 dias
    "Q",                    # componente Q (0–100)
    # E — Engagement
    "time_sub",             # % revisões com tempo > 2s (tempo engajado)
    "ease_sub",             # % revisões com ease ≥ 2 (não travadas no Again)
    "mean_factor",          # fator médio de ease (meta: ~2500)
    "E",                    # componente E (0–100)
    # Nota final
    "grade",                # nota 0–100
    "nota_0_10",            # nota 0–10 (calculada aqui)
    "flags",                # flags de comportamento (RET100, LOW_TIME, CRAM)
]


def prefixed(cols, prefix: str) -> list[str]:
    return [f"{prefix}_{c}" for c in cols]


HEADER = (
    ID_COLS
    + prefixed(METRIC_COLS, "E01")
    + prefixed(METRIC_COLS, "E02")
)


def build_row(student: dict, e01_row, e02_row) -> list:
    sid   = student["student_id"]
    name  = student["name"]
    course = student["course"]
    tier  = student["tier"]
    path  = student["path"]

    def metrics(row, prefix):
        if row is None:
            return [""] * len(METRIC_COLS)
        vals = []
        for col in METRIC_COLS:
            if col == "nota_0_10":
                vals.append(_grade_0_10(row))
            else:
                vals.append(_f(row, col))
        return vals

    return (
        [sid, name, course, tier, path]
        + metrics(e01_row, "E01")
        + metrics(e02_row, "E02")
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--e01",    required=True, metavar="CSV",
                        help="CSV de notas E01 (ex.: planning_E01/E01_final_grades.csv)")
    parser.add_argument("--e02",    required=True, metavar="CSV",
                        help="CSV de notas E02 (ex.: output/E02_final_grades.csv)")
    parser.add_argument("--roster", required=True, metavar="CSV",
                        help="CSV do roster v2 (ex.: exam_prep/exam_01/bases/curated_student_roster_v2.csv)")
    parser.add_argument("--output", required=True, metavar="CSV",
                        help="CSV de saída (ex.: output/E01_E02_metrics.csv)")
    args = parser.parse_args()

    e01_path     = Path(args.e01)
    e02_path     = Path(args.e02)
    roster_path  = Path(args.roster)
    output_path  = Path(args.output)

    for p in (e01_path, e02_path, roster_path):
        if not p.exists():
            sys.exit(f"Arquivo não encontrado: {p}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Carregando E01: {e01_path}")
    e01_by_id, e01_by_name = load_grades(e01_path)
    print(f"  {len(e01_by_id)} entradas com student_id")

    print(f"Carregando E02: {e02_path}")
    e02_by_id, e02_by_name = load_grades(e02_path)
    print(f"  {len(e02_by_id)} entradas com student_id")

    print(f"Carregando roster: {roster_path}")
    with open(roster_path, newline="", encoding="utf-8-sig") as f:
        roster = []
        for row in csv.DictReader(f):
            norm = {k.strip().lower(): v.strip() for k, v in row.items()}
            roster.append({
                "student_id": norm.get("id", ""),
                "name":       norm.get("nome", norm.get("name", "")),
                "course":     norm.get("curso", norm.get("course", "")),
                "tier":       norm.get("suggested tier", norm.get("tier", "")),
                "path":       norm.get("caminho", norm.get("path", "")),
            })
    print(f"  {len(roster)} alunos no roster")

    matched_e01 = matched_e02 = 0
    rows_out = []

    for student in roster:
        sid  = student["student_id"]
        name = student["name"]

        e01_row = find_row(sid, name, e01_by_id, e01_by_name)
        e02_row = find_row(sid, name, e02_by_id, e02_by_name)

        if e01_row:
            matched_e01 += 1
        if e02_row:
            matched_e02 += 1

        rows_out.append(build_row(student, e01_row, e02_row))

    # Escrever CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows_out)

    print(f"\nSalvo em: {output_path}")
    print(f"  Alunos: {len(rows_out)}")
    print(f"  Com dados E01: {matched_e01}  |  Com dados E02: {matched_e02}")
    print(f"  Colunas: {len(HEADER)}")


if __name__ == "__main__":
    main()
