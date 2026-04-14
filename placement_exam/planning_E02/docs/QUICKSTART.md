# QUICKSTART — Scripts de avaliação E02

Este documento cobre os três scripts do pipeline de avaliação do E02:

| Script | Entrada | Saída |
|--------|---------|-------|
| `grade_exercise_v2.py` | DBs SQLite (local / S3 / SSH) + roster + account_map | `E02_final_grades.csv` |
| `build_roster_xlsx.py` | xlsx E01 + `E02_final_grades.csv` + roster v2 | `curated_student_roster_E02.xlsx` |
| `build_metrics_csv.py` | `E01_final_grades.csv` + `E02_final_grades.csv` + roster v2 | `E01_E02_metrics.csv` |

---

## Requisitos

```bash
# Criar venv (apenas uma vez)
python3 -m venv placement_exam/.venv
placement_exam/.venv/bin/pip install numpy openpyxl
```

Python 3.8+ requerido. `boto3` só é necessário para o modo S3 de `grade_exercise_v2.py`.

---

## Estrutura de arquivos (E02)

```
placement_exam/planning_E02/
├── bases/
│   ├── account_map.csv               # mapeamento usernames → roster
│   └── curated_student_roster.xlsx   # planilha de entrada com notas E01
├── output/
│   ├── E02_final_grades.csv          # notas E02 (gerado por grade_exercise_v2)
│   ├── curated_student_roster_E02.xlsx  # planilha consolidada E01+E02
│   └── E01_E02_metrics.csv           # métricas detalhadas V/C/Q/E por exercício
├── scripts/
│   ├── grade_exercise_v2.py
│   ├── build_roster_xlsx.py
│   └── build_metrics_csv.py
└── docs/
    └── QUICKSTART.md                 # este arquivo

exam_prep/exam_01/bases/
└── curated_student_roster_v2.csv     # roster permanente (fonte de verdade)
```

---

## 1. grade_exercise_v2.py — Calcular notas E02

Calcula as notas individuais dos alunos usando a fórmula:

```
Nota = 0.25 × V  +  0.25 × C  +  0.30 × Q  +  0.20 × E
```

> **Diferença E01 → E02**: E02 inclui criação de cards no componente Volume —
> **não** usar `--no-card-creation`.

### Fontes de dados

#### Bancos locais (recomendado)

```bash
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260414/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260414/user_dbs \
    --output placement_exam/planning_E02/output/E02_final_grades.csv
```

#### Backup S3

```bash
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --bucket study-amigo-backups-645069181643 --profile study-amigo \
    --output placement_exam/planning_E02/output/E02_final_grades.csv
```

#### SSH — servidor de produção ao vivo

```bash
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --host 54.152.109.26 \
    --output placement_exam/planning_E02/output/E02_final_grades.csv
```

Chave SSH padrão: `~/.ssh/study-amigo-aws`. Sobrescrever com `--key`.

### Flags principais

| Flag | Descrição |
|------|-----------|
| `--label LABEL` | Rótulo do exercício (ex.: `E02`). |
| `--interval` | Janela de tempo: `24h`, `week`, `2weeks`, `3weeks`, `month` ou `custom`. |
| `--start YYYY-MM-DD` | Data de início (obrigatório com `--interval custom`). |
| `--end YYYY-MM-DD` | Data de fim inclusive (padrão: hoje). |
| `--roster CSV` | Caminho para o roster v2 (aceita colunas em português). |
| `--account-map CSV` | CSV com colunas `username`, `roster_name` para mapear contas secundárias. |
| `--output FILE` | Caminho de saída do CSV. |
| `--no-card-creation` | Exclui criação de cards do Volume. **Não usar no E02.** |
| `--top N` | Número de alunos nas tabelas Top/Bottom (padrão: 10). |
| `--cache-dir DIR` | Diretório para armazenar bancos baixados. |
| `--refresh` | Força re-download mesmo que cópia em cache exista. |

### Formato do account_map.csv

```
username,roster_name
Mahx.vpc,Marcella Vasconcelos Pacheco da Cruz
Matt,Mateus Ferreira Patrício
theuxzvA7X,Matheus Dias Gomes
...
```

O mapeamento é aplicado após o matching fuzzy — injeta UIDs de contas
secundárias no aluno correto do roster. A conta com mais revisões é
usada para o cálculo da nota.

### Flags de comportamento na saída

| Flag | Condição |
|------|----------|
| `RET100` | 100% de retenção com ≥ 30 revisões tipo 1/2 |
| `LOW_TIME` | `time_sub` < 30% com ≥ 20 revisões (respostas abaixo de 2 s) |
| `CRAM` | > 80% das revisões no último dia da janela |

---

## 2. build_roster_xlsx.py — Planilha consolidada E01 + E02

Lê a planilha xlsx de entrada (com notas E01) e o CSV de notas E02, e gera
uma planilha de saída com as colunas originais + `E02` + `obs_E02`, ordenada
alfabeticamente por nome. Alunos presentes no roster v2 mas ausentes no xlsx
de entrada são inseridos automaticamente via `--roster-v2`.

### Uso

```bash
python3 placement_exam/planning_E02/scripts/build_roster_xlsx.py \
    --input     placement_exam/planning_E02/bases/curated_student_roster.xlsx \
    --grades    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster-v2 exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --output    placement_exam/planning_E02/output/curated_student_roster_E02.xlsx
```

`--roster-v2` é opcional. Sem ele, apenas os alunos já presentes no xlsx de
entrada recebem a nota E02.

### Flags

| Flag | Obrigatório | Descrição |
|------|:-----------:|-----------|
| `--input` | ✅ | XLSX de entrada com notas E01 |
| `--grades` | ✅ | CSV de notas E02 gerado por `grade_exercise_v2.py` |
| `--output` | ✅ | XLSX de saída |
| `--roster-v2` | — | CSV do roster v2 para inserir alunos novos |

### Colunas da saída

As colunas do xlsx de entrada são preservadas integralmente. São adicionadas:

| Coluna | Descrição |
|--------|-----------|
| `E02` | Nota 0–10 (1 casa decimal) |
| `obs_E02` | Flags de comportamento + username da conta secundária (se houver) |

Formatação automática: cabeçalho azul escuro, linhas coloridas por curso
(Biotecnologia / Metrologia / SegCiber), nota 0 em rosa, nota < 5 em amarelo,
flags em vermelho.

---

## 3. build_metrics_csv.py — Métricas detalhadas V/C/Q/E por exercício

Gera um CSV com as sub-métricas brutas das 4 componentes de avaliação para
cada aluno, cruzando E01 e E02 lado a lado. Útil para análise comparativa de
desempenho entre exercícios.

### Uso

```bash
python3 placement_exam/planning_E02/scripts/build_metrics_csv.py \
    --e01    placement_exam/planning_E01/E01_final_grades.csv \
    --e02    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --output placement_exam/planning_E02/output/E01_E02_metrics.csv
```

### Flags

| Flag | Obrigatório | Descrição |
|------|:-----------:|-----------|
| `--e01` | ✅ | CSV de notas E01 |
| `--e02` | ✅ | CSV de notas E02 |
| `--roster` | ✅ | CSV do roster v2 (define a lista de alunos e ordem) |
| `--output` | ✅ | CSV de saída |

### Colunas da saída

Identificação (5 colunas) + métricas E01 (16 colunas) + métricas E02 (16 colunas) = **37 colunas**.

| Grupo | Colunas (prefixo `E01_` e `E02_`) |
|-------|-----------------------------------|
| **V — Volume** | `total_reviews`, `cards_created`, `V` |
| **C — Consistency** | `review_days`, `cramming_ratio`, `C` |
| **Q — Quality** | `retention_pct`, `maturity_pct`, `Q` |
| **E — Engagement** | `time_sub`, `ease_sub`, `mean_factor`, `E` |
| Nota | `grade` (0–100), `nota_0_10` (0–10), `flags` |

> Nota: `E01_maturity_pct` é 0 para todos os alunos — reflexo do bug de
> intervalo linear ativo durante o E01 (documentado em
> `docs/CARD_PROGRESSION_ANALYSIS.md`). A partir do E02 o bug foi corrigido.

---

## Pipeline completo (execução sequencial)

```bash
# 1. Calcular notas E02
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260414/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260414/user_dbs \
    --output placement_exam/planning_E02/output/E02_final_grades.csv

# 2. Gerar planilha consolidada E01 + E02
python3 placement_exam/planning_E02/scripts/build_roster_xlsx.py \
    --input     placement_exam/planning_E02/bases/curated_student_roster.xlsx \
    --grades    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster-v2 exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --output    placement_exam/planning_E02/output/curated_student_roster_E02.xlsx

# 3. Gerar CSV de métricas detalhadas
python3 placement_exam/planning_E02/scripts/build_metrics_csv.py \
    --e01    placement_exam/planning_E01/E01_final_grades.csv \
    --e02    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --output placement_exam/planning_E02/output/E01_E02_metrics.csv
```

---

*Scripts*: `placement_exam/planning_E02/scripts/`
*Última atualização*: 2026-04-14
