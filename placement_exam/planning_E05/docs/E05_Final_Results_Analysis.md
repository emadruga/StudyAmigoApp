# E05 — Análise Final de Resultados

**Exercício**: E05 — Verbos Modais no Cotidiano
**Período**: 16/06/2026 – 05/07/2026 (19 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Dados**: snapshot de produção em 06/07/2026 (`~/.cache/studyamigo/20260706`)
**Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E`
**Penalidade**: RET100 + maturidade < 10% → nota máxima = 40 (flag `RET100_CAP`)
**Scripts**: `grade_exercise_v2.py` + `assess_card_quality.py` + `assess_source_tracking.py` + `account_map.csv`

---

## 1. Sumário de participação

| Situação | Alunos |
|----------|-------:|
| **Ativos** (roster + revisões no período) | **36** |
| Sem atividade — sem conta cadastrada | 1 |
| Sem atividade — conta existe, zero revisões | 27 |
| **Total no roster** | **64** |

**Taxa de participação**: 36/64 = **56%** (vs. 44/64 = 69% em E04).

Queda significativa de participação: 8 alunos a menos que em E04. O período mais curto (19 dias vs. 28 de E04) e a proximidade do fim do semestre podem ter contribuído. Notavelmente, alunos que tiveram bom desempenho em E04 ficaram inativos em E05 — Gabriel Bernardo (2º em E04, agora inativo) e Ricardo de Souza Rodrigues (3º em E04, criou 28 cartões mas fez zero revisões).

### 1.1 Alunos sem conta cadastrada (1)

| ID | Nome | Curso | Tier | Email |
|----|------|-------|------|-------|
| 5091 | Sophia Tavares dos Santos | SegCiber | Tier 2 | sophia2sun1@gmail.com |

> Nota E05 = 0.

### 1.2 Alunos com conta mas sem revisões no período (27)

| ID | Nome | Curso | Tier | Nota E04 |
|----|------|-------|------|-------:|
| 3006 | Arthur Alves do Nascimento | Biotecnologia | Tier 1 | 51.1 |
| 3021 | Fernando Henrique Souza Laia | Biotecnologia | Tier 1 | 0 |
| 3026 | Gabriel Bernardo Do Nascimento | Biotecnologia | Tier 2 | **83.3** |
| 3031 | Maria Clara Mesquita Pires | Biotecnologia | Tier 1 | 0 |
| 3046 | Matheus Dias Gomes | Biotecnologia | Tier 2 | 0 |
| 3051 | Samuel Martins Da Conceição | Biotecnologia | Tier 1 | 55.6 |
| 3056 | Wallace Gabriel Ferreira dos Santos | Biotecnologia | Tier 2 | 57.3 |
| 4006 | Ana Julia de Souza Oliveira | Metrologia | Tier 1 | 0 |
| 4016 | Cauã Jorge de Nazareth Marins | Metrologia | Tier 1 | 59.2 |
| 4018 | Edson José Bernardino | Metrologia | — | 0 |
| 4021 | Eduardo da Silva Fiuza | Metrologia | Tier 2 | 0 |
| 4026 | Eloá de Oliveira Amorim | Metrologia | Tier 1 | 67.6 |
| 4066 | Laura Martins da Silva | Metrologia | Tier 1 🏁 | 66.7 |
| 4076 | Leandro Moreira Andrade da Silva | Metrologia | Tier 1 | 71.9 |
| 4081 | Lucas Pandini Pinheiro | Metrologia | Tier 2 | 56.2 |
| 4088 | Manuelly Alves Batista | Metrologia | — | 0 |
| 4096 | Ricardo de Souza Rodrigues | Metrologia | Tier 1 | **82.8** |
| 4098 | Rogério Gabriel Barros dos Santos Simões | Metrologia | — | 0 |
| 4101 | Thiago Kaleb Figueiredo de Oliveira | Metrologia | Tier 1 | 0 |
| 4106 | Victor Anderson Reid | Metrologia | Tier 2 | 44.8 |
| 5006 | Ana Beatriz Pontes de Almeida | SegCiber | Tier 2 | 0 |
| 5008 | Anthony Lucas Muniz Dos Santos | SegCiber | — | 61.7 |
| 5011 | Arthur do Nascimento Paiva | SegCiber | Tier 2 | 69.7 |
| 5026 | Cauê da Paixão Gomes | SegCiber | Tier 1 | 0 |
| 5028 | Daniel André de Oliveira | SegCiber | — | 65.7 |
| 5041 | José Augusto Freire | SegCiber | Tier 1 🏁 | 0 |
| 5076 | Marcio da Silva Bertucio | SegCiber | Tier 1 | 59.4 |

> Nota E05 = 0.

**Destaque negativo**: Gabriel Bernardo [3026] (B em E04, nota 83.3) e Ricardo de Souza Rodrigues [4096] (B em E04, nota 82.8) desapareceram de E05. Ricardo criou 28 cartões no período mas não fez nenhuma revisão — possível desistência tardia ou problemas de agenda. Leandro Moreira [4076] (C em E04, 71.9) também tornou-se inativo.

---

## 2. Resultados dos alunos ativos

### 2.1 Estatísticas gerais

| Métrica | Valor |
|---------|------:|
| Alunos ativos | 36 |
| Nota média | **66.3** |
| Nota mediana | **68.1** |
| Nota máxima | **87.1** |
| Nota mínima | **25.9** |
| Revisões — média | **96** |
| Revisões — máx | **271** |
| Retenção média | **85.0%** |
| Maturidade média | **26.3%** |
| Alunos com cartões maduros (ivl ≥ 21d) | 18 |
| Alunos penalizados (RET100_CAP) | 1 |

### 2.2 Distribuição de menções

| Menção | Intervalo | Alunos | % ativos |
|--------|-----------|-------:|---------:|
| A | ≥ 90 | 0 | 0% |
| B | 80–89 | 9 | 25% |
| C | 70–79 | 8 | 22% |
| D | 60–69 | 8 | 22% |
| F | < 60 | 11 | 31% |

### 2.3 Resultados por curso

| Curso | Ativos | Nota média | Rev média | Dist. (A/B/C/D/F) |
|-------|-------:|----------:|----------:|-----------------|
| Biotecnologia | 6 | 49.4 | 39 | 0/0/0/2/4 |
| Metrologia | 14 | 75.1 | 133 | 0/7/1/3/3 |
| SegCiber | 16 | 64.9 | 85 | 0/2/7/3/4 |

**Metrologia domina E05**: nota média de 75.1, com 7 menções B — ocupando 7 das 9 posições B do ranking. Ana Carolina Barbosa da Costa [4001] lidera a turma com 87.1. Biotecnologia apresenta a menor média (49.4) e nenhum aluno acima de D, refletindo tanto a baixa participação quanto o desengajamento dos presentes.

---

## 3. Ranking completo

| # | Nome | ID | Curso | Tier | Rev | Dias | Cards | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|------|----|-------|------|----:|-----:|------:|-----:|-----:|--:|--:|--:|--:|-----:|---|-------|
| 1 | Ana Carolina Barbosa da Costa | 4001 | Metrologia | Tier 2 | 168 | 8 | 30 | 88.0 | 62.5 | 90.4 | 100.0 | 80.4 | 77.0 | **87.1** | B | |
| 2 | Philipe Emanuel de Souza Meireles | 5083 | SegCiber | — | 165 | 12 | 19 | 91.1 | 69.4 | 82.2 | 100.0 | 84.6 | 79.5 | **86.8** | B | |
| 3 | Keyrrison da Silva Braga | 4060 | Metrologia | — | 139 | 10 | 21 | 98.3 | 65.7 | 77.7 | 99.6 | 88.5 | 79.1 | **86.7** | B | |
| 4 | Laryssa Vitória Ramos da Silva | 4061 | Metrologia | Tier 1 | 177 | 16 | 35 | 85.2 | 51.9 | 93.2 | 93.2 | 75.2 | 81.6 | **85.5** | B | |
| 5 | Isabella Queres | 4041 | Metrologia | Tier 2 | 101 | 6 | 21 | 98.8 | 56.3 | 66.1 | 100.0 | 86.0 | 82.5 | **83.8** | B | |
| 6 | Emanuelly Almeida da Silva | 4031 | Metrologia | Tier 1 | 271 | 8 | 13 | 94.2 | 22.3 | 82.4 | 98.7 | 72.7 | 78.7 | **82.8** | B | |
| 7 | Laís Nascimento Silva | 4071 | Metrologia | Tier 1 | 97 | 13 | 16 | 100.0 | 60.5 | 56.3 | 99.0 | 88.2 | 81.5 | **81.6** | B | RET100 |
| 8 | Marcelo Ygor de Sá Cordeiro | 4091 | Metrologia | Tier 1 | 143 | 2 | 21 | 100.0 | 32.1 | 78.9 | 86.0 | 79.6 | 80.7 | **81.3** | B | RET100 |
| 9 | Julia de Oliveira Corrêa | 4051 | Metrologia | Tier 2 | 266 | 5 | 21 | 80.0 | 24.0 | 96.1 | 93.2 | 63.2 | 72.9 | **80.9** | B | |
| 10 | Lucas da Silva Santos | 5056 | SegCiber | Tier 1 | 174 | 4 | 8 | 100.0 | 25.4 | 66.0 | 89.1 | 77.6 | 77.5 | **77.6** | C | RET100 |
| 11 | Jhonatan Brandão da Silva | 4046 | Metrologia | Tier 1 | 176 | 2 | 21 | 97.1 | 5.0 | 89.0 | 73.6 | 69.4 | 79.0 | **77.3** | C | |
| 12 | Bernardo Da Silva Lucas | 5016 | SegCiber | Tier 2 | 133 | 3 | 18 | 75.7 | 40.7 | 70.7 | 94.0 | 65.2 | 81.0 | **76.9** | C | |
| 13 | Mateus Ferreira Patrício | 5081 | SegCiber | Tier 2 | 36 | 4 | 5 | 96.8 | 80.6 | 18.7 | 100.0 | 91.9 | 81.1 | **73.5** | C | |
| 14 | Adriany Praia Serafim | 5001 | SegCiber | Tier 2 | 72 | 4 | 0 | 95.8 | 67.3 | 21.1 | 95.8 | 87.3 | 85.7 | **72.5** | C | |
| 15 | Bruno dos Santos Lima | 5021 | SegCiber | Tier 1 | 94 | 5 | 16 | 85.7 | 1.6 | 55.3 | 100.0 | 60.5 | 75.9 | **72.2** | C | |
| 16 | Jady Maria Rodrigues Figueiredo | 5036 | SegCiber | Tier 1 | 66 | 7 | 15 | 92.2 | 0.0 | 45.1 | 97.7 | 64.5 | 82.7 | **71.6** | C | |
| 17 | Luiz Antonio Inácio Pereira | 4086 | Metrologia | Tier 2 | 101 | 3 | 5 | 92.0 | 4.3 | 38.6 | 100.0 | 65.7 | 79.7 | **70.3** | C | |
| 18 | Ana Luiza Camilo da Silva | 4011 | Metrologia | Tier 1 | 59 | 4 | 21 | 76.3 | 0.0 | 53.3 | 100.0 | 53.4 | 76.6 | **69.7** | D | |
| 19 | João Ricardo Rocha de Carvalho | 5046 | SegCiber | Tier 1 🏁 | 138 | 5 | 6 | 65.2 | 43.5 | 51.6 | 100.0 | 58.7 | 54.5 | **66.4** | D | |
| 20 | Miguel Monteiro Cunha de Araujo | 5082 | SegCiber | Tier 1 | 72 | 7 | 13 | 72.4 | 0.0 | 43.5 | 95.1 | 50.7 | 77.8 | **65.4** | D | |
| 21 | Amanda Silva do Nascimento | 4000 | Metrologia | — | 100 | 6 | 13 | 72.5 | 18.0 | 52.0 | 77.0 | 56.1 | 74.6 | **64.0** | D | |
| 22 | Elias Soares Dutra da Conceição | 3016 | Biotecnologia | Tier 1 | 98 | 4 | 19 | 55.7 | 0.0 | 61.7 | 94.9 | 39.0 | 64.7 | **63.8** | D | |
| 23 | Eduardo Cardoso Oliveira | 3011 | Biotecnologia | Tier 2 | 55 | 1 | 0 | 86.1 | 1.8 | 15.9 | 100.0 | 60.8 | 76.7 | **62.6** | D | |
| 24 | Luiz Henrique Silva de Carvalho | 5061 | SegCiber | Tier 1 🏁 | 99 | 1 | 0 | 99.0 | 36.4 | 29.4 | 100.0 | 80.2 | 29.9 | **62.4** | D | LOW_TIME |
| 25 | Marcella Vasconcelos Pacheco da Cruz | 5071 | SegCiber | Tier 1 | 13 | 1 | 0 | 100.0 | 100.0 | 3.1 | 50.0 | 100.0 | 84.6 | **60.2** | D | |
| 26 | Lenilson Maia Rodrigues de Lima | 5051 | SegCiber | Tier 1 | 43 | 2 | 16 | 78.6 | 0.0 | 39.8 | 64.0 | 55.0 | 77.4 | **57.9** | F | |
| 27 | Maria Eduarda De Lima Abreu | 3036 | Biotecnologia | Tier 1 | 25 | 1 | 7 | 100.0 | 0.0 | 18.8 | 100.0 | 70.0 | 32.0 | **57.1** | F | LOW_TIME |
| 28 | Kauã Alves da Silva de França | 4056 | Metrologia | Tier 1 | 47 | 1 | 0 | 59.3 | 2.9 | 13.5 | 100.0 | 42.3 | 77.0 | **56.5** | F | |
| 29 | Maria Isabel Silva dos Santos | 3041 | Biotecnologia | Tier 1 | 44 | 1 | 0 | 87.5 | 0.0 | 12.5 | 100.0 | 61.2 | 44.0 | **55.3** | F | |
| 30 | Tainá Avelino Barbosa da Silva | 5096 | SegCiber | Tier 2 | 107 | 3 | 16 | 63.6 | 2.2 | 59.3 | 83.6 | 45.2 | 27.6 | **54.8** | F | LOW_TIME |
| 31 | Ezequiel Telles Pedrosa dos Santos | 5031 | SegCiber | Tier 1 | 32 | 2 | 0 | 71.9 | 71.0 | 8.9 | 100.0 | 71.6 | 24.1 | **53.5** | F | LOW_TIME |
| 32 | Samea Soares Pacheco | 5086 | SegCiber | Tier 1 | 43 | 1 | 9 | 78.3 | 0.0 | 27.7 | 50.0 | 54.8 | 56.5 | **47.2** | F | CRAM |
| 33 | Isabel da Silva Peixoto | 4036 | Metrologia | Tier 1 🏁 | 11 | 1 | 10 | 0.0 | 0.0 | 19.7 | 100.0 | 0.0 | 68.2 | **43.5** | F | |
| 34 | Madson Ferreira de Souza | 5066 | SegCiber | Tier 1 | 68 | 8 | 17 | 100.0 | 0.0 | 49.1 | 100.0 | 70.0 | 84.1 | **40.0** | F | RET100 RET100_CAP |
| 35 | Emanuel Melo dos Santos | 3019 | Biotecnologia | — | 10 | 1 | 10 | 0.0 | 0.0 | 19.3 | 50.0 | 0.0 | 71.7 | **31.7** | F | |
| 36 | Ana Manuela de Carvalho Trindade | 3001 | Biotecnologia | Tier 2 | 3 | 1 | 3 | 0.0 | 0.0 | 5.2 | 50.0 | 0.0 | 60.6 | **25.9** | F | |

---

## 4. Alertas e comportamentos suspeitos

| Aluno | ID | Flag | Detalhe |
|-------|----|------|---------|
| Laís Nascimento Silva | 4071 | RET100 | 81/81 acertos; maturidade 60.5% — aprendizado consolidado; não penalizada |
| Marcelo Ygor de Sá Cordeiro | 4091 | RET100 | 122/122 acertos; maturidade 32.1% — não penalizado |
| Lucas da Silva Santos | 5056 | RET100 | 134/134 acertos; maturidade 25.4% — não penalizado |
| **Madson Ferreira de Souza** | 5066 | **RET100_CAP** | 51/51 acertos; maturidade 0% — **nota limitada a 40** (era 75.4) |
| Tainá Avelino Barbosa da Silva | 5096 | LOW_TIME | 107 revisões em 3 dias; tempo engajado 2.8% |
| Ezequiel Telles Pedrosa dos Santos | 5031 | LOW_TIME | 32 revisões em 2 dias; tempo engajado 0% |
| Luiz Henrique Silva de Carvalho | 5061 | LOW_TIME | 99 revisões em 1 dia; tempo engajado 1% |
| Maria Eduarda De Lima Abreu | 3036 | LOW_TIME | 25 revisões em 1 dia; tempo engajado 4% |
| Samea Soares Pacheco | 5086 | CRAM | 43 revisões em 1 dia (cramming ratio 100%) |

### Penalidade RET100_CAP

Em E05, apenas **1 aluno** foi penalizado (vs. 2 em E04):

- **Madson Ferreira de Souza [5066]**: 100% retenção + 0% maturidade → nota capped de **40** (original seria 75.4). Caso notável: Madson foi 4º lugar em E04 (nota 81.5) com maturidade 100% e 163 revisões. Em E05, apenas 68 revisões em 8 dias e nenhum cartão maduro — forte queda de engajamento. A maturidade zero indica que ele provavelmente revisou apenas cartões novos sem dar tempo de amadurecimento.

**Não penalizados** (RET100 com maturidade ≥ 10%): Laís (60.5%), Marcelo Ygor (32.1%) e Lucas da Silva Santos (25.4%).

---

## 5. Criação de cartões

| Métrica | Valor |
|---------|------:|
| Alunos que criaram cartões | 29/36 (81%) |
| Média de cartões criados (entre criadores) | 14.6 |
| Máximo | 35 (Laryssa Vitória Ramos da Silva) |
| Mínimo (entre criadores) | 3 |

Os 7 alunos ativos sem criação de cartões: Adriany Praia Serafim, Marcella Vasconcelos Pacheco da Cruz, Eduardo Cardoso Oliveira, Luiz Henrique Silva de Carvalho, Ezequiel Telles Pedrosa dos Santos, Maria Isabel Silva dos Santos, Kauã Alves da Silva de França. Destes, Eduardo, Luiz Henrique, Maria Isabel e Kauã estudaram apenas 1 dia cada.

**Comparação com E04**: média de cartões caiu de 20.2 para 14.6 — ajuste esperado dado o período mais curto (19 vs. 28 dias).

---

## 6. Maturidade — consolidação do SM-2

Em E05, **18 alunos** apresentam cartões maduros (ivl ≥ 21d), queda em relação a E04 (26 alunos), explicada pela menor participação. A maturidade média entre os ativos subiu para **26.3%** (vs. 20.9% em E04), indicando que os alunos que permaneceram são os mais consistentes.

| Aluno | ID | Mat% E04 | Mat% E05 | Δ |
|-------|----|----------:|---------:|--|
| Marcella Vasconcelos Pacheco da Cruz | 5071 | 70.4% | **100.0%** | ↑ |
| Mateus Ferreira Patrício | 5081 | 92.3% | **80.6%** | ↓ |
| Philipe Emanuel de Souza Meireles | 5083 | 27.7% | **69.4%** | ↑ |
| Adriany Praia Serafim | 5001 | 22.1% | **67.3%** | ↑ |
| Keyrrison da Silva Braga | 4060 | 60.5% | **65.7%** | ↑ |
| Ana Carolina Barbosa da Costa | 4001 | 33.0% | **62.5%** | ↑ |
| Laís Nascimento Silva | 4071 | 75.4% | **60.5%** | ↓ |
| Isabella Queres | 4041 | 48.3% | **56.3%** | ↑ |
| Laryssa Vitória Ramos da Silva | 4061 | 68.6% | **51.9%** | ↓ |
| João Ricardo Rocha de Carvalho | 5046 | 27.3% | **43.5%** | ↑ |

Philipe Emanuel (+41.7pp) e Adriany (+45.2pp) apresentam o maior crescimento. As quedas de Mateus Ferreira (92.3 → 80.6%) e Laryssa (68.6 → 51.9%) refletem criação de cartões novos (imaturos) que diluem a proporção.

---

## 7. Distribuição de dias de estudo

| Dias ativos | Alunos |
|------------:|-------:|
| 1 | 12 |
| 2 | 4 |
| 3 | 3 |
| 4 | 5 |
| 5 | 3 |
| 6 | 2 |
| 7 | 2 |
| 8 | 3 |
| 10 | 1 |
| 12 | 1 |
| 13 | 1 |
| 16 | 1 |

**33% dos alunos ativos (12/36) estudaram apenas 1 dia** — piora em relação a E04 (16%). O período mais curto combinado com a proximidade do fim do semestre parece ter concentrado a atividade em sessões únicas. Laryssa destaca-se novamente com **16 dias de estudo** (84% do período de 19 dias), seguida por Laís com 13 dias (68%) e Philipe com 12 dias (63%).

---

## 8. Component C — Rastreabilidade de fontes

### 8.1 Sumário de adesão

| Métrica | Valor |
|---------|------:|
| Alunos com baralho `AUTHENTIC_E05` | 18 |
| Alunos com ≥ 1 fonte rastreável | 17 |
| Total de fontes encontradas | 44 |
| Fontes válidas (URL ou padrão Artista — Título) | 32 (73%) |
| Fontes inválidas | 12 (27%) |
| Total de cartões de vocabulário | 144 |

### 8.2 Flags de rastreabilidade

| Flag | Alunos | Significado |
|------|-------:|-------------|
| `SEM_FONTE` | 1 | Cartões criados sem cartão-metadado (Ricardo de Souza Rodrigues) |
| `FONTE_INVALIDA` | 1 | Referências com formato inválido (Ana Luiza Camilo da Silva — 12 fontes) |
| `POUCOS_CARTOES` | 5 | Menos cartões de vocabulário que o mínimo por fonte |
| `POUCAS_FONTES` | 1 | Abaixo do mínimo de fontes para o tier (Ricardo) |

### 8.3 Destaques do Component C

- **Ana Carolina Barbosa da Costa [4001]**: 10 fontes diferentes (George Michael, Madonna, Joji, Bon Jovi, etc.) com 1 cartão por fonte — máximo de diversidade, mas `POUCOS_CARTOES` em todas as fontes. Mesmo padrão observado em E04.
- **Ana Luiza Camilo da Silva [4011]**: 16 "fontes", mas apenas 4 são válidas (URLs). As outras 12 são cartões onde a frente contém "FONTE" mas o verso é uma descrição/tradução em vez de URL ou referência formatada — flagged como `FONTE_INVALIDA`. Nenhum cartão de vocabulário associado (0 vocab cards). A aluna misturou o formato dos cartões de vocabulário com o formato do cartão-metadado.
- **Laryssa Vitória Ramos da Silva [4061]**: 3 fontes (Billy Joel, Laufey ×2) com distribuição variável (4, 6, 10 cartões) — `POUCOS_CARTOES` para a primeira fonte.
- **Isabella Queres [4041]**: 1 fonte (Coldplay — Clocks) com 11 cartões — excelente concentração e exploração profunda.
- **"Lauren Daigle — You Say" como fonte popular**: usada por 3 alunos diferentes (Emanuelly, Keyrrison, Marcelo Ygor).

### 8.4 Comparação Component C: E04 → E05

| Métrica | E04 | E05 |
|---------|----:|----:|
| Alunos com baralho AUTHENTIC | 20 | 18 |
| Fontes válidas | 41 (100%) | 32 (73%) |
| Fontes inválidas | 0 | **12** |
| Total de cartões de vocabulário | 203 | 144 |

A taxa de fontes válidas caiu significativamente (100% → 73%), inteiramente por conta de Ana Luiza [4011] cujas 12 fontes inválidas representam todo o retrocesso. Excluindo esse caso, a adesão ao formato seria 32/32 = 100%.

---

## 9. Qualidade de cartões (Component B)

| Métrica | E05 | E04 |
|---------|----:|----:|
| Alunos com baralho `PASSAGE_E05` | 16 | 18 |
| Total de cartões avaliados | 118 | 224 |
| Score médio de aderência | **91.4%** | **94.6%** |
| Cartões de baixa qualidade (< 33%) | 0 | 0 |
| Flag COPIA | 0 | 0 |

Leve queda de 3.2pp no score de aderência ao método. Nenhum cartão copiado ou de baixa qualidade. A queda vem principalmente do score do verso nos cartões Tier 2 (média ~1.1/2.0 vs. 2.0/2.0 no Tier 1), sugerindo que os alunos Tier 2 ainda têm dificuldade com o formato mais complexo (classe gramatical + colocação + tradução).

**Destaques de qualidade**:
- **Tier 1** — score ≥ 95%: Lenilson (98.3%), Miguel Monteiro (97.6%), Emanuelly (97.2%), Marcelo Ygor (96.7%), Ricardo (95.8%), Lucas da Silva Santos (95.8%), Laís (95.2%), Jady Maria (95.2%)
- **Tier 2** — score ≥ 80%: Ana Carolina (85.0%), Luiz Antonio (83.3%), Bernardo (83.3%), Isabella (81.5%)

---

## 10. Comparação E01 → E02 → E03 → E04 → E05

| Métrica | E01 | E02 | E03 | E04 | E05 |
|---------|----:|----:|----:|----:|----:|
| Alunos no roster | 54 | 64 | 64 | 64 | 64 |
| Ativos (com revisões) | 44 | 44 | 39 | 44 | **36** |
| Taxa de participação | 81% | 69% | 61% | 69% | **56%** |
| Revisões médias | 154 | 54 | 72 | 163 | **96** |
| Retenção média | — | 89.8% | 88.8% | 80.2% | **85.0%** |
| Maturidade média | ~0% | 5.1% | 10.7% | 20.9% | **26.3%** |
| Menções B ou acima | 3 | 4 | 5 | 6 | **9** |
| Menções A | 0 | 0 | 3 | 0 | 0 |
| Nota média (ativos) | — | 62.1 | 61.9 | 66.1 | **66.3** |
| Alunos penalizados (RET100_CAP) | — | — | 3 | 2 | **1** |
| Score aderência ao método | — | — | 89.0% | 94.6% | **91.4%** |

### Tendências em E05

- **Participação atinge mínimo histórico**: 56% — 13pp abaixo de E04. A combinação de período mais curto (19 vs. 28 dias) e final de semestre contribuiu para a queda. 27 alunos com conta mas sem nenhuma revisão — o maior número da série.
- **Menções B disparam**: 9 alunos com B (25% dos ativos) — máximo histórico. A seleção natural explica: os alunos que permaneceram são os mais comprometidos.
- **Maturidade continua subindo**: 20.9% → 26.3%. A tendência ascendente confirma que a revisão espaçada acumulada funciona para os alunos consistentes.
- **Retenção recupera**: 80.2% → 85.0%. A subida pode refletir o fato de que os alunos ativos em E05 são os mais experientes, com coleções mais maduras.
- **Nota média estagna**: 66.1 → 66.3 (+0.2). A nota não subiu significativamente porque o ganho em qualidade (Q) e maturidade foi compensado pela menor participação em volume (V médio caiu com menos dias disponíveis).
- **Penalizados caem**: de 2 para 1. Madson, surpreendentemente, foi o único penalizado após ter sido top 4 em E04.
- **Efeito bifurcação**: a turma se polarizou. Os bons ficaram melhores (mais B's), mas os fracos desistiram (mais inativos). O "meio" está esvaziando.

---

## 11. Mapeamento de contas secundárias aplicado

O mesmo `account_map.csv` de E02–E04 foi utilizado (15 mapeamentos). Não houve novos casos de contas duplicadas identificados em E05.

---

## 12. Casos notáveis

### Ascensões

| Aluno | E04 | E05 | Δ | Observação |
|-------|----:|----:|---|------------|
| Julia de Oliveira Corrêa | 65.6 (D) | **80.9 (B)** | +15.3 | De D para B — maior salto da turma |
| Isabella Queres | 73.9 (C) | **83.8 (B)** | +9.9 | De C para B — consolidação |
| Bruno dos Santos Lima | 62.2 (D) | **72.2 (C)** | +10.0 | De D para C |
| Luiz Antonio Inácio Pereira | 30.1 (F) | **70.3 (C)** | +40.2 | Maior salto absoluto: F → C |
| Samea Soares Pacheco | 0 (inativa) | **47.2 (F)** | — | Retornou à atividade |

### Quedas

| Aluno | E04 | E05 | Δ | Observação |
|-------|----:|----:|---|------------|
| Madson Ferreira de Souza | 81.5 (B) | **40.0 (F)** | −41.5 | B → F (RET100_CAP) |
| Ezequiel Telles Pedrosa dos Santos | 72.6 (C) | **53.5 (F)** | −19.1 | C → F (LOW_TIME) |
| Ana Manuela de Carvalho Trindade | 68.2 (D) | **25.9 (F)** | −42.3 | 3 revisões em 1 dia |

---

## 13. Reproduzindo os resultados

```bash
# Notas finais
placement_exam/.venv/bin/python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-06-16 --end 2026-07-05 \
    --label E05 \
    --roster placement_exam/planning_E05/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E05/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260706/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260706/user_dbs \
    --output placement_exam/planning_E05/output/E05_final_grades.csv

# Qualidade de cartões (Component B)
placement_exam/.venv/bin/python placement_exam/planning_E03/scripts/assess_card_quality.py \
    --start 2026-06-16 --end 2026-07-05 \
    --deck-prefix PASSAGE_E05 \
    --roster placement_exam/planning_E05/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E05/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260706/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260706/user_dbs \
    --detail-output placement_exam/planning_E05/output/E05_card_quality_detail.csv \
    --summary-output placement_exam/planning_E05/output/E05_card_quality_summary.csv

# Rastreabilidade de fontes (Component C)
placement_exam/.venv/bin/python placement_exam/planning_E04/scripts/assess_source_tracking.py \
    --start 2026-06-16 --end 2026-07-05 \
    --roster placement_exam/planning_E05/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E05/bases/account_map.csv \
    --admin-db ~/.cache/studyamigo/20260706/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260706/user_dbs \
    --deck-name AUTHENTIC_E05 \
    --detail-output placement_exam/planning_E05/output/E05_source_tracking_detail.csv \
    --summary-output placement_exam/planning_E05/output/E05_source_tracking_summary.csv
```

---

*Elaborado em: 06/07/2026*
*Dados: snapshot de produção local — `~/.cache/studyamigo/20260706`*
