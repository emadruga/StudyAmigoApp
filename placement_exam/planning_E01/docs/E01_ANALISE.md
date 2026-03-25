# E01 — Análise Técnica: Fórmula de Avaliação

**Exercício**: E01 — Verbal Tenses
**Período**: 01/03/2026 – 23/03/2026
**Turma**: 54 alunos (Biotecnologia, Metrologia, Segurança Cibernética)

Este documento explica em detalhe como cada componente da nota é calculado, com ênfase
nos conceitos que exigem familiaridade com o banco de dados Anki/StudyAmigo. A geração
dos valores numéricos individuais é responsabilidade de `server/tools/grade_exercise.py`.

---

## Fórmula geral

```
Nota = 0.25 × V + 0.25 × C + 0.30 × Q + 0.20 × E
```

onde V, C, Q, E ∈ [0, 100].

---

## Conceitos fundamentais do banco de dados

Antes de detalhar os componentes, é necessário entender dois campos presentes nas tabelas
do banco de dados de cada aluno.

### Campo `type` na tabela `revlog`

Cada linha de `revlog` registra uma revisão e carrega um campo `type` que indica o
contexto em que ela ocorreu:

| `type` | Nome | Significado |
|--------|------|-------------|
| `0` | Learn | Cartão sendo aprendido pela primeira vez |
| `1` | Review | Revisão agendada normalmente pelo SM-2 |
| `2` | Relearn | Re-aprendizado após errar um cartão já maduro |
| `3` | Cram | Revisão manual forçada fora do agendamento |

**Revisão não-cram** = qualquer revisão com `type != 3`, ou seja, tipos 0, 1 e 2.
O modo cram permite ao aluno revisar qualquer cartão a qualquer momento sem que isso
altere o intervalo ou o fator de facilidade do cartão. Por não representar aprendizado
genuíno no contexto do SM-2, revisões cram são excluídas de todos os componentes.

### Campo `ivl` na tabela `cards` — intervalo de agendamento

`ivl` é o **intervalo de agendamento** do cartão, medido em dias. Ele responde à
pergunta: *"daqui a quantos dias o sistema vai apresentar este cartão de novo?"*

Ele não é fixo — cresce a cada revisão bem-sucedida, de acordo com o algoritmo SM-2:

| Situação | O que acontece com `ivl` |
|----------|--------------------------|
| Cartão novo, 1ª revisão | `ivl` = 1 dia |
| Respondido com Good na 2ª revisão | `ivl` ≈ 4 dias |
| Respondido com Good novamente | `ivl` = `ivl_anterior × ease_factor` (ex: × 2.5 → ~10 dias) |
| Respondido com Again (errou) | `ivl` volta para 1 dia |
| Respondido com Easy | `ivl` cresce ainda mais rápido |

Cada acerto consecutivo **multiplica** o intervalo. Um cartão que o aluno acerta
repetidamente vai sendo agendado com intervalos cada vez maiores — 1, 4, 10, 25, 60
dias… — porque o sistema está cada vez mais confiante de que ele domina aquele conteúdo.

**`ivl >= 21`** significa que o cartão sobreviveu a várias rodadas de revisão
bem-sucedidas ao ponto de ser agendado para daqui a 3 semanas ou mais. É o limiar
convencional do Anki para considerar um cartão **"maduro"** — consolidado na memória
de longo prazo.

### Campo `factor` na tabela `cards` — fator de facilidade

`factor` (ou **ease factor**) é um número associado a cada cartão que representa
**o quão bem o aluno domina aquele conteúdo específico**. Ele é o multiplicador que o
SM-2 usa para calcular o próximo intervalo após cada revisão.

No banco de dados, o valor é armazenado multiplicado por 1000 para evitar decimais:

| Valor em `cards.factor` | Ease factor real | Significado |
|-------------------------|------------------|-------------|
| 1300 | 1.3× | Cartão muito difícil para o aluno |
| 2500 | 2.5× | Valor padrão ao criar um cartão (neutro) |
| 3500 | 3.5× | Cartão muito fácil para o aluno |

**Como ele muda a cada revisão:**

| Botão pressionado | Efeito no `factor` |
|-------------------|--------------------|
| Again (errei) | −200 |
| Hard | −150 |
| Good | sem alteração |
| Easy | +150 |

Todo cartão começa em 2500 (neutro). Se o aluno erra muito, o `factor` cai — e o
sistema passa a agendar aquele cartão com intervalos menores, revisando-o com mais
frequência. Se o aluno acerta com facilidade, o `factor` sobe — e o sistema espaça
mais as revisões.

**Exemplo concreto:**
- Cartão com `factor = 2500` e `ivl = 10 dias` → próxima revisão em 10 × 2.5 = 25 dias
- Após dois erros: `factor = 2100` → próxima revisão em 10 × 2.1 = 21 dias
- Após dois acertos fáceis: `factor = 2800` → próxima revisão em 10 × 2.8 = 28 dias

---

## Componente 1 — Volume (V, peso 25%)

Mede a **quantidade bruta de estudo** durante o exercício.

| Variável | Fonte | Descrição |
|----------|-------|-----------|
| `total_reviews` | `revlog` | Revisões não-cram (`type != 3`) na janela do exercício |
| `cards_reviewed` | `revlog` | Cartões únicos revisados (`DISTINCT cid`) |

Normalização por min-max com cap no percentil 95 da turma:

```
reviews_sub = clip((total_reviews - min) / (p95 - min) × 100, 0, 100)
cards_sub   = clip((cards_reviewed - min) / (p95 - min) × 100, 0, 100)
V = 0.40 × cards_sub + 0.60 × reviews_sub
```

> Em E01, o baralho é pré-carregado (os alunos não criam cartões). Por isso o Volume
> colapsa para `V = reviews_sub` via flag `--no-card-creation` do `grade_exercise.py`.

---

## Componente 2 — Consistência (C, peso 25%)

Mede se o aluno **distribuiu o estudo ao longo do período** em vez de concentrar tudo
no final. É composto por dois sub-scores.

### 2.1 Participação (`participation_sub`)

```sql
-- Dias com pelo menos uma revisão não-cram
SELECT COUNT(DISTINCT DATE(id/1000, 'unixepoch'))
FROM revlog
WHERE id BETWEEN :start AND :end AND type != 3;
```

`participation_sub = 100` se houve qualquer revisão não-cram no período, `0` caso
contrário. Este sub-score é binário: distingue apenas quem participou de quem não
participou. A granularidade (quantos dias estudou) é capturada pela coluna **Dias**
no relatório mas não entra diretamente neste sub-score — o que entra é o segundo.

### 2.2 Distribuição anti-cramming (`distribution_sub`)

```sql
-- Revisões no último dia do período (23/03/2026)
SELECT COUNT(*)
FROM revlog
WHERE id BETWEEN :last_day_start AND :end AND type != 3;
```

```
cramming_ratio   = revisões_ultimo_dia / total_revisoes
distribution_sub = (1 - cramming_ratio) × 100
```

Penaliza o aluno proporcionalmente à fração de revisões concentrada no último dia.
Um aluno que fez 80% das revisões no dia 23/03 recebe `distribution_sub ≈ 20`.
Um aluno que distribuiu uniformemente recebe `distribution_sub ≈ 100`.

### Combinação

```
C = 0.50 × participation_sub + 0.50 × distribution_sub
```

> Em E01, a Consistência foi C = 100 para todos os alunos ativos, pois nenhum realizou
> todas as revisões exclusivamente no último dia do período.

---

## Componente 3 — Qualidade (Q, peso 30%)

Mede **quanto o aluno realmente aprendeu**, via dois sub-scores.

### 3.1 Retenção (`retention_sub`)

**O que mede:** Das vezes que o aluno foi testado em cartões que já conhecia, quantas
vezes ele acertou?

```sql
SELECT COUNT(*) AS total,
       SUM(CASE WHEN ease >= 3 THEN 1 ELSE 0 END) AS ok
FROM revlog
WHERE id BETWEEN :start AND :end AND type IN (1, 2);
```

```
retention_sub = (ok / total) × 100
```

A query olha apenas revisões `type IN (1, 2)` — revisões agendadas e re-aprendizado.
São excluídos:
- `type = 0` (aprendizado inicial): errar um cartão novo não é "esquecer", o aluno
  ainda está vendo aquele conteúdo pela primeira vez.
- `type = 3` (cram): não representa aprendizado genuíno no SM-2.

Um acerto é contado quando o aluno respondeu com **Good ou Easy** (`ease >= 3`).
Respostas Again e Hard (`ease < 3`) contam como erro.

**Exemplo:** 100 revisões agendadas no período, 75 respondidas com Good ou Easy →
`retention_sub = 75`.

### 3.2 Maturidade (`maturity_sub`)

**O que mede:** Dos cartões que o aluno revisou, quantos já estão fixados na memória
de longo prazo?

```sql
SELECT COUNT(DISTINCT c.id) AS total,
       SUM(CASE WHEN c.ivl >= 21 THEN 1 ELSE 0 END) AS mature
FROM cards c
WHERE c.id IN (
    SELECT DISTINCT cid FROM revlog
    WHERE id BETWEEN :start AND :end
);
```

```
maturity_sub = (mature / total) × 100
```

A query **não olha o histórico de revisões** — ela olha o estado atual do cartão na
tabela `cards`. O `ivl` que aparece ali é o intervalo calculado após a última revisão
do aluno naquele cartão. Um cartão com `ivl >= 21` só existe se o aluno o acertou
repetidamente ao longo de semanas, o que é uma evidência muito mais forte de
aprendizado real do que simplesmente acertar na semana corrente.

**Por que a maturidade foi quase zero em E01?**
O exercício durou apenas 23 dias. Um cartão que começa do zero precisaria de muitas
revisões bem-sucedidas e rápidas para atingir `ivl >= 21` nesse tempo. Além disso, o
bug de crescimento linear de intervalos (em vez de exponencial) estava presente na
maior parte do período, dificultando ainda mais a maturação. Apenas 3 alunos atingiram
algum nível de maturidade: Laryssa (25%), Marcelo Ygor (3.7%), Laís (1.9%).

**Diferença conceitual entre retenção e maturidade:**
- **Retenção** = o aluno está acertando *agora*, neste período.
- **Maturidade** = o conhecimento sobreviveu tempo suficiente para ser considerado
  consolidado.

Um aluno pode ter retenção alta simplesmente por estar revisando cartões novos todo
dia (fácil acertar na fase inicial). Cartões maduros, por outro lado, só existem se o
aluno acertou aquele conteúdo repetidamente ao longo de semanas.

### Combinação

```
Q = 0.70 × retention_sub + 0.30 × maturity_sub
```

A retenção tem peso maior (70%) porque responde à pergunta mais imediata. A maturidade
(30%) responde à pergunta mais profunda sobre consolidação de longo prazo. Em E01, como
a maturidade foi quase zero para todos, o componente Q ficou essencialmente limitado a
`0.70 × retention_sub` — com teto prático em torno de 70 pontos para quem acertou tudo.

---

## Componente 4 — Engajamento (E, peso 20%)

Mede a **atenção genuína** durante as revisões por dois sub-scores.

### 4.1 Qualidade do tempo (`time_sub`)

```sql
SELECT COUNT(*) FILTER (WHERE time < 60000) AS total,
       COUNT(*) FILTER (WHERE time >= 2000 AND time < 60000) AS engaged
FROM revlog
WHERE id BETWEEN :start AND :end AND type != 3;
```

```
time_sub = (engaged / total) × 100
```

O campo `time` em `revlog` registra em milissegundos quanto tempo o aluno levou entre
ver o cartão e clicar em um botão de resposta.

- **< 2000 ms (< 2 s):** tempo insuficiente para ler e analisar o cartão — não conta
  como revisão engajada.
- **>= 60000 ms (>= 60 s):** o aluno provavelmente saiu da tela ou ficou ocioso — a
  revisão é excluída do denominador para não penalizar pausas naturais.
- **2000–60000 ms:** janela considerada válida para engajamento real.

### 4.2 Saúde do fator de facilidade (`ease_sub`)

Calcula a **média do `cards.factor`** de todos os cartões que o aluno revisou no período
e normaliza no intervalo teórico [1300, 3500]:

```
ease_sub = clip((mean_factor - 1300) / (3500 - 1300) × 100, 0, 100)
```

| `mean_factor` médio | `ease_sub` |
|---------------------|------------|
| 1300 (mínimo possível) | 0 |
| 2500 (valor padrão neutro) | ~54.5 |
| 3500 (máximo possível) | 100 |

**O que `ease_sub` realmente indica:**

Um `factor` médio baixo significa que o aluno pressionou **Again** e **Hard** com
frequência — os cartões estão difíceis e o sistema reduziu os multiplicadores.

Um `factor` médio alto significa que o aluno pressionou **Easy** com frequência — o
que pode indicar duas coisas opostas:
- **Positivo:** o aluno realmente domina o conteúdo.
- **Suspeito:** o aluno está pressionando Easy mecanicamente sem ler os cartões.

Por isso o sub-score se chama **"saúde"** do fator: um factor saudável é aquele que
reflete o esforço real do aluno, nem artificialmente baixo (muitos erros) nem
artificialmente alto (botão Easy sem critério). O cruzamento com `time_sub` é o que
distingue os dois casos: alto `ease_sub` com baixo `time_sub` é o padrão típico do
aluno que não está realmente estudando.

### Combinação

```
E = 0.50 × time_sub + 0.50 × ease_sub
```

Os dois sub-scores se complementam:
- `time_sub` detecta quem respondeu rápido demais — provavelmente sem ler.
- `ease_sub` detecta quem marcou Easy em tudo — provavelmente sem critério.

Um aluno que leu cada cartão com atenção e respondeu honestamente tende a ter bom
tempo médio **e** um factor saudável. Quem "jogou no automático" tende a ser
penalizado em pelo menos um dos dois.

---

## Situações de participação

### Alunos que fizeram o placement exam mas não têm atividade no Study Amigo

Os alunos abaixo constam no roster do placement exam mas não geraram nenhuma revisão
não-cram durante o período de E01. **Nota E01 = 0.**

#### Sem conta cadastrada na plataforma

| ID | Nome | Curso |
|----|------|-------|
| 5006 | Ana Beatriz Pontes de Almeida | Segurança Cibernética |
| 5061 | Luiz Henrique Silva de Carvalho | Segurança Cibernética |
| 5091 | Sophia Tavares dos Santos | Segurança Cibernética |

#### Conta cadastrada, mas sem nenhuma revisão no período

| ID | Nome | Curso |
|----|------|-------|
| 3006 | Arthur Alves do Nascimento | Biotecnologia |
| 4031 | Emanuelly Almeida da Silva | Metrologia |
| 4076 | Leandro Moreira Andrade da Silva | Metrologia |
| 4106 | Victor Anderson Reid | Metrologia |
| 5026 | Cauê da Paixão Gomes | Segurança Cibernética |
| 5041 | José Augusto | Segurança Cibernética |
| 5096 | Tainá Avelino. Sebosa da Silva | Segurança Cibernética |

**Total sem atividade: 10 alunos (18.5% da turma).**

---

### Alunos que entregaram revisões mas não fizeram o placement exam

Estes alunos têm atividade registrada no Study Amigo durante o período de E01, mas não
constam no roster do placement exam. Sua situação deve ser verificada manualmente antes
da consolidação das notas.

> A lista definitiva é gerada automaticamente pelo `grade_exercise.py` via cruzamento
> entre os bancos de dados de usuários e o arquivo CSV `--roster`. Consultar a saída
> do script para o relatório final.

---

## Geração dos valores numéricos

As notas individuais (V, C, Q, E e Nota final) de cada aluno são calculadas e
exportadas por `server/tools/grade_exercise.py`. Este documento descreve apenas a
semântica das métricas. Para reproduzir os resultados de E01:

```bash
python grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260323/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260323/user_dbs
```

---

*Última atualização: 24/03/2026*
