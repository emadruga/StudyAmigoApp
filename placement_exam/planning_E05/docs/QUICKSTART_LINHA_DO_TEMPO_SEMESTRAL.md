# Quickstart — Linha do Tempo Semestral de um Aluno

Script: `placement_exam/scripts/create_semester_timeline.py`

Gera um relatório `.md` com a linha do tempo de atividade de um aluno ao longo do semestre, exercício a exercício, incluindo: revisões, cartões criados, dias ativos, notas calculadas e flags comportamentais.

---

## 1. Pré-requisitos

- **Python 3.9+** com `numpy` instalado
- **Snapshots locais** em `~/.cache/studyamigo/YYYYMMDD/` (cada um com `admin.db` e `user_dbs/`)
- **Roster** — CSV com a lista de alunos do semestre (colunas: Curso, ID, Nome, Email, Caminho, Suggested Tier)
- **Account maps** — em `placement_exam/planning_<label>/bases/account_map.csv` (se houver contas duplicadas)

O script depende do `grade_exercise_v2.py` em `placement_exam/planning_E02/scripts/`, que é importado como módulo.

---

## 2. JSON de configuração

O arquivo JSON define o semestre: qual roster usar e a lista de exercícios com suas datas.

### Formato

```json
{
  "roster": "caminho/relativo/ao/roster.csv",
  "exercises": [
    {"label": "E01", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "review_only": true},
    {"label": "E02", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
    {"label": "E03", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
  ]
}
```

### Campos

| Campo | Obrigatório | Descrição |
|---|---|---|
| `roster` | Sim | Caminho do CSV do roster (relativo à raiz do projeto `StudyAmigoApp/`) |
| `exercises[].label` | Sim | Identificador do exercício (ex.: `E01`, `E02`). Usado para localizar `account_map.csv` em `planning_<label>/bases/` |
| `exercises[].start` | Sim | Data de início do exercício (YYYY-MM-DD, inclusive) |
| `exercises[].end` | Sim | Data de fim do exercício (YYYY-MM-DD, inclusive até 23:59:59 local) |
| `exercises[].review_only` | Não | Se `true`, exclui criação de cartões da nota (usar em E01 onde o deck Verbal Tenses é pré-carregado). Default: `false` |

### Exemplo — 2026.1

```json
{
  "roster": "placement_exam/planning_E05/bases/curated_student_roster_v2.csv",
  "exercises": [
    {"label": "E01", "start": "2026-03-02", "end": "2026-03-29", "review_only": true},
    {"label": "E02", "start": "2026-03-31", "end": "2026-04-12"},
    {"label": "E03", "start": "2026-04-19", "end": "2026-05-17"},
    {"label": "E04", "start": "2026-05-19", "end": "2026-06-15"},
    {"label": "E05", "start": "2026-06-16", "end": "2026-07-06"}
  ]
}
```

Arquivo pronto para uso: `placement_exam/scripts/semester_config_2026_1.json`

---

## 3. Formas de uso

Todos os comandos devem ser executados a partir da raiz do projeto (`StudyAmigoApp/`).

### 3.1 Gerar timeline de um aluno por student_id

```bash
python placement_exam/scripts/create_semester_timeline.py \
  --config placement_exam/scripts/semester_config_2026_1.json \
  --student-id 3006
```

Gera `timeline_3006.md` no diretório atual.

### 3.2 Gerar timeline de um aluno por nome

```bash
python placement_exam/scripts/create_semester_timeline.py \
  --config placement_exam/scripts/semester_config_2026_1.json \
  --student-name "Arthur"
```

Busca parcial, case-insensitive. Se encontrar mais de um aluno, lista os resultados e gera para todos.

### 3.3 Especificar arquivo de saída

```bash
python placement_exam/scripts/create_semester_timeline.py \
  --config placement_exam/scripts/semester_config_2026_1.json \
  --student-id 3006 \
  --output placement_exam/planning_E05/docs/timeline_arthur.md
```

### 3.4 Gerar timelines para todos os alunos

```bash
python placement_exam/scripts/create_semester_timeline.py \
  --config placement_exam/scripts/semester_config_2026_1.json \
  --output-dir placement_exam/planning_E05/output/timelines/
```

Cria um arquivo `timeline_<student_id>.md` para cada aluno do roster.

### 3.5 Usar snapshots de outro local

```bash
python placement_exam/scripts/create_semester_timeline.py \
  --config placement_exam/scripts/semester_config_2026_1.json \
  --student-id 3006 \
  --snapshot-base /mnt/backup/studyamigo_snapshots
```

Default: `~/.cache/studyamigo`.

---

## 4. O que o script faz internamente

1. **Carrega o roster** e identifica o(s) aluno(s) alvo
2. **Para cada exercício** no JSON:
   - Encontra automaticamente o snapshot mais próximo após a data de fim (busca em `~/.cache/studyamigo/YYYYMMDD/`)
   - Carrega o `admin.db` do snapshot e faz fuzzy matching do roster com as contas
   - Procura `account_map.csv` em `placement_exam/planning_<label>/bases/` e aplica, se existir
   - Processa **todos** os alunos do snapshot para calcular os vetores de normalização da turma (p95_rev, min_rev, p95_card)
   - Extrai métricas do aluno alvo: revisões, cartões, dias ativos, retenção, maturidade
   - Calcula V, C, Q, E e nota final usando a fórmula do `grade_exercise_v2.py`
   - Verifica flags: RET100, RET100_CAP, CRAM, LOW_TIME
   - Detalha atividade por dia e deck
3. **Gera o relatório `.md`** com:
   - Cronograma oficial do semestre
   - Tabela resumo com todas as métricas e notas
   - Tabela de produção consolidada (dias totais, dias com atividade, cards criados, cards revisados)
   - Observações por exercício com detalhes de atividade e flags

---

## 5. Saída gerada

O `.md` contém as seguintes seções:

### Cabeçalho
Nome, curso, tier, student_id, email e data de geração.

### Cronograma oficial
Tabela com início, fim e duração de cada exercício.

### Resumo por exercício
```
| Ex | Período | Revs | Cria | Dias | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
```

### Produção consolidada (E02 em diante)
```
| Ex | Dias totais | Dias c/ atividade | Cards criados | Cards revisados |
```

### Observações
Detalhes por exercício: atividade por dia/deck, flags detectadas, notas relevantes.

---

## 6. Como preparar para um novo semestre

### 6.1 Criar o JSON de configuração

Copiar o arquivo do semestre anterior e ajustar:

```bash
cp placement_exam/scripts/semester_config_2026_1.json \
   placement_exam/scripts/semester_config_2026_2.json
```

Editar `semester_config_2026_2.json`:
- Atualizar o caminho do `roster` (apontar para o roster do novo semestre)
- Substituir as datas de `start` e `end` de cada exercício conforme o cronograma oficial
- Ajustar `review_only: true` no primeiro exercício (ou em qualquer exercício que não envolva criação de cartões)
- Adicionar ou remover exercícios conforme necessário

### 6.2 Garantir os snapshots

O script precisa de snapshots em `~/.cache/studyamigo/YYYYMMDD/` com:
- `admin.db` — banco de usuários
- `user_dbs/` — diretório com os bancos individuais (`user_<ID>.db`)

Os snapshots são gerados pelo backup rotineiro do S3 e baixados com o `grade_exercise_v2.py` (opção `--cache-dir`). Manter ao menos um snapshot por exercício, preferencialmente logo após o prazo de cada exercício.

**Snapshots recomendados:** um por prazo de exercício (±1 dia após o `end`). O script busca o snapshot mais próximo >= dia seguinte ao `end`, ou o mais recente disponível.

### 6.3 Criar account_maps (se necessário)

Se algum aluno tiver contas duplicadas ou username diferente do nome no roster, criar `account_map.csv` em:

```
placement_exam/planning_<label>/bases/account_map.csv
```

Formato:
```csv
username,roster_name
Arthurx,Arthur Alves do Nascimento
```

O script procura automaticamente o `account_map.csv` no diretório `planning_<label>/bases/` de cada exercício.

### 6.4 Criar o roster

O roster é um CSV com colunas (aceita nomes em português ou inglês):

```csv
Curso,ID,Nome,Email,Caminho,Suggested Tier
Biotecnologia,3006,Arthur Alves do Nascimento,arthuralvesnas@gmail.com,B,Tier 1
```

Colunas aceitas: `Course/Curso`, `ID`, `Name/Nome`, `Email`, `Path/Caminho`, `Suggested Tier`.

---

## 7. Fórmula de avaliação

O script usa exatamente a mesma fórmula do grader oficial (`grade_exercise_v2.py`):

```
Grade = 0.25 × V + 0.25 × C + 0.30 × Q + 0.20 × E
```

| Componente | Cálculo |
|---|---|
| **V** (Volume) | `0.60 × rev_score + 0.40 × card_score` (normalizado por p95 da turma) |
| **C** (Consistência) | `0.50 × participation + 0.50 × (1 - cramming_ratio) × 100` |
| **Q** (Qualidade) | `0.70 × retention_pct + 0.30 × maturity_pct` |
| **E** (Engagement) | `0.50 × time_sub + 0.50 × ease_sub` (ou só `ease_sub` se time_data_missing) |

Conceitos: A (≥90), B (≥80), C (≥70), D (≥60), F (<60).

### Flags comportamentais

| Flag | Condição |
|---|---|
| **RET100** | ≥30 revisões type=1/2 com 100% retenção |
| **RET100_CAP** | RET100 + maturidade <10% → nota capada em 40 |
| **CRAM** | >80% das revisões no último dia E total ≥20 |
| **LOW_TIME** | Tempo de revisão <30% E total ≥20 |

### Notas sobre a fórmula

- **Retenção** conta apenas revisões type=1 (Review) e type=2 (Relearn). "Correto" = `ease >= 3` (em Anki, ease=2 é "Hard", que conta como erro para o grader).
- **Normalização** usa p95 da turma (não p100) para mitigar outliers.
- Para exercícios com `review_only: true`, V usa apenas `rev_score` (sem cards).
- O componente E usa `mean_factor = 2500` (default Anki) para alunos sem revisões, resultando em E ≈ 54.5.

---

## 8. Questões de fuso horário

O script usa **datetimes naive** (sem tzinfo), o que faz `datetime.timestamp()` converter pela timezone do sistema (tipicamente America/Sao_Paulo = UTC-3). Isso é intencional: uma revisão feita às 21:42 BRT em 12/04 tem timestamp UTC de 13/04 00:42. Usando boundaries UTC, essa revisão seria excluída do período de E02 (que termina em 12/04). Com boundaries locais, é corretamente incluída.

Se o script for executado em uma máquina com timezone diferente de BRT, os resultados podem diferir. Para garantir consistência, executar com:

```bash
TZ=America/Sao_Paulo python placement_exam/scripts/create_semester_timeline.py ...
```

---

## 9. Troubleshooting

### "Roster not found"
O caminho do roster no JSON é relativo à raiz do projeto (`StudyAmigoApp/`). Verificar que o arquivo existe no caminho especificado.

### "Nenhum snapshot encontrado"
Verificar que `~/.cache/studyamigo/` contém diretórios com formato `YYYYMMDD/` e que possuem `admin.db` e `user_dbs/` dentro.

### Notas diferentes do grader oficial
Causas possíveis:
- **Datas de período diferentes** — o JSON deve usar exatamente as mesmas datas do cronograma oficial.
- **Snapshot diferente** — o script seleciona automaticamente o snapshot mais próximo; o grader pode ter usado outro. Conferir na saída do script qual snapshot foi selecionado para cada exercício.
- **Account map ausente** — se o aluno tem conta duplicada e o `account_map.csv` não existe em `planning_<label>/bases/`, o script pode usar a conta errada.

### Aluno não encontrado
- Conferir que o `student_id` ou nome parcial corresponde a uma entrada no roster CSV.
- Com `--student-name`, a busca é parcial e case-insensitive (ex.: `"ana"` encontra "Ana Luiza", "Ana Julia", etc.).

### E01 com nota 0.0
Comportamento esperado. Alunos sem nenhuma revisão em E01 recebem nota 0 pelo grader (todos os componentes zerados). Isso difere de cálculos manuais que atribuem E>0 pelo mean_factor dos cartões existentes.

---

## 10. Referência de argumentos CLI

| Argumento | Obrigatório | Default | Descrição |
|---|---|---|---|
| `--config` | Sim | — | Caminho do JSON de configuração do semestre |
| `--student-id` | Não | — | Filtrar por student_id do roster |
| `--student-name` | Não | — | Filtrar por nome (busca parcial, case-insensitive) |
| `--output` | Não | `timeline_<id>.md` | Caminho do .md de saída |
| `--output-dir` | Não | — | Diretório para gerar um .md por aluno (modo batch) |
| `--snapshot-base` | Não | `~/.cache/studyamigo` | Diretório base dos snapshots |

Se nem `--student-id` nem `--student-name` forem passados, o script gera timeline para **todos** os alunos do roster.

---

*Última atualização: 07/07/2026. Arquivo de referência: `placement_exam/scripts/create_semester_timeline.py`.*
