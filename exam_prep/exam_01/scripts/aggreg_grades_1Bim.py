"""
aggreg_grades_1Bim.py
Agrega as notas de E01, E02 e Exame 01 para todos os alunos do 1º Bimestre.

Uso:
    python3 aggreg_grades_1Bim.py --roster <roster.csv> \
        --metrics <E01_E02_metrics.csv> --exame <prova_final_1bim_RESULTADOS.csv> \
        --out <RESULTADOS_1BIM.csv>

Entradas:
  --roster   curated_student_roster_v2.csv  — fonte canônica da lista de alunos
  --metrics  E01_E02_metrics.csv            — notas dos exercícios E01 e E02
  --exame    prova_final_1bim_RESULTADOS.csv — notas do Exame 01
  --out      RESULTADOS_1BIM.csv            — CSV de saída agregado

Regras:
  - Base de alunos: o roster (todos os 64 alunos).
  - E01_nota_0_10 e E02_nota_0_10: vindas de --metrics; vazio → 0.0.
  - Exame01_nota: vinda de --exame (coluna Nota_10); ausente ou AUSENTE → 0.0.
  - Alunos ausentes no Exame 01 têm Exame01_nota = 0.0 e Exame01_obs = AUSENTE.
"""

import argparse
import csv
import os
import unicodedata
import re

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(__file__)
_BASE       = os.path.join(_SCRIPT_DIR, "..")

parser = argparse.ArgumentParser(
    description="Agrega notas E01, E02 e Exame 01 em um único CSV do 1º Bimestre."
)
parser.add_argument(
    "--roster",
    default=os.path.join(_BASE, "bases", "curated_student_roster_v2.csv"),
    metavar="FILE",
    help="CSV do roster de alunos (padrão: ../bases/curated_student_roster_v2.csv)",
)
parser.add_argument(
    "--metrics",
    default=os.path.join(_BASE, "bases", "E01_E02_metrics.csv"),
    metavar="FILE",
    help="CSV com notas E01 e E02 (padrão: ../bases/E01_E02_metrics.csv)",
)
parser.add_argument(
    "--exame",
    default=os.path.join(_BASE, "output", "prova_final_1bim_RESULTADOS.csv"),
    metavar="FILE",
    help="CSV com notas do Exame 01 (padrão: ../output/prova_final_1bim_RESULTADOS.csv)",
)
parser.add_argument(
    "--out",
    default=os.path.join(_BASE, "output", "RESULTADOS_1BIM.csv"),
    metavar="FILE",
    help="Caminho do CSV de saída (padrão: ../output/RESULTADOS_1BIM.csv)",
)
args = parser.parse_args()

os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.lower().strip())


def _float_or_zero(val: str) -> float:
    try:
        return round(float(val), 2)
    except (TypeError, ValueError):
        return 0.0

# ---------------------------------------------------------------------------
# 1. Carregar roster (fonte de verdade da lista de alunos)
# ---------------------------------------------------------------------------
roster = {}      # student_id -> {nome, curso, tier, path}

with open(args.roster, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        sid = row["ID"].strip()
        curso_key = next(k for k in row if "Curso" in k)
        roster[sid] = {
            "nome":  row["Nome"].strip(),
            "curso": row[curso_key].strip(),
            "tier":  row.get("Suggested Tier", "").strip(),
            "path":  row.get("Caminho", "").strip(),
        }

# ---------------------------------------------------------------------------
# 2. Carregar métricas E01/E02  (indexado por student_id)
# ---------------------------------------------------------------------------
metrics = {}  # student_id -> row dict

with open(args.metrics, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        sid = row["student_id"].strip()
        metrics[sid] = row

# ---------------------------------------------------------------------------
# 3. Carregar notas do Exame 01  (indexado por ID)
# ---------------------------------------------------------------------------
exame = {}  # student_id -> {nota, obs, fonte, tier_exame}

with open(args.exame, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        sid = row["ID"].strip()
        exame[sid] = {
            "nota":       row.get("Nota_10", "").strip(),
            "obs":        row.get("Obs", "").strip(),
            "fonte":      row.get("Fonte_prova", "").strip(),
            "tier_exame": row.get("Tier", "").strip(),
        }

# ---------------------------------------------------------------------------
# 4. Montar linhas de saída
# ---------------------------------------------------------------------------
rows_out = []

for sid, info in sorted(roster.items(), key=lambda x: x[1]["nome"]):
    m  = metrics.get(sid, {})
    ex = exame.get(sid, {})

    # Tier: preferir o do exame (mais recente), depois roster, depois métricas
    tier = ex.get("tier_exame") or info["tier"] or m.get("tier", "")

    # Notas E01 / E02
    e01 = _float_or_zero(m.get("E01_nota_0_10", ""))
    e02 = _float_or_zero(m.get("E02_nota_0_10", ""))

    # Nota Exame 01
    fonte_exame = ex.get("fonte", "AUSENTE")
    if fonte_exame == "AUSENTE" or not ex or not ex.get("nota"):
        exame_nota = 0.0
        exame_obs  = ex.get("obs", "AUSENTE") or "AUSENTE"
    else:
        exame_nota = _float_or_zero(ex["nota"])
        exame_obs  = ex.get("obs", "")

    rows_out.append({
        "ID":            sid,
        "Nome":          info["nome"],
        "Curso":         info["curso"],
        "Tier":          tier,
        "E01_nota":      e01,
        "E01_flags":     m.get("E01_flags", ""),
        "E02_nota":      e02,
        "E02_flags":     m.get("E02_flags", ""),
        "Exame01_nota":  exame_nota,
        "Exame01_fonte": fonte_exame,
        "Exame01_obs":   exame_obs,
    })

# ---------------------------------------------------------------------------
# 5. Escrever CSV
# ---------------------------------------------------------------------------
fieldnames = [
    "ID", "Nome", "Curso", "Tier",
    "E01_nota", "E01_flags",
    "E02_nota", "E02_flags",
    "Exame01_nota", "Exame01_fonte", "Exame01_obs",
]

with open(args.out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

# ---------------------------------------------------------------------------
# 6. Relatório no terminal
# ---------------------------------------------------------------------------
total   = len(rows_out)
ausente = [r for r in rows_out if r["Exame01_fonte"] == "AUSENTE"]
zeros   = [r for r in rows_out if r["Exame01_nota"] == 0.0 and r["Exame01_fonte"] != "AUSENTE"]

print(f"CSV gerado: {args.out}")
print(f"Total alunos: {total}")
print(f"Ausentes no Exame 01 (nota = 0.0): {len(ausente)}")
for r in ausente:
    print(f"  - {r['ID']} {r['Nome']}")
if zeros:
    print(f"Fizeram o exame mas tiraram 0.0: {len(zeros)}")
    for r in zeros:
        print(f"  - {r['ID']} {r['Nome']} ({r['Exame01_fonte']})")
