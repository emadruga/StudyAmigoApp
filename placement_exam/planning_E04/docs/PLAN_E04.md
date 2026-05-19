# E04 — Plano de Exercício

**Exercício**: E04 — Ampliando fontes de vocabulário
**Período**: 20/05/2026 – 14/06/2026 (25 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Elaborado em**: Maio 2026

Este documento consolida as decisões pedagógicas e operacionais de E04, partindo dos resultados de E01–E03.

---

## Sumário

1. [Ponto de partida: o que E03 nos disse](#1-ponto-de-partida-o-que-e03-nos-disse)
2. [Decisões centrais de E04](#2-decisões-centrais-de-e04)
3. [Estrutura de E04](#3-estrutura-de-e04)
4. [Textos por tier (Component B)](#4-textos-por-tier-component-b)
5. [Component C — Letras de Músicas e Transcrição de Vídeos](#5-component-c--letras-de-músicas-e-transcrição-de-vídeos)
6. [Checkpoints](#6-checkpoints)
7. [Metas e formato de cartões por tier](#7-metas-e-formato-de-cartões-por-tier)
8. [Critérios de avaliação](#8-critérios-de-avaliação)
9. [Avaliação programática de aderência ao método](#9-avaliação-programática-de-aderência-ao-método)
10. [Nomes de baralhos](#10-nomes-de-baralhos)
11. [Reproduzindo os resultados](#11-reproduzindo-os-resultados)

---

## 1. Ponto de partida: o que E03 nos disse

### Dados acumulados (E01 → E02 → E03)

| Métrica | E01 | E02 | E03 |
|---------|----:|----:|----:|
| Alunos no roster | 54 | 64 | 64 |
| Ativos | 44 | 44 | — |
| Taxa de participação | 81% | 69% | — |
| Revisões médias | 154 | 54 | — |
| Nota média (ativos) | — | 62.1 | 61.9 |
| Maturidade média | ~0% | 5.1% | — |
| Menções B ou acima | 3 | 4 | 5 |

> **Nota**: Preencher dados definitivos de E03 após snapshot final (18/05/2026).

### O que funcionou em E03

- Checkpoints intermediários (CP1–CP3) ajudaram a distribuir a criação de cartões ao longo do período
- Score médio de aderência ao método: **89.0%** (assess_card_quality.py)
- Penalidade RET100_CAP identificou corretamente 3 alunos com comportamento de resposta automática
- Segundo uso do mesmo texto T3 (AlphaFold) produziu cartões de vocabulário complementar

### O que não funcionou

- Distribuição de menções ainda concentrada em D/F (D=13, F=18)
- Consistência continua como gargalo: muitos alunos estudam em rajadas curtas
- Component C sem rastreabilidade de fonte — impossível verificar programaticamente a origem dos cartões
- Alunos inativos permanecem sem engajamento (20+ com nota 0)

### Lições para E04

1. **Component C precisa de rastreabilidade**: associar cada cartão/baralho a uma fonte verificável
2. **Material autêntico diversificado**: letras de músicas e transcrições de vídeos aumentam motivação intrínseca
3. **Manter checkpoints**: evidência de que distribuem melhor a carga de estudo
4. **Manter penalidade RET100_CAP**: comportamento de resposta automática precisa continuar sendo penalizado

---

## 2. Decisões centrais de E04

| Questão | Decisão |
|---------|---------|
| Estrutura geral | **3 componentes** (A + B + C), mesma arquitetura de E02/E03 |
| Textos T1 e T2 (Component B) | **Versão 2 — Os Jogadores** (última versão não utilizada de `TIER_{1,2}_TEXT_SOCCER_3_VERSIONS.md`) |
| Texto T3 (Component B) | **Mesmo texto de E02/E03** (AlphaFold, 490 palavras) — 3ª passagem, sob demanda |
| Component C | **Letras de Músicas e/ou Transcrição de Vídeos** — material autêntico com fonte rastreável |
| Rastreabilidade do Component C | **Opção 2 — Cartão-metadado** (ver seção 5) |
| Duração | **26 dias** com checkpoints intermediários |
| Metas de cartões Component B | Iguais a E02/E03 — T1: 5–10, T2: 8–15, T3: 10–18 |
| Metas de cartões Component C | Mínimo **5 cartões** + 1 cartão-metadado por fonte |
| Avaliação qualitativa | **Sim** — assess_card_quality.py + verificação de fonte |
| Penalidade RET100_CAP | **Mantida** — cap em 40 se retenção = 100% e maturidade < 10% |
| Componente A | **Placeholder** — baralho compartilhado a confirmar pelo professor |

---

## 3. Estrutura de E04

| Componente | Descrição | Peso aproximado |
|------------|-----------|----------------|
| **A — Baralho Compartilhado** | Revisão do baralho designado pelo professor | ~30% |
| **B — Texto Nivelado** | Leitura + criação de cartões (texto por tier) | ~35% |
| **C — Material Autêntico** | Cartões a partir de letras de músicas e/ou transcrição de vídeos | ~35% |

> **Mudança em relação a E03**: Component C ganha peso ligeiramente maior (~30% → ~35%) para refletir o foco pedagógico em material autêntico e a exigência de rastreabilidade de fonte. Component B ajustado proporcionalmente.

---

## 4. Textos por tier (Component B)

> As 3 versões de texto por tier foram criadas em E02 (`TIER_{1,2}_TEXT_SOCCER_3_VERSIONS.md`). E02 usou a Versão 1 (História e Conquistas), E03 usou a Versão 3 (Estilo/Copa 2026). E04 usa a **Versão 2 — Os Jogadores**, a última versão disponível.

### Tier 1 — Foundation

**Texto**: *"The Stars of Brazil"* — Versão 2 do `TIER_1_TEXT_SOCCER_3_VERSIONS.md`
**Tamanho**: 174 palavras
**Foco lexical**: jogadores atuais (Vini Jr., Rodrygo, Neymar), posições no campo, atributos de jogador
**Lista curada (10 palavras)**:

| # | Palavra | Tradução |
|---|---------|----------|
| 1 | winger | ponta / extremo |
| 2 | scored | marcou (gol) |
| 3 | forward | atacante |
| 4 | calm | calmo / tranquilo |
| 5 | captain | capitão |
| 6 | defender | zagueiro / defensor |
| 7 | goalkeeper | goleiro |
| 8 | pitch | campo de futebol |
| 9 | award | prêmio |
| 10 | pride | orgulho |

**Formato de cartão**: cloze simples — frente com `[MAIÚSCULO]`, verso com `palavra = tradução`
**Andaime**: Nível 1 (substituição de 1 palavra de contexto)

---

### Tier 2 — Developing

**Texto**: *"The Stars of A Seleção"* — Versão 2 do `TIER_2_TEXT_SOCCER_3_VERSIONS.md`
**Tamanho**: ~300 palavras
**Foco lexical**: atributos de jogador (composure, explosive pace), colocações (serves as, plays alongside), vocabulário abstrato (excellence, passion, generation)
**Lista de referência (20 palavras)**:

| # | Palavra / Colocação | Tradução |
|---|---------------------|----------|
| 1 | exceptional | excepcional |
| 2 | generation | geração |
| 3 | winger | ponta / extremo |
| 4 | explosive pace | velocidade explosiva |
| 5 | dribbling | drible / habilidade de driblar |
| 6 | honor | honraria / premiação |
| 7 | composure | compostura / calma sob pressão |
| 8 | crucial | crucial / decisivo |
| 9 | versatile | versátil |
| 10 | leading scorer | artilheiro / maior goleador |
| 11 | despite | apesar de |
| 12 | remains | permanece / continua sendo |
| 13 | recognizable | reconhecível |
| 14 | serves as | exerce a função de / atua como |
| 15 | captain | capitão |
| 16 | pitch | campo de futebol |
| 17 | position | posição |
| 18 | passion | paixão |
| 19 | excellence | excelência |
| 20 | alongside | ao lado de |

**Formato de cartão**: cloze contextual — frente com `[MAIÚSCULO]`, verso com classe gramatical + `☞ colocação` + tradução da frase
**Andaime**: Tradução Reversa (escreve em PT → Google Translate → edita 1 elemento)

---

### Tier 3 — Expanding (sob demanda)

**Texto**: *"From Chess Prodigy to Nobel Laureate: The Mind Behind AlphaFold"* — **mesmo texto de E02/E03**
**Tamanho**: 490 palavras
**Justificativa**: 3ª passagem — o texto tem vocabulário editorial denso o suficiente. Nenhum aluno sinalizou demanda por Tier 3 até o momento; este tier fica disponível caso algum aluno se apresente.
**Seleção de palavras**: autônoma — o aluno aplica auditoria produtiva com critério mais fino que nas passagens anteriores (colocações, registro formal, nuances de significado)
**Formato de cartão**: definição em inglês — verso com `palavra (classe) = definição EN` + `☞ colocações` + tradução da frase

---

## 5. Component C — Letras de Músicas e Transcrição de Vídeos

### Conceito

Em E04, o Component C evolui de "livre escolha" para **material autêntico direcionado**: o aluno cria cartões de vocabulário a partir de **letras de músicas em inglês** e/ou **transcrições de vídeos educacionais do YouTube**.

### Por que letras de músicas e transcrições de vídeos?

1. **Motivação intrínseca**: alunos escolhem conteúdo de seu interesse real
2. **Exposição a linguagem autêntica**: vocabulário em contexto natural, diferente de textos didáticos
3. **Repetição natural**: músicas são ouvidas várias vezes, reforçando vocabulário
4. **Acessibilidade**: YouTube e plataformas de letras (AZLyrics, Genius, Vagalume) são gratuitos
5. **Variedade de registros**: linguagem informal (músicas), acadêmica/técnica (vídeos), coloquial

### Fontes aceitas

| Tipo de fonte | Exemplos | Requisitos |
|---------------|----------|------------|
| **Letra de música** | Música em inglês (qualquer gênero) | URL da letra (Genius, AZLyrics, Vagalume, etc.) ou nome da música + artista |
| **Transcrição de vídeo** | Vídeo educacional no YouTube com legendas em inglês | URL do vídeo do YouTube |

### Rastreabilidade: Cartão-metadado (Opção 2)

Conforme análise em `E03_sugestoes_para_E04.md`, a **Opção 2 — Cartão-metadado** é adotada para E04 por ser a de menor impacto no aluno e zero código.

**Regra**: Para cada fonte utilizada, o aluno cria **1 cartão especial** como primeiro cartão do grupo:

- **Frente**: `📺 FONTE` (para vídeos) ou `🎵 FONTE` (para músicas)
- **Verso**: URL completa ou referência da fonte (artista + nome da música)

**Exemplo — Vídeo do YouTube:**
```
Frente: 📺 FONTE
Verso:  https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Exemplo — Letra de música:**
```
Frente: 🎵 FONTE
Verso:  Coldplay — Fix You (https://genius.com/Coldplay-fix-you-lyrics)
```

Os cartões de vocabulário que seguem referem-se àquela fonte até o próximo cartão-metadado.

### Formato dos cartões de vocabulário (Component C)

O formato segue o tier do aluno, adaptado ao material autêntico:

| Tier | Formato do cartão Component C |
|------|-------------------------------|
| **Tier 1** | Frente: frase da música/vídeo com `[MAIÚSCULO]`; Verso: `palavra = tradução` |
| **Tier 2** | Frente: frase com `[MAIÚSCULO]`; Verso: `(classe) = tradução ☞ colocação` + tradução da frase |
| **Tier 3** | Frente: frase com `[MAIÚSCULO]`; Verso: `(classe) = definição EN ☞ colocações` + tradução da frase |

### Metas do Component C

| Tier | Mínimo de cartões de vocabulário | Mínimo de fontes |
|------|--------------------------------:|----------------:|
| Tier 1 | 5 | 1 |
| Tier 2 | 7 | 1 |
| Tier 3 | 8 | 2 |

> Tier 3 exige 2 fontes diferentes para incentivar diversificação de registros (ex.: 1 música + 1 vídeo).

### Verificação programática de fonte

O script de avaliação buscará cartões cuja frente contenha `FONTE` (case-insensitive) no baralho Component C. A partir deles:

1. Extrai URL ou referência do verso
2. Valida formato (URL válida ou padrão `Artista — Título`)
3. Conta cartões de vocabulário associados a cada fonte
4. Gera flags:
   - `SEM_FONTE`: nenhum cartão-metadado encontrado
   - `FONTE_INVALIDA`: verso do cartão-metadado não contém URL nem referência reconhecível
   - `POUCOS_CARTOES`: menos de 5 cartões de vocabulário para uma fonte

---

## 6. Checkpoints

| Checkpoint | Data | Atividade esperada |
|------------|------|--------------------|
| **CP1** | 26/05 | Component B: 1ª leitura + 2–3 cartões criados; Component C: fonte escolhida + cartão-metadado criado |
| **CP2** | 02/06 | Component B: meta mínima de cartões; Component C: ≥ 3 cartões de vocabulário + revisão diária |
| **CP3** | 09/06 | Todos os cartões criados + revisão diária consistente |
| **Entrega** | 14/06 23:59 | Concluído |

---

## 7. Metas e formato de cartões por tier

### Component B

| Tier | Baralho | Mínimo | Alvo | Máximo | Formato do verso |
|------|---------|-------:|-----:|-------:|-----------------|
| Tier 1 | `PASSAGE_E04_TIER1` | 5 | 7–8 | 10 | `palavra = tradução` |
| Tier 2 | `PASSAGE_E04_TIER2` | 8 | 10–12 | 15 | `(classe) = tradução ☞ colocação + trad. frase` |
| Tier 3 | `PASSAGE_E04_TIER3` | 10 | 13–15 | 18 | `(classe) = definição EN ☞ colocação + trad. frase` |

### Component C

| Tier | Baralho | Mínimo de cartões vocabulário | Mínimo de fontes | Formato do verso |
|------|---------|------------------------------:|------------------:|-----------------|
| Tier 1 | `AUTHENTIC_E04` | 5 | 1 | `palavra = tradução` |
| Tier 2 | `AUTHENTIC_E04` | 7 | 1 | `(classe) = tradução ☞ colocação + trad. frase` |
| Tier 3 | `AUTHENTIC_E04` | 8 | 2 | `(classe) = definição EN ☞ colocação + trad. frase` |

---

## 8. Critérios de avaliação

Fórmula mantida de E02/E03:

```
Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E
```

| Componente | Variáveis |
|------------|-----------|
| **V — Volume** | revisões totais / cards criados |
| **C — Consistência** | dias de estudo / distribuição temporal |
| **Q — Qualidade** | retenção (70%) + maturidade (30%) |
| **E — Engajamento** | tempo de resposta + distribuição dos botões Again/Hard/Good/Easy |

### Penalidades

| Penalidade | Condição | Efeito |
|------------|----------|--------|
| **RET100_CAP** | Retenção = 100% (≥ 30 revisões) + maturidade < 10% | Nota final limitada a 40 |
| **SEM_FONTE** | Component C sem cartão-metadado de fonte | Desconto de 10 pontos na nota do Component C |

> **Maturidade** (ivl ≥ 21d): com 26 dias de E04, alunos que criarem cartões na primeira semana e revisarem consistentemente poderão ter cartões maduros ao final.

---

## 9. Avaliação programática de aderência ao método

### Scripts

| Script | Função |
|--------|--------|
| `grade_exercise_v2.py` | Cálculo da nota final (V + C + Q + E) |
| `assess_card_quality.py` | Aderência ao formato por tier (score 0–6 por cartão) |
| `assess_source_tracking.py` *(novo)* | Verificação de cartões-metadado e rastreabilidade de fontes no Component C |

### assess_source_tracking.py (novo para E04)

Heurísticas:

1. Busca cartões com `FONTE` na frente dentro do baralho `AUTHENTIC_E04`
2. Extrai URL/referência do verso
3. Conta cartões de vocabulário entre um cartão-metadado e o próximo (ou fim do baralho)
4. Gera flags: `SEM_FONTE`, `FONTE_INVALIDA`, `POUCOS_CARTOES`

**Outputs:**

| Arquivo | Conteúdo |
|---------|----------|
| `E04_source_tracking_detail.csv` | Uma linha por fonte: `student_id, name, tier, source_type, source_ref, vocab_card_count, flag` |
| `E04_source_tracking_summary.csv` | Uma linha por aluno: `total_sources, total_vocab_cards, flags` |

### Heurísticas de qualidade de cartão (assess_card_quality.py)

Mantidas de E03, com extensão para o baralho `AUTHENTIC_E04`:

| Critério | Pontuação | Lógica |
|----------|-----------|--------|
| **Formato da frente** | 0–2 | 2: frase ≥ 4 palavras + `[MAIÚSCULO]` · 1: frase sem marcação · 0: palavra isolada |
| **Formato do verso** | 0–2 | Regras por tier (idênticas a E03) |
| **Evidência de processo** | 0–2 | 2: similaridade < 0.60 com texto-fonte · 1: 0.60–0.85 · 0: ≥ 0.85 (cópia) |

> **Nota sobre Component C**: a evidência de processo para cartões do Component C compara o cartão com a letra/transcrição-fonte (se disponível via URL). Se a fonte não for acessível programaticamente, o critério de evidência de processo é pontuado como 1 (benefício da dúvida).

---

## 10. Nomes de baralhos

| Tier | Component B | Component C |
|------|-------------|-------------|
| Tier 1 | `PASSAGE_E04_TIER1` | `AUTHENTIC_E04` |
| Tier 2 | `PASSAGE_E04_TIER2` | `AUTHENTIC_E04` |
| Tier 3 | `PASSAGE_E04_TIER3` | `AUTHENTIC_E04` |

> **Mudança em relação a E03**: Component C agora tem nome de baralho padronizado (`AUTHENTIC_E04`) para facilitar a separação programática e verificação de fontes. O script `grade_exercise_v2.py` usará `PASSAGE_E04_TIER*` para Component B e `AUTHENTIC_E04` para Component C.

---

## 11. Reproduzindo os resultados

Comando esperado para calcular as notas de E04 (adaptar datas e snapshot):

```bash
# Notas finais
placement_exam/.venv/bin/python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-05-20 --end 2026-06-14 \
    --label E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/SNAPSHOT_DATE/admin.db \
    --user-db-dir ~/.cache/studyamigo/SNAPSHOT_DATE/user_dbs \
    --output placement_exam/planning_E04/output/E04_final_grades.csv

# Qualidade de cartões
placement_exam/.venv/bin/python \
    placement_exam/planning_E03/scripts/assess_card_quality.py \
    --start 2026-05-20 --end 2026-06-14 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/SNAPSHOT_DATE/admin.db \
    --user-db-dir ~/.cache/studyamigo/SNAPSHOT_DATE/user_dbs \
    --detail-output placement_exam/planning_E04/output/E04_card_quality_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_card_quality_summary.csv

# Rastreabilidade de fontes (novo)
placement_exam/.venv/bin/python \
    placement_exam/planning_E04/scripts/assess_source_tracking.py \
    --start 2026-05-20 --end 2026-06-14 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/SNAPSHOT_DATE/admin.db \
    --user-db-dir ~/.cache/studyamigo/SNAPSHOT_DATE/user_dbs \
    --deck-name AUTHENTIC_E04 \
    --detail-output placement_exam/planning_E04/output/E04_source_tracking_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_source_tracking_summary.csv
```

> Substituir `SNAPSHOT_DATE` pela data do snapshot tirado próximo a 14/06/2026.

---

## Progressão E01 → E02 → E03 → E04

| Exercício | Duração | Foco principal | Component B | Component C |
|-----------|---------|----------------|-------------|-------------|
| E01 | 3 semanas | Revisar baralho pronto | — | — |
| E02 | 2 semanas | Criar primeiros cartões | Texto nivelado (futebol/AlphaFold) | Livre escolha (s/ rastreabilidade) |
| E03 | 26 dias | Consolidar + checkpoints | Texto nivelado (futebol v3/AlphaFold 2ª passagem) | Livre escolha (s/ rastreabilidade) |
| E04 | 26 dias | Ampliar fontes + rastreabilidade | Texto nivelado (futebol v2 — Os Jogadores / AlphaFold 3ª passagem) | **Letras de músicas + transcrição de vídeos** (c/ cartão-metadado) |

---

## Decisões pendentes

| Item | Status | Responsável |
|------|--------|-------------|
| Texto T3 (AlphaFold 3ª passagem): confirmar se algum aluno demanda Tier 3 | Pendente | Professor |
| Baralho compartilhado (Component A) | Pendente | Professor |
| Datas exatas do período de E04 | Pendente — usar 20/05–14/06 como placeholder | Professor |
| Implementação do `assess_source_tracking.py` | Pendente | Desenvolvedor |
| Aceitar Opção 2 (cartão-metadado) como padrão definitivo de rastreabilidade | Pendente | Professor |

---

*Elaborado em: Maio 2026*
*Referências: `PLAN_E03.md`, `E03_NOVO_CRITERIO_DE_AVALIACAO_REV_E_CARTOES_E03.md`, `E03_sugestoes_para_E04.md`, `TIER_1_TEXT_SOCCER_3_VERSIONS.md`, `TIER_2_TEXT_SOCCER_3_VERSIONS.md`*
