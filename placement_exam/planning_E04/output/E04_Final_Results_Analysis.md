# E04 — Análise Final de Resultados

**Exercício**: E04 — Ampliando fontes de vocabulário
**Período**: 19/05/2026 – 15/06/2026 (28 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Dados**: snapshot de produção em 15/06/2026 (`~/.cache/studyamigo/20260615`)
**Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E`
**Penalidade**: RET100 + maturidade < 10% → nota máxima = 40 (flag `RET100_CAP`)
**Scripts**: `grade_exercise_v2.py` + `assess_card_quality.py` + `assess_source_tracking.py` + `account_map.csv`

---

## 1. Sumário de participação

| Situação | Alunos |
|----------|-------:|
| **Ativos** (roster + revisões no período) | **44** |
| Sem atividade — sem conta cadastrada | 1 |
| Sem atividade — conta existe, zero revisões | 19 |
| **Total no roster** | **64** |

**Taxa de participação**: 44/64 = **69%** (vs. 39/64 = 61% em E03).

Recuperação significativa de participação: 5 alunos que estavam inativos em E03 retornaram em E04. Destaque para Gabriel Bernardo Do Nascimento (Biotecnologia), que saiu de inativo em E03 para 2º lugar no ranking geral em E04.

### 1.1 Alunos sem conta cadastrada (1)

| ID | Nome | Curso | Tier | Email |
|----|------|-------|------|-------|
| 5091 | Sophia Tavares dos Santos | SegCiber | Tier 2 | sophia2sun1@gmail.com |

> Nota E04 = 0.

### 1.2 Alunos com conta mas sem revisões no período (19)

| ID | Nome | Curso | Tier |
|----|------|-------|------|
| 3011 | Eduardo Cardoso Oliveira | Biotecnologia | Tier 2 |
| 3016 | Elias Soares Dutra da Conceição | Biotecnologia | Tier 1 |
| 3019 | Emanuel Melo dos Santos | Biotecnologia | — |
| 3021 | Fernando Henrique Souza Laia | Biotecnologia | Tier 1 |
| 3031 | Maria Clara Mesquita Pires | Biotecnologia | Tier 1 |
| 3036 | Maria Eduarda De Lima Abreu | Biotecnologia | Tier 1 |
| 3046 | Matheus Dias Gomes | Biotecnologia | Tier 2 |
| 4006 | Ana Julia de Souza Oliveira | Metrologia | Tier 1 |
| 4018 | Edson José Bernardino | Metrologia | — |
| 4021 | Eduardo da Silva Fiuza | Metrologia | Tier 2 |
| 4046 | Jhonatan Brandão da Silva | Metrologia | Tier 1 |
| 4088 | Manuelly Alves Batista | Metrologia | — |
| 4098 | Rogério Gabriel Barros dos Santos Simões | Metrologia | — |
| 4101 | Thiago Kaleb Figueiredo de Oliveira | Metrologia | Tier 1 |
| 5006 | Ana Beatriz Pontes de Almeida | SegCiber | Tier 2 |
| 5026 | Cauê da Paixão Gomes | SegCiber | Tier 1 |
| 5041 | José Augusto Freire | SegCiber | Tier 1 🏁 |
| 5082 | Miguel Monteiro Cunha de Araujo | SegCiber | Tier 1 |
| 5086 | Samea Soares Pacheco | SegCiber | Tier 1 |

> Nota E04 = 0.

---

## 2. Resultados dos alunos ativos

### 2.1 Estatísticas gerais

| Métrica | Valor |
|---------|------:|
| Alunos ativos | 44 |
| Nota média | **66.1** |
| Nota mediana | **66.7** |
| Nota máxima | **86.1** |
| Nota mínima | **30.1** |
| Revisões — média | **163** |
| Revisões — máx | **816** |
| Retenção média | **80.2%** |
| Maturidade média | **20.9%** |
| Alunos com cartões maduros (ivl ≥ 21d) | 26 |
| Alunos penalizados (RET100_CAP) | 2 |

### 2.2 Distribuição de menções

| Menção | Intervalo | Alunos | % ativos |
|--------|-----------|-------:|---------:|
| A | ≥ 90 | 0 | 0% |
| B | 80–89 | 6 | 14% |
| C | 70–79 | 11 | 25% |
| D | 60–69 | 15 | 34% |
| F | < 60 | 12 | 27% |

### 2.3 Resultados por curso

| Curso | Ativos | Nota média | Rev média | Dist. (A/B/C/D/F) |
|-------|-------:|----------:|----------:|-----------------|
| Biotecnologia | 6 | 62.0 | 78 | 0/1/0/1/4 |
| Metrologia | 20 | 65.8 | 156 | 0/4/5/5/6 |
| SegCiber | 18 | 67.9 | 199 | 0/1/6/9/2 |

SegCiber lidera em nota média e volume de revisões, impulsionada pelo retorno de alunos que estavam inativos. Biotecnologia mantém a menor média, mas com metade dos ativos — 6 de um total de 14 alunos no roster — o que reflete ausência estrutural, não desempenho ruim dos presentes (o destaque Gabriel Bernardo é de Biotecnologia).

---

## 3. Ranking completo

| # | Nome | ID | Curso | Tier | Rev | Dias | Cards | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|------|----|-------|------|----:|-----:|------:|-----:|-----:|--:|--:|--:|--:|-----:|---|-------|
| 1 | Keyrrison da Silva Braga | 4060 | Metrologia | — | 370 | 11 | 21 | 92.3 | 60.5 | 81.8 | 99.3 | 82.7 | 79.8 | **86.1** | B | |
| 2 | Gabriel Bernardo Do Nascimento | 3026 | Biotecnologia | Tier 2 | 241 | 4 | 32 | 95.2 | 51.4 | 72.2 | 100.0 | 82.1 | 78.1 | **83.3** | B | |
| 3 | Ricardo de Souza Rodrigues | 4096 | Metrologia | Tier 1 | 462 | 7 | 86 | 83.4 | 13.9 | 100.0 | 92.9 | 62.5 | 79.2 | **82.8** | B | |
| 4 | Madson Ferreira de Souza | 5066 | SegCiber | Tier 1 | 163 | 10 | 11 | 100.0 | 100.0 | 37.6 | 97.5 | 100.0 | 88.4 | **81.5** | B | RET100 |
| 5 | Laryssa Vitória Ramos da Silva | 4061 | Metrologia | Tier 1 | 183 | 21 | 27 | 88.9 | 68.6 | 57.5 | 98.6 | 82.8 | 82.9 | **80.5** | B | |
| 6 | Marcelo Ygor de Sá Cordeiro | 4091 | Metrologia | Tier 1 | 366 | 7 | 21 | 94.8 | 19.4 | 81.2 | 91.0 | 72.2 | 76.7 | **80.0** | B | |
| 7 | Laís Nascimento Silva | 4071 | Metrologia | Tier 1 | 130 | 17 | 19 | 99.1 | 75.4 | 40.5 | 100.0 | 92.0 | 83.8 | **79.5** | C | |
| 8 | Ana Carolina Barbosa da Costa | 4001 | Metrologia | Tier 2 | 201 | 9 | 39 | 89.4 | 33.0 | 72.4 | 100.0 | 72.5 | 71.6 | **79.2** | C | |
| 9 | Marcella Vasconcelos Pacheco da Cruz | 5071 | SegCiber | Tier 1 | 197 | 3 | 9 | 96.8 | 70.4 | 41.1 | 100.0 | 88.9 | 85.1 | **79.0** | C | |
| 10 | João Ricardo Rocha de Carvalho | 5046 | SegCiber | Tier 1 🏁 | 816 | 18 | 23 | 69.2 | 27.3 | 83.9 | 100.0 | 56.7 | 72.6 | **77.5** | C | |
| 11 | Philipe Emanuel de Souza Meireles | 5083 | SegCiber | — | 249 | 8 | 22 | 84.1 | 27.7 | 63.1 | 100.0 | 67.2 | 79.9 | **76.9** | C | |
| 12 | Emanuelly Almeida da Silva | 4031 | Metrologia | Tier 1 | 366 | 8 | 21 | 88.2 | 0.0 | 81.2 | 88.4 | 61.7 | 77.6 | **76.4** | C | |
| 13 | Bernardo Da Silva Lucas | 5016 | SegCiber | Tier 2 | 265 | 5 | 16 | 85.4 | 15.4 | 59.5 | 98.3 | 64.4 | 79.9 | **74.7** | C | |
| 14 | Mateus Ferreira Patrício | 5081 | SegCiber | Tier 2 | 130 | 10 | 6 | 93.5 | 92.3 | 27.0 | 100.0 | 93.2 | 74.5 | **74.6** | C | |
| 15 | Isabella Queres | 4041 | Metrologia | Tier 2 | 127 | 3 | 10 | 99.1 | 48.3 | 30.7 | 100.0 | 83.9 | 80.6 | **73.9** | C | |
| 16 | Ezequiel Telles Pedrosa dos Santos | 5031 | SegCiber | Tier 1 | 278 | 14 | 36 | 59.9 | 66.1 | 82.4 | 100.0 | 61.7 | 42.5 | **72.6** | C | LOW_TIME |
| 17 | Leandro Moreira Andrade da Silva | 4076 | Metrologia | Tier 1 | 226 | 9 | 10 | 86.2 | 14.3 | 46.9 | 100.0 | 64.6 | 79.1 | **71.9** | C | |
| 18 | Arthur do Nascimento Paiva | 5011 | SegCiber | Tier 2 | 157 | 8 | 21 | 81.6 | 2.8 | 47.0 | 100.0 | 58.0 | 77.8 | **69.7** | D | |
| 19 | Jady Maria Rodrigues Figueiredo | 5036 | SegCiber | Tier 1 | 112 | 4 | 15 | 84.5 | 20.9 | 33.4 | 100.0 | 65.4 | 79.6 | **68.9** | D | |
| 20 | Ana Manuela de Carvalho Trindade | 3001 | Biotecnologia | Tier 2 | 139 | 3 | 0 | 95.1 | 17.3 | 22.3 | 100.0 | 71.8 | 80.3 | **68.2** | D | |
| 21 | Eloá de Oliveira Amorim | 4026 | Metrologia | Tier 1 | 27 | 1 | 24 | 100.0 | 0.0 | 28.8 | 100.0 | 70.0 | 71.7 | **67.6** | D | |
| 22 | Laura Martins da Silva | 4066 | Metrologia | Tier 1 🏁 | 188 | 3 | 15 | 73.0 | 11.0 | 45.9 | 100.0 | 54.4 | 69.9 | **66.7** | D | |
| 23 | Daniel André de Oliveira | 5028 | SegCiber | — | 134 | 4 | 25 | 72.0 | 0.0 | 47.4 | 92.9 | 50.4 | 77.3 | **65.7** | D | |
| 24 | Lenilson Maia Rodrigues de Lima | 5051 | SegCiber | Tier 1 | 43 | 3 | 15 | 93.1 | 0.0 | 65.2 | 65.2 | 65.2 | 77.8 | **65.6** | D | |
| 25 | Julia de Oliveira Corrêa | 4051 | Metrologia | Tier 2 | 73 | 8 | 20 | 81.8 | 0.0 | 32.2 | 100.0 | 57.3 | 76.9 | **65.6** | D | |
| 26 | Adriany Praia Serafim | 5001 | SegCiber | Tier 2 | 192 | 2 | 10 | 98.8 | 22.1 | 41.3 | 59.9 | 75.8 | 82.0 | **64.4** | D | CRAM |
| 27 | Isabel da Silva Peixoto | 4036 | Metrologia | Tier 1 🏁 | 68 | 3 | 31 | 73.0 | 0.0 | 42.8 | 100.0 | 51.1 | 65.8 | **64.2** | D | |
| 28 | Tainá Avelino Barbosa da Silva | 5096 | SegCiber | Tier 2 | 213 | 4 | 40 | 65.0 | 0.0 | 74.4 | 100.0 | 45.5 | 33.7 | **64.0** | D | LOW_TIME |
| 29 | Luiz Henrique Silva de Carvalho | 5061 | SegCiber | Tier 1 🏁 | 260 | 3 | 5 | 90.4 | 0.0 | 47.3 | 100.0 | 63.3 | 39.8 | **63.8** | D | LOW_TIME |
| 30 | Bruno dos Santos Lima | 5021 | SegCiber | Tier 1 | 42 | 4 | 20 | 74.4 | 0.0 | 27.1 | 100.0 | 52.1 | 74.2 | **62.2** | D | |
| 31 | Anthony Lucas Muniz Dos Santos | 5008 | SegCiber | — | 173 | 5 | 10 | 67.7 | 0.8 | 38.2 | 100.0 | 47.7 | 64.4 | **61.7** | D | |
| 32 | Amanda Silva do Nascimento | 4000 | Metrologia | — | 86 | 11 | 9 | 68.5 | 12.0 | 22.9 | 96.5 | 51.5 | 75.0 | **60.3** | D | |
| 33 | Marcio da Silva Bertucio | 5076 | SegCiber | Tier 1 | 114 | 2 | 21 | 78.5 | 12.2 | 40.0 | 100.0 | 58.6 | 34.3 | **59.4** | F | LOW_TIME |
| 34 | Cauã Jorge de Nazareth Marins | 4016 | Metrologia | Tier 1 | 12 | 3 | 17 | 66.7 | 0.0 | 19.1 | 100.0 | 46.7 | 77.3 | **59.2** | F | |
| 35 | Wallace Gabriel Ferreira dos Santos | 3056 | Biotecnologia | Tier 2 | 52 | 2 | 0 | 100.0 | 35.4 | 8.0 | 59.6 | 80.6 | 81.0 | **57.3** | F | RET100 CRAM |
| 36 | Maria Isabel Silva dos Santos | 3041 | Biotecnologia | Tier 1 | 24 | 1 | 0 | 81.0 | 0.0 | 3.4 | 100.0 | 56.7 | 69.1 | **56.7** | F | |
| 37 | Lucas Pandini Pinheiro | 4081 | Metrologia | Tier 2 | 83 | 1 | 3 | 93.7 | 1.2 | 16.2 | 100.0 | 65.9 | 36.9 | **56.2** | F | LOW_TIME |
| 38 | Samuel Martins Da Conceição | 3051 | Biotecnologia | Tier 1 | 10 | 1 | 20 | 70.0 | 0.0 | 21.9 | 100.0 | 49.0 | 51.9 | **55.6** | F | |
| 39 | Arthur Alves do Nascimento | 3006 | Biotecnologia | Tier 1 | 3 | 1 | 0 | 66.7 | 0.0 | 0.0 | 100.0 | 46.7 | 60.6 | **51.1** | F | |
| 40 | Kauã Alves da Silva de França | 4056 | Metrologia | Tier 1 | 22 | 2 | 0 | 47.4 | 0.0 | 3.1 | 100.0 | 33.2 | 77.0 | **51.1** | F | |
| 41 | Victor Anderson Reid | 4106 | Metrologia | Tier 2 | 17 | 1 | 17 | 0.0 | 0.0 | 19.9 | 100.0 | 0.0 | 74.3 | **44.8** | F | |
| 42 | Ana Luiza Camilo da Silva | 4011 | Metrologia | Tier 1 | 112 | 6 | 18 | 100.0 | 0.0 | 36.5 | 100.0 | 70.0 | 77.3 | **40.0** | F | RET100 RET100_CAP |
| 43 | Lucas da Silva Santos | 5056 | SegCiber | Tier 1 | 52 | 4 | 16 | 100.0 | 0.0 | 24.6 | 100.0 | 70.0 | 75.0 | **40.0** | F | RET100 RET100_CAP |
| 44 | Luiz Antonio Inácio Pereira | 4086 | Metrologia | Tier 2 | 4 | 1 | 8 | 0.0 | 0.0 | 8.5 | 50.0 | 0.0 | 77.3 | **30.1** | F | |

---

## 4. Alertas e comportamentos suspeitos

| Aluno | ID | Flag | Detalhe |
|-------|----|------|---------|
| Madson Ferreira de Souza | 5066 | RET100 | 163/163 acertos; maturidade 100% — aprendizado consolidado; não penalizado |
| Ana Luiza Camilo da Silva | 4011 | **RET100_CAP** | 112/112 acertos; maturidade 0% — **nota limitada a 40** (era 80.5) |
| Lucas da Silva Santos | 5056 | **RET100_CAP** | 52/52 acertos; maturidade 0% — **nota limitada a 40** (era 70.0) |
| Wallace Gabriel Ferreira dos Santos | 3056 | RET100 + CRAM | 52/52 acertos; maturidade 35.4% (acima de 10%); revisões em 2 dias |
| Adriany Praia Serafim | 5001 | CRAM | 192 revisões em 2 dias (100% cramming ratio) |
| Ezequiel Telles Pedrosa dos Santos | 5031 | LOW_TIME | 278 revisões; tempo engajado abaixo do limiar — respostas muito rápidas |
| Tainá Avelino Barbosa da Silva | 5096 | LOW_TIME | 213 revisões em 4 dias; tempo engajado insuficiente |
| Luiz Henrique Silva de Carvalho | 5061 | LOW_TIME | 260 revisões em 3 dias; tempo engajado insuficiente |
| Marcio da Silva Bertucio | 5076 | LOW_TIME | 114 revisões; tempo de resposta médio muito baixo |
| Lucas Pandini Pinheiro | 4081 | LOW_TIME | 83 revisões em 1 dia; tempo engajado insuficiente |

### Penalidade RET100_CAP

Alunos com **100% de retenção** (zero erros em ≥ 30 revisões) **e maturidade < 10%** recebem nota máxima de **40 pontos**. Em E04, apenas 2 alunos foram penalizados (vs. 3 em E03):

**Não penalizados** (RET100 com maturidade ≥ 10%): Madson Ferreira de Souza (maturidade 100%) e Wallace Gabriel Ferreira dos Santos (maturidade 35.4%).

**CRAM (2 alunos)**: Adriany (192 revisões em 2 dias) e Wallace (52 revisões em 2 dias) concentraram toda a atividade em sessões únicas, sem espaçamento.

---

## 5. Criação de cartões

| Métrica | Valor |
|---------|------:|
| Alunos que criaram cartões | 39/44 (89%) |
| Média de cartões criados (entre criadores) | 20.2 |
| Máximo | 86 (Ricardo de Souza Rodrigues) |
| Mínimo (entre criadores) | 3 |

Os 5 alunos sem criação de cartões: Ana Manuela de Carvalho Trindade, Wallace Gabriel Ferreira dos Santos, Maria Isabel Silva dos Santos, Arthur Alves do Nascimento, Kauã Alves da Silva de França. Destes, Wallace e Maria Isabel também estudaram apenas 1–2 dias, sugerindo revisão do baralho compartilhado sem criação de novos cartões.

**Caso Ricardo de Souza Rodrigues [4096]**: 86 cartões criados em 7 dias de estudo — máximo histórico de criação na turma. A alta produção refletiu-se em nota B (82.8), sustentada pelo volume (V=100.0).

---

## 6. Maturidade — consolidação do SM-2

Em E04, **26 alunos** apresentam cartões maduros (ivl ≥ 21d), um salto expressivo em relação a E03 (6 alunos). A maturidade média subiu de 10.7% (E03) para **20.9%** (E04), reflexo acumulado de quatro exercícios consecutivos de revisão espaçada.

| Aluno | ID | Mat% E03 | Mat% E04 | Δ |
|-------|----|----------:|---------:|--|
| Madson Ferreira de Souza | 5066 | 100.0% | **100.0%** | = |
| Mateus Ferreira Patrício | 5081 | 65.6% | **92.3%** | ↑ |
| Laís Nascimento Silva | 4071 | 87.2% | **75.4%** | ↓ |
| Marcella Vasconcelos Pacheco da Cruz | 5071 | — | **70.4%** | ↑ (nova) |
| Laryssa Vitória Ramos da Silva | 4061 | 92.1% | **68.6%** | ↓ |
| Ezequiel Telles Pedrosa dos Santos | 5031 | 0.0% | **66.1%** | ↑ |
| Keyrrison da Silva Braga | 4060 | 0.0% | **60.5%** | ↑ |
| Gabriel Bernardo Do Nascimento | 3026 | — | **51.4%** | ↑ (retornou) |
| Isabella Queres | 4041 | 0.0% | **48.3%** | ↑ |
| Ana Carolina Barbosa da Costa | 4001 | 20.5% | **33.0%** | ↑ |

A queda de Laryssa (92.1% → 68.6%) e Laís (87.2% → 75.4%) provavelmente reflete criação de novos cartões imaturos no período, diluindo a proporção de maduros. Ezequiel e Keyrrison mostram o maior crescimento absoluto — de 0% para acima de 60%.

---

## 7. Distribuição de dias de estudo

| Dias ativos | Alunos |
|------------:|-------:|
| 1 | 7 |
| 2 | 4 |
| 3 | 8 |
| 4 | 6 |
| 5 | 2 |
| 6 | 1 |
| 7 | 2 |
| 8 | 4 |
| 9 | 2 |
| 10 | 2 |
| 11 | 2 |
| 14 | 1 |
| 17 | 1 |
| 18 | 1 |
| 21 | 1 |

**25% dos alunos ativos (11/44) estudaram apenas 1 ou 2 dias** — queda em relação a E03 (49%). A distribuição de dias de estudo melhorou substancialmente: em E03, nenhum aluno ultrapassou 22 dias; em E04, 7 alunos estudaram 11 dias ou mais. Laryssa destaca-se com **21 dias de estudo** (75% do período).

---

## 8. Component C — Rastreabilidade de fontes (novo em E04)

Em E04, o Component C exigiu cartões criados a partir de letras de músicas e/ou transcrições de vídeos, com um **cartão-metadado** (`📺 FONTE` / `🎵 FONTE`) rastreando a fonte de cada grupo de cartões.

### 8.1 Sumário de adesão

| Métrica | Valor |
|---------|------:|
| Alunos com baralho `AUTHENTIC_E04` | 20 |
| Alunos com ≥ 1 fonte rastreável | 17 |
| Total de fontes encontradas | 41 |
| Fontes válidas (URL ou padrão Artista — Título) | 41 (100%) |
| Total de cartões de vocabulário | 203 |
| Score médio de aderência ao formato (assess_card_quality.py) | **94.6%** |

### 8.2 Flags de rastreabilidade

| Flag | Alunos | Significado |
|------|-------:|-------------|
| `SEM_FONTE` | 3 | Cartões criados sem cartão-metadado (Ana Luiza, Marcella, Marcio) |
| `POUCOS_CARTOES` | 7 | Menos cartões de vocabulário que o mínimo por fonte |
| `POUCAS_FONTES` | 3 | Abaixo do mínimo de fontes para o tier (Ana Luiza, Marcella, Marcio) |
| `FONTE_INVALIDA` | 0 | Nenhuma referência com formato inválido |

### 8.3 Destaques do Component C

- **Ezequiel Telles [5031]**: 4 fontes (Coldplay, Maroon 5, Michael Jackson ×2) com 5 cartões cada — aderência exemplar ao mínimo de cartões por fonte.
- **Ana Carolina Barbosa da Costa [4001]**: 12 fontes diferentes (The Beatles, Bon Jovi, Michael Jackson, Harry Styles, etc.) com 1 cartão por fonte — máximo de diversidade, mas `POUCOS_CARTOES` em todas as fontes.
- **Emanuelly Almeida da Silva [4031]**: 10 cartões a partir de uma única fonte (Goodness of God) — concentração efetiva em vez de dispersão.

---

## 9. Qualidade de cartões (Component B)

| Métrica | E04 | E03 |
|---------|----:|----:|
| Alunos com baralho `PASSAGE_E04` | 18 | — |
| Total de cartões avaliados | 224 | — |
| Score médio de aderência | **94.6%** | **89.0%** |
| Cartões de baixa qualidade (< 33%) | 0 | — |
| Flag COPIA | 0 | — |

Melhora de 5.6 pontos percentuais no score de aderência ao método — nenhum cartão copiado e nenhum de baixa qualidade. Nota: 36 alunos ativos não possuem baralho `PASSAGE_E04`, indicando que estudaram apenas o baralho compartilhado (Component A) sem criar cartões no Component B.

---

## 10. Comparação E01 → E02 → E03 → E04

| Métrica | E01 | E02 | E03 | E04 |
|---------|----:|----:|----:|----:|
| Alunos no roster | 54 | 64 | 64 | 64 |
| Ativos (com revisões) | 44 | 44 | 39 | **44** |
| Taxa de participação | 81% | 69% | 61% | **69%** |
| Revisões médias | 154 | 54 | 72 | **163** |
| Retenção média | — | 89.8% | 88.8% | 80.2% |
| Maturidade média | ~0% | 5.1% | 10.7% | **20.9%** |
| Menções B ou acima | 3 | 4 | 5 | **6** |
| Menções A | 0 | 0 | 3 | 0 |
| Nota média (ativos) | — | 62.1 | 61.9 | **66.1** |
| Alunos penalizados (RET100_CAP) | — | — | 3 | **2** |
| Score aderência ao método | — | — | 89.0% | **94.6%** |

**Tendências em E04**:

- **Participação recuperada**: volta aos 69% de E02, após queda para 61% em E03. O Component C com material autêntico (músicas, vídeos) pode ter contribuído para re-engajar alunos inativos.
- **Revisões disparam**: média de 163 por aluno — o dobro de E03 (72) e três vezes mais que E02 (54). Reflexo do acúmulo de cartões de exercícios anteriores somado aos novos.
- **Maturidade dobra**: 10.7% → 20.9%. O crescimento é contínuo e diretamente ligado à consistência acumulada dos melhores alunos.
- **Retenção cai**: 88.8% → 80.2%. Queda esperada com o aumento de cartões novos (imaturos) — a fração de revisões de cartões jovens cresce com a coleção maior, pressionando a retenção global para baixo.
- **Nota média sobe**: 61.9 → 66.1 (+4.2 pontos) — a maior melhora até agora entre exercícios consecutivos.
- **Menções A desaparecem**: em E03 houve 3 menções A (Laryssa 93.3, Madson 92.8, Laís 90.6). Em E04 nenhum aluno ultrapassou 90. Provavelmente reflexo do aumento de cartões novos (maturidade e retenção global menores), que comprimiu o componente Q.

---

## 11. Mapeamento de contas secundárias aplicado

O mesmo `account_map.csv` de E02–E03 foi utilizado (15 mapeamentos). Não houve novos casos de contas duplicadas identificados em E04.

---

## 12. Reproduzindo os resultados

```bash
# Notas finais
placement_exam/.venv/bin/python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-05-19 --end 2026-06-15 \
    --label E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --output placement_exam/planning_E04/output/E04_final_grades.csv

# Qualidade de cartões (Component B)
placement_exam/.venv/bin/python placement_exam/planning_E03/scripts/assess_card_quality.py \
    --start 2026-05-19 --end 2026-06-15 \
    --deck-prefix PASSAGE_E04 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --detail-output placement_exam/planning_E04/output/E04_card_quality_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_card_quality_summary.csv

# Rastreabilidade de fontes (Component C)
placement_exam/.venv/bin/python placement_exam/planning_E04/scripts/assess_source_tracking.py \
    --start 2026-05-19 --end 2026-06-15 \
    --roster placement_exam/planning_E04/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E04/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260615/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260615/user_dbs \
    --deck-name AUTHENTIC_E04 \
    --detail-output placement_exam/planning_E04/output/E04_source_tracking_detail.csv \
    --summary-output placement_exam/planning_E04/output/E04_source_tracking_summary.csv
```

---

*Elaborado em: 22/06/2026*
*Dados: snapshot de produção local — `~/.cache/studyamigo/20260615`*
