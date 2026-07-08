# Plano: Como Criar a Linha do Tempo Semestral de um Aluno

Este documento descreve o processo completo para auditar e reconstituir o histórico de atividade de qualquer aluno no StudyAmigo ao longo de um semestre, produzindo uma linha do tempo exercício a exercício com notas recalculadas.

---

## Visão geral do processo

```
1. Identificar contas do aluno (admin.db)
       ↓
2. Verificar atividade em cada conta (qual é a conta ativa?)
       ↓
3. Mapear revisões e criações por período usando datas oficiais do cronograma
       ↓
4. Detalhar atividade por dia e deck usando o snapshot da época
       ↓
5. Verificar condição RET100_CAP
       ↓
6. Verificar flag CRAM
       ↓
7. Verificar entrega via .apkg (se houver arquivo submetido)
       ↓
8. Calcular as notas finais com os parâmetros de turma do exercício
       ↓
9. Comparar com nota oficial do grader e registrar discrepâncias
```

---

## Pré-requisitos

### Arquivos necessários
- **Snapshots locais** em `~/.cache/studyamigo/YYYYMMDD/` — um por data relevante do semestre
  - `admin.db` — lista de usuários (username, user_id, nome real)
  - `user_dbs/user_<ID>.db` — banco Anki de cada aluno
- **Cronograma oficial** com datas exatas de início e fim de cada exercício
- **Parâmetros de normalização da turma** por exercício (p95_rev, min_rev, p95_card) — extraídos do grader
- **Arquivo .apkg** submetido pelo aluno via Google Forms (opcional, para validação cruzada)
- **Roster** — lista com student_id, nome real e curso de cada aluno
- **account_map.csv** — mapeamento de usernames alternativos para nomes do roster

### Convenções de tipo no revlog
| type | Significado |
|---|---|
| 0 | Learn (fase de aprendizagem inicial) |
| 1 | Review (revisão espaçada — conta para RET100) |
| 2 | Relearn (reaprendizagem após erro — conta para RET100) |
| 3 | Cram (modo manual, ignorado nas métricas) |

**Filtro padrão para "revisões válidas":** `WHERE type != 3`

---

## Passo 1 — Identificar as contas do aluno no admin.db

Buscar pelo nome real ou parte do username no snapshot mais recente.

```python
import sqlite3

SNAPSHOT = '~/.cache/studyamigo/20260706'  # ajustar para o snapshot mais recente
NOME_BUSCA = 'arthur'  # parte do nome real ou username

conn = sqlite3.connect(f'{SNAPSHOT}/admin.db')
cur = conn.cursor()
cur.execute('''
    SELECT user_id, username, name
    FROM users
    WHERE LOWER(username) LIKE ? OR LOWER(name) LIKE ?
''', (f'%{NOME_BUSCA}%', f'%{NOME_BUSCA}%'))
for row in cur.fetchall():
    print(row)
conn.close()
```

**O que procurar:**
- Alunos com **duas contas** com o mesmo `name` real → possível conta fantasma
- Contas com username genérico (ex.: apenas o primeiro nome) geralmente são contas criadas por importação automática de deck, sem uso real
- A conta ativa costuma ser a de username mais específico (sufixo, variação)

**Ação se houver conta duplicada:** verificar qual conta tem atividade real (Passo 2) e adicionar a conta ativa ao `account_map.csv` do exercício em questão.

---

## Passo 2 — Verificar atividade em cada conta

Para cada `user_id` encontrado, contar notas e revisões totais.

```python
import sqlite3

SNAPSHOT = '~/.cache/studyamigo/20260706'
USER_IDS = [32, 49]  # preencher com os IDs encontrados no Passo 1

for uid in USER_IDS:
    db = f'{SNAPSHOT}/user_dbs/user_{uid}.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM notes')
    notes = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM revlog WHERE type != 3')
    revs = cur.fetchone()[0]
    print(f'user_{uid}: {notes} notas, {revs} revisões')
    conn.close()
```

**Interpretação:**
- `0 revisões` → conta nunca utilizada (fantasma)
- Conta com revisões → conta ativa; usar esse `user_id` para toda a análise restante

---

## Passo 3 — Mapear revisões por período (datas oficiais do cronograma)

Usando o snapshot mais recente (contém o revlog completo), quantificar revisões, dias ativos e notas criadas por exercício.

> **Atenção:** se o aluno deletou decks ao longo do semestre, as **notas** (tabela `notes`) no snapshot final podem não refletir os exercícios antigos. As **revisões** (tabela `revlog`) persistem mesmo após deleção dos decks. Para contagem de notas criadas por período em exercícios antigos, use os snapshots da época (Passo 4).

```python
import sqlite3, datetime

SNAPSHOT = '~/.cache/studyamigo/20260706'
USER_ID = 49

# Ajustar as datas conforme o cronograma oficial
EXERCISES = [
    ('E01', '2026-03-02', '2026-03-29'),
    ('E02', '2026-03-31', '2026-04-12'),
    ('E03', '2026-04-19', '2026-05-17'),
    ('E04', '2026-05-19', '2026-06-15'),
    ('E05', '2026-06-16', '2026-07-06'),
]

db = f'{SNAPSHOT}/user_dbs/user_{USER_ID}.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

for label, s, e in EXERCISES:
    s_ms = int(datetime.datetime(*(int(x) for x in s.split('-'))).timestamp() * 1000)
    e_ms = int((datetime.datetime(*(int(x) for x in e.split('-'))) + datetime.timedelta(days=1)).timestamp() * 1000)

    cur.execute('SELECT COUNT(*) FROM revlog WHERE type!=3 AND id>=? AND id<?', (s_ms, e_ms))
    revs = cur.fetchone()[0]

    cur.execute('''
        SELECT COUNT(DISTINCT DATE(id/1000,"unixepoch","localtime"))
        FROM revlog WHERE type!=3 AND id>=? AND id<?
    ''', (s_ms, e_ms))
    days = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM notes WHERE id>=? AND id<?', (s_ms, e_ms))
    notes = cur.fetchone()[0]

    print(f'{label}: {revs} revs, {days} dias ativos, {notes} notas criadas')

conn.close()
```

**Datas importantes:**
- O campo `id` do `revlog` é um timestamp em **milissegundos** desde epoch UTC
- O campo `id` da tabela `notes` também é timestamp em milissegundos (momento da criação)
- O fim do período deve usar `+1 dia` sem hora (ou seja, `e_ms` aponta para o início do dia seguinte)
- Usar `"localtime"` no SQLite para exibir datas no fuso local

---

## Passo 4 — Detalhar atividade por dia e deck (snapshots da época)

Para cada exercício, usar o snapshot mais próximo do fim do prazo para listar a atividade detalhada por dia e por deck.

```python
import sqlite3, datetime, json

# Selecionar snapshot e período do exercício a analisar
SNAPSHOT = '~/.cache/studyamigo/20260414'   # snapshot da época do exercício
USER_ID = 49
START = datetime.datetime(2026, 3, 31)       # início do exercício (ajustar)
END   = datetime.datetime(2026, 4, 13)       # dia seguinte ao fim do prazo

s_ms = int(START.timestamp() * 1000)
e_ms = int(END.timestamp() * 1000)

db = f'{SNAPSHOT}/user_dbs/user_{USER_ID}.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Carregar nomes dos decks (armazenados como JSON na tabela col)
cur.execute('SELECT decks FROM col')
decks = json.loads(cur.fetchone()[0])

# Revisões por dia e deck
cur.execute('''
    SELECT DATE(r.id/1000, 'unixepoch', 'localtime') AS dia,
           c.did,
           COUNT(r.id)                                AS total,
           SUM(CASE WHEN r.ease >= 2 THEN 1 ELSE 0 END) AS ok
    FROM revlog r
    JOIN cards c ON c.id = r.cid
    WHERE r.type != 3 AND r.id >= ? AND r.id < ?
    GROUP BY 1, 2
    ORDER BY 1
''', (s_ms, e_ms))

for dia, did, total, ok in cur.fetchall():
    nome_deck = decks.get(str(did), {}).get('name', f'DID {did}')
    print(f'{dia}: {total} revs ({ok} OK) — {nome_deck}')

# Notas criadas no período
cur.execute('SELECT COUNT(*) FROM notes WHERE id >= ? AND id < ?', (s_ms, e_ms))
print(f'Notas criadas no período: {cur.fetchone()[0]}')

conn.close()
```

**Qual snapshot usar por exercício:**

| Exercício | Snapshot recomendado | Observação |
|---|---|---|
| E01 | snapshot pós-E01 | ou o mais antigo disponível |
| E02 | snapshot ~14/04 | captura o estado após o prazo de E02 |
| E03 | snapshot ~18/05 | captura o estado após o prazo de E03 |
| E04 | snapshot ~16/06 | captura o estado após o prazo de E04 |
| E05 | snapshot final | snapshot mais recente disponível |

**Alerta sobre decks deletados:** se o deck não existe mais no snapshot usado, o `JOIN cards c` não retornará linhas para aquele deck. Nesse caso, usar o snapshot da época correta resolve o problema de nomes, mas os cartões podem já não existir. Para contar revisões, a tabela `revlog` é suficiente mesmo sem o JOIN (use `cid` em vez de `c.did`).

---

## Passo 5 — Verificar condição RET100_CAP

A penalidade RET100_CAP é aplicada pelo grader quando **todas** as condições abaixo são verdadeiras:

1. `ret_total >= 30` — quantidade de revisões do tipo **1 (Review)** ou **2 (Relearn)** no período
2. `retention_pct == 100%` — nenhum erro (`ease < 2`) nas revisões válidas
3. `maturity_pct < 10%` — menos de 10% dos cartões revisados com `ivl >= 21 dias`

> **Atenção:** o limiar é **30 revisões type=1/2**, não 30 revisões totais. Alunos que nunca saem da fase Learn (type=0) raramente atingem esse limiar.

```python
import sqlite3, datetime

# Ajustar lista de exercícios, snapshots e user_id
EXERCISES = [
    ('E02', '2026-03-31', '2026-04-12', '20260414'),
    ('E03', '2026-04-19', '2026-05-17', '20260518'),
    ('E04', '2026-05-19', '2026-06-15', '20260706'),
    ('E05', '2026-06-16', '2026-07-06', '20260706'),
]
USER_ID = 49

for label, s, e, snap in EXERCISES:
    db = f'~/.cache/studyamigo/{snap}/user_dbs/user_{USER_ID}.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    s_ms = int(datetime.datetime(*(int(x) for x in s.split('-'))).timestamp() * 1000)
    e_ms = int((datetime.datetime(*(int(x) for x in e.split('-'))) + datetime.timedelta(days=1)).timestamp() * 1000)

    cur.execute('SELECT COUNT(*) FROM revlog WHERE type!=3 AND id>=? AND id<?', (s_ms, e_ms))
    total = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM revlog WHERE type IN (1,2) AND id>=? AND id<?', (s_ms, e_ms))
    ret_total = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM revlog WHERE type!=3 AND ease>=2 AND id>=? AND id<?', (s_ms, e_ms))
    ok = cur.fetchone()[0]

    ret_pct = ok / total * 100 if total else 0
    flag = ret_total >= 30 and ret_pct == 100.0

    print(f'{label}: total={total}, type1/2={ret_total} (limiar=30), ret={ret_pct:.1f}%, RET100={flag}')
    conn.close()
```

**Interpretação:**
- `RET100=True` → grader aplica cap na nota (nota máxima reduzida)
- `RET100=False` → nenhuma penalidade por esse critério

---

## Passo 6 — Verificar flag CRAM

A flag CRAM é acionada quando: `cramming_ratio > 0.80` **E** `total_reviews >= 20`.

`cramming_ratio` = revisões no último dia do período ÷ total de revisões no período.

```python
import sqlite3, datetime

EXERCISES = [
    ('E02', '2026-03-31', '2026-04-12', '20260414'),
    ('E03', '2026-04-19', '2026-05-17', '20260518'),
    ('E04', '2026-05-19', '2026-06-15', '20260706'),
    ('E05', '2026-06-16', '2026-07-06', '20260706'),
]
USER_ID = 49

for label, s, e, snap in EXERCISES:
    db = f'~/.cache/studyamigo/{snap}/user_dbs/user_{USER_ID}.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    s_ms = int(datetime.datetime(*(int(x) for x in s.split('-'))).timestamp() * 1000)
    e_ms = int((datetime.datetime(*(int(x) for x in e.split('-'))) + datetime.timedelta(days=1)).timestamp() * 1000)

    cur.execute('SELECT COUNT(*) FROM revlog WHERE type!=3 AND id>=? AND id<?', (s_ms, e_ms))
    total = cur.fetchone()[0]

    cur.execute('''
        SELECT MAX(DATE(id/1000,"unixepoch","localtime"))
        FROM revlog WHERE type!=3 AND id>=? AND id<?
    ''', (s_ms, e_ms))
    last_day = cur.fetchone()[0]

    last_day_revs = 0
    if last_day:
        cur.execute('''
            SELECT COUNT(*) FROM revlog
            WHERE type!=3 AND DATE(id/1000,"unixepoch","localtime")=?
        ''', (last_day,))
        last_day_revs = cur.fetchone()[0]

    ratio = last_day_revs / total if total else 0
    cram  = ratio > 0.80 and total >= 20

    print(f'{label}: total={total}, last_day={last_day_revs}, ratio={ratio:.2f}, CRAM={cram}')
    conn.close()
```

> **Nota:** o grader calcula `cramming_ratio` sobre o **último dia real de atividade** dentro do período, não necessariamente o último dia do prazo.

---

## Passo 7 — Verificar entrega via .apkg (opcional)

Quando o aluno submeteu um arquivo `.apkg` via Google Forms, validar que:
1. O arquivo é idêntico (ou subconjunto fiel) do estado de produção na data correspondente
2. A atividade registrada ocorreu dentro do prazo do exercício

```bash
# 1. Extrair o .apkg (formato ZIP)
mkdir -p /tmp/aluno_apkg
cp "/caminho/para/arquivo.apkg" /tmp/aluno_apkg/colecao.zip
cd /tmp/aluno_apkg && unzip -o colecao.zip -d extracted/
# O banco SQLite fica em: extracted/collection.anki2
```

```python
import sqlite3, datetime

# Verificar última revisão registrada no .apkg
apkg = sqlite3.connect('/tmp/aluno_apkg/extracted/collection.anki2')
cur = apkg.cursor()

cur.execute('SELECT MAX(id) FROM revlog')
last_ms = cur.fetchone()[0]
if last_ms:
    print(f'Última revisão: {datetime.datetime.fromtimestamp(last_ms/1000)}')

# Comparar IDs de revisão com o snapshot de produção da época
prod = sqlite3.connect('~/.cache/studyamigo/YYYYMMDD/user_dbs/user_<ID>.db')
pcur = prod.cursor()

pcur.execute('SELECT id FROM revlog WHERE type!=3 ORDER BY id')
prod_ids = set(r[0] for r in pcur.fetchall())

cur.execute('SELECT id FROM revlog WHERE type!=3 ORDER BY id')
apkg_ids = set(r[0] for r in cur.fetchall())

print(f'IDs só no .apkg:      {len(apkg_ids - prod_ids)}')
print(f'IDs só em produção:   {len(prod_ids - apkg_ids)}')
print(f'Total .apkg:          {len(apkg_ids)}')
print(f'Total produção:       {len(prod_ids)}')

# Revisões no período do exercício
EX_START = datetime.datetime(2026, 4, 19)
EX_END   = datetime.datetime(2026, 5, 18)   # dia seguinte ao prazo
s_ms = int(EX_START.timestamp() * 1000)
e_ms = int(EX_END.timestamp() * 1000)
cur.execute('SELECT COUNT(*) FROM revlog WHERE type!=3 AND id>=? AND id<?', (s_ms, e_ms))
print(f'Revisões no período do exercício: {cur.fetchone()[0]}')

apkg.close()
prod.close()
```

**Interpretação dos resultados:**
- `IDs só no .apkg = 0` e `IDs só em produção = 0` → arquivo idêntico ao snapshot de produção ✓
- `IDs só no .apkg > 0` → aluno tem atividade local não sincronizada com o servidor (investigar)
- `IDs só em produção > 0` → arquivo é subconjunto do estado de produção (pode ser exportação parcial)
- Última revisão posterior ao prazo → atividade fora do prazo (verificar se revisões dentro do prazo são suficientes)

---

## Passo 8 — Calcular as notas finais

### Fórmula de avaliação

```
Grade = 0.25×V + 0.25×C + 0.30×Q + 0.20×E

V (Volume):
    rev_score  = clip((revs - min_rev) / (p95_rev - min_rev) × 100)
    card_score = clip(created / p95_card × 100)
    V = 0.60 × rev_score + 0.40 × card_score

C (Consistência):
    C = clip(days_active / period_days × 100)

Q (Qualidade):
    Q = 0.70 × retention_pct + 0.30 × maturity_pct
    retention_pct = % de revisões válidas sem erro (ease >= 2)
    maturity_pct  = % de cartões revisados com intervalo (ivl) >= 21 dias

E (Ease):
    E = clip((mean_factor - 1300) / (3500 - 1300) × 100)
    mean_factor = média do fator de facilidade (ease) dos cartões do aluno
    (quando time_data_missing=True, usa ease_sub calculado a partir dos cartões existentes)

clip(x) = min(max(x, 0), 100)
```

### Parâmetros de normalização

Os parâmetros `p95_rev`, `min_rev` e `p95_card` são calculados sobre toda a turma para cada exercício e são obtidos do output do grader automático ou extraídos manualmente.

### Cálculo

```python
EASE_MIN, EASE_MAX = 1300, 3500

def clip(x):
    return min(max(x, 0), 100)

def calc_grade(revs, created, days, period_days, ret_pct, mat_pct, mean_factor,
               p95_rev, min_rev, p95_card):
    rev_score  = clip((revs - min_rev) / (p95_rev - min_rev) * 100) if revs > 0 else 0
    card_score = clip(created / p95_card * 100) if p95_card > 0 else 0
    V = 0.60 * rev_score + 0.40 * card_score
    C = clip(days / period_days * 100)
    Q = 0.70 * ret_pct + 0.30 * mat_pct
    E = clip((mean_factor - EASE_MIN) / (EASE_MAX - EASE_MIN) * 100)
    grade = 0.25*V + 0.25*C + 0.30*Q + 0.20*E
    return grade, V, C, Q, E

def letter(grade):
    if grade >= 85: return 'A'
    if grade >= 75: return 'B'
    if grade >= 65: return 'C'
    if grade >= 55: return 'D'
    return 'F'

# Exemplo — preencher com dados apurados nos passos anteriores
# (ex, revs, cards_criados, dias_ativos, periodo_dias, ret%, mat%, mean_factor, p95_rev, min_rev, p95_card)
exercises = [
    ('E01',  0,  0,  0, 28,  0.0,  0.0, 2500,   1, 1,  1),
    ('E02', 16, 15,  2, 13,100.0,  0.0, 2500, 159, 1, 35),
    ('E03', 34, 18,  1, 29,100.0,  0.0, 2500, 209, 1, 28),
    ('E04',  3,  0,  1, 28, 66.7,  0.0, 2500, 370, 3, 39),
    ('E05', 20, 15,  1, 21,100.0,  0.0, 2500, 199, 3, 23),
]

print(f"{'Ex':<4} {'V':>5} {'C':>5} {'Q':>5} {'E':>5} {'Nota':>6} {'L'}")
for ex, revs, created, days, period_days, ret, mat, mf, p95r, minr, p95c in exercises:
    grade, V, C, Q, E = calc_grade(revs, created, days, period_days, ret, mat, mf, p95r, minr, p95c)
    print(f'{ex:<4} {V:>5.1f} {C:>5.1f} {Q:>5.1f} {E:>5.1f} {grade:>6.1f} {letter(grade)}')
```

---

## Passo 9 — Comparar com nota oficial e registrar discrepâncias

Após calcular a nota auditada, comparar com a nota registrada pelo grader automático e documentar as causas de qualquer diferença.

**Causas comuns de discrepância:**

| Causa | Efeito na nota oficial |
|---|---|
| Grader usou user_id errado (conta fantasma) | Nota 0 ou muito baixa |
| Grader usou datas de período incorretas | Inclui/exclui atividade indevida |
| Grader usou métricas cumulativas (sem corte de datas) | Infla V, C e Q |
| Aluno deletou decks entre snapshots | Nota criadas = 0 no snapshot final |
| account_map.csv não contém o username real do aluno | Grader usa conta errada |

**Ação corretiva:**
- Erro de mapeamento de conta → adicionar username correto ao `account_map.csv` e regredir o grader, ou corrigir manualmente
- Outros erros de cálculo → documentar e corrigir manualmente no registro do aluno

---

## Armadilhas conhecidas

1. **Timestamps em milissegundos** — `revlog.id` e `notes.id` são em ms; dividir por 1000 para converter para segundos antes de usar `datetime.fromtimestamp()`.

2. **Fuso horário** — usar `"localtime"` nas funções de data SQLite para obter a data local correta; sem isso, revisões feitas à noite podem aparecer no dia seguinte (UTC).

3. **Decks deletados** — o `JOIN revlog r JOIN cards c ON c.id=r.cid` falha silenciosamente para cartões cujo deck foi deletado; verificar se o número de revisões retornado bate com o esperado.

4. **type=3 (Cram)** — sempre excluir com `WHERE type != 3`; revisões em modo Cram não contam para as métricas de avaliação.

5. **E (Ease) com time_data_missing** — quando o aluno nunca teve revisões com timestamp de tempo registrado (ou o campo `time` está zerado), o grader usa `ease_sub` calculado a partir do `factor` médio dos cartões. O resultado é um E fixo próximo de 54.5 para `mean_factor=2500` (padrão Anki).

6. **RET100_CAP threshold** — o cap exige **≥ 30 revisões type=1/2**, não 30 revisões totais. Alunos em fase Learn (type=0) dificilmente atingem esse limiar.

7. **CRAM só aciona com total ≥ 20** — alunos com menos de 20 revisões no período nunca têm a flag CRAM, mesmo estudando tudo no último dia.

8. **Datas oficiais do cronograma** — usar sempre as datas do cronograma oficial da disciplina; datas aproximadas podem incluir ou excluir atividade de exercícios adjacentes, distorcendo todas as métricas.

---

## Template de saída (Resumo Final)

```markdown
| Ex | Período | Revs | Cria | Dias | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E01 | DD/MM–DD/MM | ... | ... | ... | ...% | ...% | ... | ... | ... | ... | ... | F/D/C/B/A | |
| E02 | DD/MM–DD/MM | ... | ... | ... | ...% | ...% | ... | ... | ... | ... | ... | F/D/C/B/A | |
| E03 | DD/MM–DD/MM | ... | ... | ... | ...% | ...% | ... | ... | ... | ... | ... | F/D/C/B/A | CRAM? |
| E04 | DD/MM–DD/MM | ... | ... | ... | ...% | ...% | ... | ... | ... | ... | ... | F/D/C/B/A | |
| E05 | DD/MM–DD/MM | ... | ... | ... | ...% | ...% | ... | ... | ... | ... | ... | F/D/C/B/A | CRAM? |

| Ex | Dias totais | Dias c/ atividade | Cards criados | Cards revisados |
|---|---|---|---|---|
| E02 | ... | ... | ... | ... |
| E03 | ... | ... | ... | ... |
| E04 | ... | ... | ... | ... |
| E05 | ... | ... | ... | ... |

| Ex | Nota oficial | Nota auditada | Causa da diferença |
|---|---|---|---|
| E01 | ... | ... | ... |
| E02 | ... | ... | ... |
| E03 | ... | ... | ... |
| E04 | ... | ... | ... |
| E05 | ... | ... | ... |
```

---

*Baseado na auditoria de Arthur Alves do Nascimento (student_id=3006, Biotecnologia Tier 1) documentada em `E05_LINHA_DO_TEMPO_ARTHUR_BIOTEC_revisado.md`.*
