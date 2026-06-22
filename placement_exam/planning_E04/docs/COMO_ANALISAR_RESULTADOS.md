# Como Analisar os Resultados dos Exercícios

**Versão**: 1.0 — acumulado E01 → E04
**Última atualização**: 22/06/2026

Este documento é o guia operacional para reproduzir a análise de qualquer exercício. Consolida todo o aprendizado acumulado desde E01, incluindo decisões que mudaram entre exercícios e por quê.

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Arquivos de entrada](#2-arquivos-de-entrada)
3. [Pipeline por exercício](#3-pipeline-por-exercício)
4. [O que mudou de exercício para exercício](#4-o-que-mudou-de-exercício-para-exercício)
5. [Flags de comportamento suspeito](#5-flags-de-comportamento-suspeito)
6. [Penalidade RET100_CAP](#6-penalidade-ret100_cap)
7. [Contas secundárias e account_map](#7-contas-secundárias-e-account_map)
8. [Como tirar o snapshot](#8-como-tirar-o-snapshot)
9. [Localização dos outputs](#9-localização-dos-outputs)
10. [Parâmetros por exercício — referência rápida](#10-parâmetros-por-exercício--referência-rápida)

---

## 1. Pré-requisitos

### Ambiente Python

```bash
# Criar venv (apenas uma vez por repositório)
python3 -m venv placement_exam/.venv
placement_exam/.venv/bin/pip install numpy openpyxl
# boto3 apenas se usar fonte S3
placement_exam/.venv/bin/pip install boto3
```

### Snapshot local

Todos os comandos abaixo assumem que o snapshot de produção já foi baixado para `~/.cache/studyamigo/YYYYMMDD/`. Ver seção 8 para instruções de como tirar o snapshot.

---

## 2. Arquivos de entrada

| Arquivo | Localização | Descrição |
|---------|-------------|-----------|
| `admin.db` | `~/.cache/studyamigo/YYYYMMDD/admin.db` | Usuários cadastrados |
| `user_dbs/` | `~/.cache/studyamigo/YYYYMMDD/user_dbs/` | Bancos individuais `user_{id}.db` |
| `curated_student_roster_v2.csv` | `placement_exam/planning_E04/bases/` | Roster oficial (fonte de verdade desde E02) |
| `account_map.csv` | `placement_exam/planning_E04/bases/` | Mapeamento de contas secundárias |

### Formato do roster CSV

```
Curso, ID, Nome, Email, Caminho, Suggested Tier
SegCiber, 5001, Adriany Praia Serafim, ..., B, Tier 2
```

Colunas aceitas em português ou inglês (case-insensitive). O script usa matching fuzzy de nomes (threshold 0.55) para associar cada aluno do roster a uma conta no `admin.db`.

### Formato do account_map.csv

```
username,roster_name
Mahx.vpc,Marcella Vasconcelos Pacheco da Cruz
Matt,Mateus Ferreira Patrício
theuxzvA7X,Matheus Dias Gomes
```

Mapeia usernames secundários ao nome oficial no roster. Aplicado após o matching fuzzy — o sistema escolhe a conta com mais revisões quando há duplicatas.

---

## 3. Pipeline por exercício

### E01 — Só revisão (sem criação de cartões)

```bash
placement_exam/.venv/bin/python \
    placement_exam/planning_E01/scripts/grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 \
    --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260323/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260323/user_dbs \
    --output placement_exam/planning_E01/output/E01_final_grades.csv
```

> **`--no-card-creation`**: obrigatório em E01. O baralho era compartilhado e pré-carregado — contar criação de cartões aqui zerava o Volume de quem só revisou.

---

### E02 — Introdução de criação de cartões + account_map

```bash
# 1. Notas finais
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster placement_exam/planning_E02/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260414/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260414/user_dbs \
    --output placement_exam/planning_E02/output/E02_final_grades.csv

# 2. Planilha consolidada E01 + E02 (opcional)
python3 placement_exam/planning_E02/scripts/build_roster_xlsx.py \
    --input     placement_exam/planning_E02/bases/curated_student_roster.xlsx \
    --grades    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster-v2 placement_exam/planning_E02/bases/curated_student_roster_v2.csv \
    --output    placement_exam/planning_E02/output/curated_student_roster_E02.xlsx

# 3. CSV de métricas detalhadas V/C/Q/E (opcional)
python3 placement_exam/planning_E02/scripts/build_metrics_csv.py \
    --e01    placement_exam/planning_E01/output/E01_final_grades.csv \
    --e02    placement_exam/planning_E02/output/E02_final_grades.csv \
    --roster placement_exam/planning_E02/bases/curated_student_roster_v2.csv \
    --output placement_exam/planning_E02/output/E01_E02_metrics.csv
```

> **`grade_exercise_v2.py`**: versão reescrita do script de E01. Adicionou suporte a `--account-map`, criação de cartões no Volume, e fontes S3/SSH além do local.

---

### E03 — Adição da avaliação de qualidade de cartões

```bash
# 1. Notas finais
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-04-19 --end 2026-05-17 \
    --label E03 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260518/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260518/user_dbs \
    --output placement_exam/planning_E03/output/E03_final_grades.csv

# 2. Qualidade de cartões (Component B)
placement_exam/.venv/bin/python \
    placement_exam/planning_E03/scripts/assess_card_quality.py \
    --start 2026-04-19 --end 2026-05-17 \
    --deck-prefix PASSAGE_E03 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260518/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260518/user_dbs \
    --detail-output placement_exam/planning_E03/output/E03_card_quality_detail.csv \
    --summary-output placement_exam/planning_E03/output/E03_card_quality_summary.csv
```

> **`assess_card_quality.py`**: novo em E03. Avalia aderência ao formato de cartão por tier (frente, verso, evidência de processo). Score 0–6 por cartão, flags COPIA para cartões copiados do texto-fonte. Parâmetro `--deck-prefix` define qual baralho Component B analisar.

> **`RET100_CAP`**: penalidade introduzida em E03. Ver seção 6.

---

### E04 — Adição do rastreamento de fontes do Component C

```bash
# 1. Notas finais
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-05-19 --end 2026-06-15 \
    --label E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --output placement_exam/planning_E04/output/E04_final_grades.csv

# 2. Qualidade de cartões (Component B)
placement_exam/.venv/bin/python \
    placement_exam/planning_E03/scripts/assess_card_quality.py \
    --start 2026-05-19 --end 2026-06-15 \
    --deck-prefix PASSAGE_E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --detail-output placement_exam/planning_E04/output/E04_card_quality_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_card_quality_summary.csv

# 3. Rastreabilidade de fontes (Component C) — novo em E04
placement_exam/.venv/bin/python \
    placement_exam/planning_E04/scripts/assess_source_tracking.py \
    --start 2026-05-19 --end 2026-06-15 \
    --deck-name AUTHENTIC_E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --detail-output placement_exam/planning_E04/output/E04_source_tracking_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_source_tracking_summary.csv
```

> **`assess_source_tracking.py`**: novo em E04. Verifica cartões-metadado (`📺 FONTE` / `🎵 FONTE`) no baralho `AUTHENTIC_E04`. Valida URLs e referências no formato `Artista — Título`. Conta cartões de vocabulário por fonte. Flags: `SEM_FONTE`, `FONTE_INVALIDA`, `POUCOS_CARTOES`, `POUCAS_FONTES`.

---

## 4. O que mudou de exercício para exercício

| | E01 | E02 | E03 | E04 |
|---|---|---|---|---|
| **Script de notas** | `grade_exercise.py` | `grade_exercise_v2.py` | `grade_exercise_v2.py` | `grade_exercise_v2.py` |
| **Criação de cartões no Volume** | ❌ (`--no-card-creation`) | ✅ | ✅ | ✅ |
| **account_map** | ❌ | ✅ (introduzido) | ✅ | ✅ |
| **Qualidade de cartões** | ❌ | ❌ | ✅ (`assess_card_quality.py`) | ✅ (`--deck-prefix PASSAGE_E04`) |
| **Rastreamento de fontes** | ❌ | ❌ | ❌ | ✅ (`assess_source_tracking.py`) |
| **Penalidade RET100_CAP** | ❌ | ❌ | ✅ (introduzida) | ✅ |
| **Nomes dos baralhos Component B** | — | `PASSAGE_E02_TIER*` | `PASSAGE_E03_TIER*` | `PASSAGE_E04_TIER*` |
| **Baralho Component C** | — | — | — | `AUTHENTIC_E04` |
| **Snapshot** | `20260323` | `20260414` | `20260518` | `20260615` |

### Decisões que não mudam entre exercícios

- **Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E` — igual desde E01
- **Maturidade**: `ivl ≥ 21 dias` — definição constante
- **Threshold de matching fuzzy**: 0.55 — constante
- **Separador de campos Anki**: `\x1f` (ASCII 31) — constante
- **Fonte de dados recomendada**: local (`--local-only`) com snapshot tirado próximo ao fim do período

---

## 5. Flags de comportamento suspeito

Geradas automaticamente por `grade_exercise_v2.py` e exibidas na coluna `flags` do CSV:

| Flag | Condição | Interpretação |
|------|----------|---------------|
| `RET100` | 100% de retenção com ≥ 30 revisões tipo 1/2 | Estatisticamente improvável; não penaliza sozinha se maturidade ≥ 10% |
| `RET100_CAP` | RET100 **e** maturidade < 10% | Nota limitada a 40 — ver seção 6 |
| `LOW_TIME` | `time_sub` < 30% com ≥ 20 revisões | Maioria das respostas abaixo de 2 segundos — possível clique automático |
| `CRAM` | > 80% das revisões no último dia da janela | Estudo concentrado de última hora |

Flags geradas por `assess_card_quality.py`:

| Flag | Condição |
|------|----------|
| `COPIA` | Similaridade média dos cartões com o texto-fonte ≥ 0.85 — cartões copiados literalmente |

Flags geradas por `assess_source_tracking.py`:

| Flag | Condição |
|------|----------|
| `SEM_FONTE` | Baralho AUTHENTIC existe com cartões, mas nenhum cartão-metadado encontrado |
| `FONTE_INVALIDA` | Cartão-metadado existe mas o verso não contém URL nem padrão `Artista — Título` |
| `POUCOS_CARTOES` | Menos cartões de vocabulário que o mínimo para aquela fonte (Tier 1: 5, Tier 2: 7, Tier 3: 8) |
| `POUCAS_FONTES` | Total de fontes abaixo do mínimo do tier (Tier 1 e 2: 1, Tier 3: 2) |
| `SEM_BARALHO` | Aluno não tem o baralho AUTHENTIC no período |

---

## 6. Penalidade RET100_CAP

**Introduzida em E03. Mantida em E04.**

**Condição**: retenção = 100% (zero erros em ≥ 30 revisões de repetição) **e** maturidade < 10%.

**Efeito**: nota final limitada a **40 pontos**, independente do que V, C, Q, E calculem.

**Lógica**: 100% de acerto sem amadurecimento de cartões é estatisticamente improvável em aprendizado genuíno — o SM-2 é projetado para que o aluno erre ocasionalmente conforme os intervalos crescem. Zero erros com cartões jovens indica resposta automática sem leitura real.

**Não penaliza** quando maturidade ≥ 10%: nesse caso, a retenção alta é compatível com aprendizado consolidado ao longo do tempo (ex.: Madson [5066], que tem RET100 com maturidade 100% em E03/E04 e não é penalizado).

**Limitação conhecida**: a heurística não distingue trapaça de conhecimento prévio legítimo. Ver `E04_Suggestions.md` para discussão de possíveis melhorias usando o score do placement exam como parâmetro.

---

## 7. Contas secundárias e account_map

**Introduzido em E02.**

Alguns alunos criaram mais de uma conta no StudyAmigo. O `account_map.csv` mapeia o username da conta secundária ao nome oficial do aluno no roster:

```
username,roster_name
Mahx.vpc,Marcella Vasconcelos Pacheco da Cruz
```

O script aplica o mapeamento após o matching fuzzy de nomes. Quando um aluno tem múltiplas contas, a nota é calculada pela conta com mais revisões no período.

**15 mapeamentos ativos** desde E02. O mesmo arquivo foi reutilizado em E03 e E04 sem alterações — nenhuma conta duplicada nova foi identificada.

> Se surgir nova conta duplicada: adicionar linha ao `account_map.csv` em `placement_exam/planning_E04/bases/` (que é o arquivo canônico desde E04).

---

## 8. Como tirar o snapshot

O snapshot é uma cópia local dos bancos de dados de produção. É necessário tirá-lo próximo ao fim do período do exercício. Há três formas de fazer isso.

### Opção A — Via `activity_monitor.py` com `--cache-dir` (mais simples)

O `activity_monitor.py` é uma ferramenta local de análise de atividade que, como efeito colateral útil, baixa e armazena os bancos em cache. É a forma mais rápida de popular `~/.cache/studyamigo/YYYYMMDD/` sem precisar rodar o pipeline de notas:

```bash
SNAP_DATE=$(date +%Y%m%d)

# Via SSH (fonte ao vivo)
python server/tools/activity_monitor.py \
    --interval custom --start YYYY-MM-DD --end YYYY-MM-DD \
    --host 54.152.109.26 \
    --cache-dir ~/.cache/studyamigo/$SNAP_DATE

# Via S3 (backup mais recente)
python server/tools/activity_monitor.py \
    --interval custom --start YYYY-MM-DD --end YYYY-MM-DD \
    --bucket study-amigo-backups-645069181643 --profile study-amigo \
    --cache-dir ~/.cache/studyamigo/$SNAP_DATE
```

Após a execução, `~/.cache/studyamigo/$SNAP_DATE/` conterá `admin.db` e `user_dbs/` prontos para uso com `--local-only`.

> **Nota**: `activity_monitor.py` é ferramenta local — não está deployada nos containers. Rodar sempre a partir da raiz do repositório.

---

### Opção B — Via SSH direto com `scp`

```bash
SNAP_DATE=$(date +%Y%m%d)
mkdir -p ~/.cache/studyamigo/$SNAP_DATE/user_dbs

# Copia admin.db
scp -i ~/.ssh/study-amigo-aws \
    ubuntu@54.152.109.26:/opt/study-amigo-v15/server/admin.db \
    ~/.cache/studyamigo/$SNAP_DATE/admin.db

# Copia todos os user_dbs
scp -i ~/.ssh/study-amigo-aws -r \
    ubuntu@54.152.109.26:/opt/study-amigo-v15/server/user_dbs/ \
    ~/.cache/studyamigo/$SNAP_DATE/user_dbs/
```

### Opção C — Via `grade_exercise_v2.py` (fonte SSH ou S3)

```bash
placement_exam/.venv/bin/python \
    placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start YYYY-MM-DD --end YYYY-MM-DD \
    --label EXX \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --host 54.152.109.26 \
    --cache-dir ~/.cache/studyamigo/YYYYMMDD
```

O script baixa e armazena em cache automaticamente. Na próxima execução, usar `--local-only --admin-db ... --user-db-dir ...` para evitar re-download.

> **Atenção**: o servidor de produção atual é `study-amigo.app` (SAv1.5), cujos arquivos ficam em `/opt/study-amigo-v15/server/`. Não confundir com `/opt/study-amigo/` (SAv1.0, legado).

---

## 9. Localização dos outputs

### CSVs de notas

| Exercício | Arquivo |
|-----------|---------|
| E01 | `placement_exam/planning_E01/output/E01_final_grades.csv` |
| E02 | `placement_exam/planning_E02/output/E02_final_grades.csv` |
| E03 | `placement_exam/planning_E03/output/E03_final_grades.csv` |
| E04 | `placement_exam/planning_E04/output/E04_final_grades.csv` |

### CSVs de qualidade de cartões (Component B, desde E03)

| Exercício | Detalhe (por cartão) | Resumo (por aluno) |
|-----------|---------------------|-------------------|
| E03 | `planning_E03/output/E03_card_quality_detail.csv` | `planning_E03/output/E03_card_quality_summary.csv` |
| E04 | `planning_E04/output/E04_card_quality_detail.csv` | `planning_E04/output/E04_card_quality_summary.csv` |

### CSVs de rastreamento de fontes (Component C, desde E04)

| Exercício | Detalhe (por fonte) | Resumo (por aluno) |
|-----------|--------------------|--------------------|
| E04 | `planning_E04/output/E04_source_tracking_detail.csv` | `planning_E04/output/E04_source_tracking_summary.csv` |

### Relatórios de análise

| Exercício | Arquivo |
|-----------|---------|
| E02 | `placement_exam/planning_E02/docs/E02_Final_Results_Analysis.md` |
| E03 | `placement_exam/planning_E03/output/E03_Final_Results_Analysis.md` |
| E04 | `placement_exam/planning_E04/output/E04_Final_Results_Analysis.md` |
| E04 Sugestões | `placement_exam/planning_E04/output/E04_Suggestions.md` |

---

## 10. Parâmetros por exercício — referência rápida

| Parâmetro | E01 | E02 | E03 | E04 |
|-----------|-----|-----|-----|-----|
| `--start` | `2026-03-01` | `2026-03-31` | `2026-04-19` | `2026-05-19` |
| `--end` | `2026-03-23` | `2026-04-13` | `2026-05-17` | `2026-06-15` |
| `--label` | `E01` | `E02` | `E03` | `E04` |
| `--no-card-creation` | ✅ | — | — | — |
| `--deck-prefix` (quality) | — | — | `PASSAGE_E03` | `PASSAGE_E04` |
| `--deck-name` (source) | — | — | — | `AUTHENTIC_E04` |
| Snapshot | `20260323` | `20260414` | `20260518` | `20260615` |
| Script de notas | `grade_exercise.py` ¹ | `grade_exercise_v2.py` | `grade_exercise_v2.py` | `grade_exercise_v2.py` |

¹ `placement_exam/planning_E01/scripts/grade_exercise.py` — versão original, não atualizada desde E01. Para re-analisar E01 com a versão atual do script, usar `grade_exercise_v2.py` com `--no-card-creation`.

---

*Referências: `QUICKSTART_GRADE_EXERCISE.md` (E01), `QUICKSTART.md` (E02), `E03_Final_Results_Analysis.md`, `E04_Final_Results_Analysis.md`, `E04_Suggestions.md`*
