# E03 — Análise Final de Resultados

**Exercício**: E03 — Consolidando seus flashcards
**Período**: 19/04/2026 – 17/05/2026 (29 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Dados**: snapshot de produção em 18/05/2026 (`~/.cache/studyamigo/20260518`)
**Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E`
**Scripts**: `grade_exercise_v2.py` + `account_map.csv`

---

## 1. Sumário de participação

| Situação | Alunos |
|----------|-------:|
| **Ativos** (roster + revisões no período) | **39** |
| Sem atividade — sem conta cadastrada | 1 |
| Sem atividade — conta existe, zero revisões | 24 |
| **Total no roster** | **64** |

**Taxa de participação**: 39/64 = **61%** (vs. 44/64 = 69% em E02).

Queda de participação em relação a E02, mas recuperação parcial no último dia do exercício: 6 alunos que não constavam no snapshot de 17/05 apareceram com atividade no snapshot final de 18/05.

### 1.1 Alunos sem conta cadastrada (1)

| ID | Nome | Curso | Tier | Email |
|----|------|-------|------|-------|
| 5091 | Sophia Tavares dos Santos | SegCiber | Tier 2 | sophia2sun1@gmail.com |

> Nota E03 = 0.

### 1.2 Alunos com conta mas sem revisões no período (24)

| ID | Nome | Curso | Tier |
|----|------|-------|------|
| 3011 | Eduardo Cardoso Oliveira | Biotecnologia | Tier 2 |
| 3016 | Elias Soares Dutra da Conceição | Biotecnologia | Tier 1 |
| 3026 | Gabriel Bernardo Do Nascimento | Biotecnologia | Tier 2 |
| 3041 | Maria Isabel Silva dos Santos | Biotecnologia | Tier 1 |
| 3051 | Samuel Martins Da Conceição | Biotecnologia | Tier 1 |
| 4006 | Ana Julia de Souza Oliveira | Metrologia | Tier 1 |
| 4018 | Edson José Bernardino | Metrologia | — |
| 4026 | Eloá de Oliveira Amorim | Metrologia | Tier 1 |
| 4036 | Isabel da Silva Peixoto | Metrologia | Tier 1 🏁 |
| 4046 | Jhonatan Brandão da Silva | Metrologia | Tier 1 |
| 4056 | Kauã Alves da Silva de França | Metrologia | Tier 1 |
| 4086 | Luiz Antonio Inácio Pereira | Metrologia | Tier 2 |
| 4088 | Manuelly Alves Batista | Metrologia | — |
| 4098 | Rogério Gabriel Barros dos Santos Simões | Metrologia | — |
| 4101 | Thiago Kaleb Figueiredo de Oliveira | Metrologia | Tier 1 |
| 4106 | Victor Anderson Reid | Metrologia | Tier 2 |
| 5008 | Anthony Lucas Muniz Dos Santos | SegCiber | — |
| 5011 | Arthur do Nascimento Paiva | SegCiber | Tier 2 |
| 5026 | Cauê da Paixão Gomes | SegCiber | Tier 1 |
| 5028 | Daniel André de Oliveira | SegCiber | — |
| 5046 | João Ricardo Rocha de Carvalho | SegCiber | Tier 1 🏁 |
| 5061 | Luiz Henrique Silva de Carvalho | SegCiber | Tier 1 🏁 |
| 5071 | Marcella Vasconcelos Pacheco da Cruz | SegCiber | Tier 1 |
| 5082 | Miguel Monteiro Cunha de Araujo | SegCiber | Tier 1 |

> Nota E03 = 0.

---

## 2. Resultados dos alunos ativos

### 2.1 Estatísticas gerais

| Métrica | Valor |
|---------|------:|
| Alunos ativos | 39 |
| Nota média | **64.2** |
| Nota mediana | **63.1** |
| Nota máxima | **93.3** |
| Nota mínima | **38.3** |
| Revisões — média | **72** |
| Revisões — máx | **239** |
| Retenção média | **88.8%** |
| Maturidade média | **10.7%** |
| Alunos com cartões maduros (ivl ≥ 21d) | 6 |

### 2.2 Distribuição de menções

| Menção | Intervalo | Alunos | % ativos |
|--------|-----------|-------:|---------:|
| A | ≥ 90 | 3 | 8% |
| B | 80–89 | 3 | 8% |
| C | 70–79 | 3 | 8% |
| D | 60–69 | 14 | 36% |
| F | < 60 | 16 | 41% |

### 2.3 Resultados por curso

| Curso | Ativos | Nota média | Rev média | Dist. (A/B/C/D/F) |
|-------|-------:|----------:|----------:|-----------------|
| Biotecnologia | 8 | 56.7 | 46 | 0/0/0/2/6 |
| Metrologia | 16 | 66.9 | 81 | 1/2/1/6/6 |
| SegCiber | 15 | 65.4 | 76 | 2/1/2/6/4 |

Metrologia lidera pela primeira vez — puxada pela consistência de Laryssa (93.3) e pelo progresso de Ana Carolina e Ana Luiza. Biotecnologia mantém a média mais baixa com 6 dos 8 ativos com F.

---

## 3. Ranking completo

| # | Nome | ID | Curso | Tier | Rev | Dias | Cards | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|------|----|-------|------|----:|-----:|------:|-----:|-----:|--:|--:|--:|--:|-----:|---|-------|
| 1 | Laryssa Vitória Ramos da Silva | 4061 | Metrologia | Tier 1 | 239 | 22 | 25 | 89.3 | 92.1 | 95.7 | 100.0 | 90.1 | 86.8 | **93.3** | A | |
| 2 | Madson Ferreira de Souza | 5066 | SegCiber | Tier 1 | 209 | 10 | 15 | 100.0 | 100.0 | 81.4 | 100.0 | 100.0 | 87.2 | **92.8** | A | RET100 |
| 3 | Laís Nascimento Silva | 4071 | Metrologia | Tier 1 | 177 | 8 | 18 | 100.0 | 87.2 | 78.5 | 100.0 | 96.2 | 85.5 | **90.6** | A | RET100 |
| 4 | Mateus Ferreira Patrício | 5081 | SegCiber | Tier 2 | 200 | 8 | 18 | 95.4 | 65.6 | 85.4 | 100.0 | 86.5 | 55.4 | **83.4** | B | |
| 5 | Ana Carolina Barbosa da Costa | 4001 | Metrologia | Tier 2 | 190 | 7 | 23 | 88.0 | 20.5 | 89.6 | 97.4 | 67.8 | 76.7 | **82.4** | B | |
| 6 | Ana Luiza Camilo da Silva | 4011 | Metrologia | Tier 1 | 123 | 5 | 28 | 100.0 | 0.0 | 76.6 | 100.0 | 70.0 | 76.9 | **80.5** | B | RET100 |
| 7 | Jady Maria Rodrigues Figueiredo | 5036 | SegCiber | Tier 1 | 81 | 10 | 15 | 90.9 | 46.7 | 45.4 | 96.3 | 77.6 | 81.4 | **75.0** | C | |
| 8 | Adriany Praia Serafim | 5001 | SegCiber | Tier 2 | 66 | 3 | 36 | 83.9 | 0.0 | 59.5 | 100.0 | 58.7 | 78.8 | **73.3** | C | |
| 9 | Ricardo de Souza Rodrigues | 4096 | Metrologia | Tier 1 | 33 | 4 | 18 | 100.0 | 0.0 | 35.3 | 100.0 | 70.0 | 77.8 | **70.4** | C | |
| 10 | Keyrrison da Silva Braga | 4060 | Metrologia | — | 38 | 5 | 16 | 100.0 | 0.0 | 34.0 | 100.0 | 70.0 | 77.3 | **69.9** | D | |
| 11 | Philipe Emanuel de Souza Meireles | 5083 | SegCiber | — | 50 | 4 | 17 | 100.0 | 0.0 | 39.0 | 91.0 | 70.0 | 81.5 | **69.8** | D | RET100 |
| 12 | Ana Manuela de Carvalho Trindade | 3001 | Biotecnologia | Tier 2 | 57 | 5 | 14 | 87.5 | 0.0 | 36.8 | 100.0 | 61.2 | 78.9 | **68.4** | D | |
| 13 | Isabella Queres | 4041 | Metrologia | Tier 2 | 26 | 4 | 11 | 100.0 | 0.0 | 23.2 | 100.0 | 70.0 | 76.6 | **67.1** | D | |
| 14 | Marcelo Ygor de Sá Cordeiro | 4091 | Metrologia | Tier 1 | 20 | 4 | 10 | 100.0 | 0.0 | 20.0 | 100.0 | 70.0 | 79.3 | **66.9** | D | |
| 15 | Matheus Dias Gomes *(theuxzvA7X)* | 3046 | Biotecnologia | Tier 2 | 111 | 2 | 11 | 100.0 | 11.7 | 48.7 | 98.6 | 73.5 | 34.2 | **65.7** | D | RET100 LOW_TIME |
| 16 | Eduardo da Silva Fiuza | 4021 | Metrologia | Tier 2 | 108 | 1 | 5 | 99.1 | 34.3 | 39.3 | 100.0 | 79.6 | 36.2 | **65.9** | D | LOW_TIME |
| 17 | Leandro Moreira Andrade da Silva | 4076 | Metrologia | Tier 1 | 91 | 6 | 15 | 63.2 | 0.0 | 48.4 | 98.4 | 44.2 | 77.6 | **65.5** | D | |
| 18 | Ana Beatriz Pontes de Almeida *(beatnik)* | 5006 | SegCiber | Tier 2 | 120 | 2 | 13 | 89.6 | 0.0 | 54.3 | 77.9 | 62.7 | 65.6 | **65.0** | D | |
| 19 | Bernardo Da Silva Lucas | 5016 | SegCiber | Tier 2 | 77 | 2 | 14 | 85.7 | 0.0 | 42.8 | 66.9 | 60.0 | 79.3 | **61.3** | D | |
| 20 | Amanda Silva do Nascimento *(Flores)* | 4000 | Metrologia | — | 46 | 9 | 9 | 83.8 | 8.7 | 26.4 | 91.3 | 61.3 | 74.7 | **62.7** | D | |
| 21 | Ezequiel Telles Pedrosa dos Santos | 5031 | SegCiber | Tier 1 | 14 | 2 | 16 | 100.0 | 0.0 | 26.8 | 100.0 | 70.0 | 52.3 | **63.1** | D | |
| 22 | Marcio da Silva Bertucio | 5076 | SegCiber | Tier 1 | 112 | 3 | 13 | 70.8 | 0.0 | 51.9 | 100.0 | 49.6 | 51.1 | **63.1** | D | |
| 23 | José Augusto Freire | 5041 | SegCiber | Tier 1 🏁 | 25 | 1 | 10 | 73.3 | 0.0 | 21.5 | 100.0 | 51.3 | 77.6 | **61.3** | D | |
| 24 | Lenilson Maia Rodrigues de Lima | 5051 | SegCiber | Tier 1 | 45 | 3 | 15 | 100.0 | 0.0 | 34.6 | 83.3 | 70.0 | 43.2 | **59.1** | F | RET100 LOW_TIME |
| 25 | Lucas da Silva Santos | 5056 | SegCiber | Tier 1 | 20 | 2 | 15 | 70.0 | 0.0 | 27.1 | 100.0 | 49.0 | 60.6 | **58.6** | F | |
| 26 | Bruno dos Santos Lima | 5021 | SegCiber | Tier 1 | 9 | 1 | 0 | 100.0 | 0.0 | 2.4 | 100.0 | 70.0 | 61.4 | **58.9** | F | |
| 27 | Tainá Avelino Barbosa da Silva *(Tata)* | 5096 | SegCiber | Tier 2 | 104 | 3 | 20 | 72.9 | 0.0 | 59.5 | 72.1 | 51.0 | 48.0 | **57.8** | F | |
| 28 | Wallace Gabriel Ferreira dos Santos | 3056 | Biotecnologia | Tier 2 | 24 | 1 | 20 | 100.0 | 0.0 | 35.5 | 50.0 | 70.0 | 77.3 | **57.8** | F | CRAM |
| 29 | Laura Martins da Silva | 4066 | Metrologia | Tier 1 🏁 | 114 | 2 | 0 | 60.6 | 0.0 | 33.9 | 82.9 | 42.4 | 77.2 | **57.4** | F | |
| 30 | Fernando Henrique Souza Laia | 3021 | Biotecnologia | Tier 1 | 15 | 1 | 12 | 100.0 | 0.0 | 21.3 | 50.0 | 70.0 | 77.3 | **54.3** | F | |
| 31 | Arthur Alves do Nascimento | 3006 | Biotecnologia | Tier 1 | 15 | 1 | 10 | 100.0 | 0.0 | 18.5 | 50.0 | 70.0 | 77.3 | **53.6** | F | |
| 32 | Julia de Oliveira Corrêa | 4051 | Metrologia | Tier 2 | 46 | 1 | 23 | 65.4 | 0.0 | 46.4 | 50.0 | 45.8 | 77.3 | **53.3** | F | CRAM |
| 33 | Emanuel Melo dos Santos | 3019 | Biotecnologia | — | 110 | 3 | 0 | 67.7 | 1.2 | 32.7 | 71.8 | 47.8 | 61.7 | **52.8** | F | |
| 34 | Maria Clara Mesquita Pires | 3031 | Biotecnologia | Tier 1 | 1 | 1 | 1 | 100.0 | 0.0 | 1.4 | 100.0 | 70.0 | 27.3 | **51.8** | F | |
| 35 | Lucas Pandini Pinheiro | 4081 | Metrologia | Tier 2 | 15 | 3 | 6 | 100.0 | 0.0 | 12.8 | 80.0 | 70.0 | 35.6 | **51.3** | F | |
| 36 | Maria Eduarda De Lima Abreu | 3036 | Biotecnologia | Tier 1 | 38 | 1 | 19 | 94.7 | 0.0 | 38.2 | 50.0 | 66.3 | 35.3 | **49.0** | F | LOW_TIME CRAM |
| 37 | Emanuelly Almeida da Silva | 4031 | Metrologia | Tier 1 | 4 | 1 | 18 | 0.0 | 0.0 | 26.6 | 100.0 | 0.0 | 77.3 | **47.1** | F | |
| 38 | Cauã Jorge de Nazareth Marins | 4016 | Metrologia | Tier 1 | 19 | 1 | 12 | 57.9 | 0.0 | 22.5 | 50.0 | 40.5 | 76.5 | **45.6** | F | |
| 39 | Samea Soares Pacheco | 5086 | SegCiber | Tier 1 | 6 | 1 | 28 | 0.0 | 0.0 | 41.5 | 50.0 | 0.0 | 77.3 | **38.3** | F | |

> *Nomes em itálico entre parênteses = username da conta secundária mapeada via `account_map.csv`.*

---

## 4. Alertas e comportamentos suspeitos

| Aluno | ID | Flag | Detalhe |
|-------|----|------|---------|
| Madson Ferreira de Souza | 5066 | RET100 | 194/194 acertos; maturidade 100% atenua suspeita — aprendizado consolidado |
| Laís Nascimento Silva | 4071 | RET100 | 159/159 acertos; maturidade 87.2% — consistente com aprendizado genuíno |
| Ana Luiza Camilo da Silva | 4011 | RET100 | 95/95 acertos; maturidade 0% — padrão suspeito mantido de E02 |
| Philipe Emanuel de Souza Meireles | 5083 | RET100 | 33/33 acertos; maturidade 0% |
| Lenilson Maia Rodrigues de Lima | 5051 | RET100 + LOW_TIME | 30/30 acertos; maturidade 0%; tempo engajado = 28.2% |
| Matheus Dias Gomes (theuxzvA7X) | 3046 | RET100 + LOW_TIME | 103/103 acertos; maturidade 11.7%; tempo engajado = 7.2% |
| Eduardo da Silva Fiuza | 4021 | LOW_TIME | 108 revisões em 1 dia; tempo engajado = 8.3% |
| Wallace Gabriel Ferreira dos Santos | 3056 | CRAM | 24 revisões em 1 dia (100% cramming); 20 cards criados |
| Julia de Oliveira Corrêa | 4051 | CRAM | 46 revisões em 1 dia (100% cramming); 23 cards criados |
| Maria Eduarda De Lima Abreu | 3036 | LOW_TIME + CRAM | 38 revisões em 1 dia; tempo engajado = 15.8% |

**Nota sobre RET100 com maturidade alta**: Madson (100%) e Laís (87.2%) demonstram domínio real do conteúdo — padrão coerente com revisão prolongada de cartões que já atingiram intervalos longos. Os demais RET100 com maturidade 0% (Ana Luiza, Philipe, Lenilson) continuam merecendo atenção.

**CRAM (3 alunos)**: Wallace, Julia e Maria Eduarda fizeram todas as revisões em um único dia — padrão de estudo de última hora sem espaçamento.

---

## 5. Criação de cartões

| Métrica | Valor |
|---------|------:|
| Alunos que criaram cartões | 33/39 (85%) |
| Média de cartões criados (entre criadores) | 15.4 |
| Máximo | 36 (Adriany Praia Serafim) |
| Mínimo (entre criadores) | 1 |

Os 6 alunos que não criaram cartões: Laura Martins da Silva, Bruno dos Santos Lima, Emanuel Melo dos Santos, Samea Soares Pacheco (criou 28 cards fora do período?), e os inativos com cards_created > 0 mas sem revisões contabilizadas.

**Caso Samea Soares Pacheco [5086]**: 28 cards criados mas apenas 6 revisões, 0% retenção — criou cartões mas não os revisou adequadamente.

---

## 6. Maturidade — consolidação do SM-2

Em E03, 6 alunos apresentam cartões maduros (ivl ≥ 21d), com destaque para a progressão dos top performers:

| Aluno | ID | Maturidade E02 | Maturidade E03 |
|-------|----|---------------:|---------------:|
| Madson Ferreira de Souza | 5066 | 33.9% | **100.0%** |
| Laryssa Vitória Ramos da Silva | 4061 | 66.7% | **92.1%** |
| Laís Nascimento Silva | 4071 | 74.2% | **87.2%** |
| Mateus Ferreira Patrício | 5081 | 1.1% | **65.6%** |
| Eduardo da Silva Fiuza | 4021 | — | **34.3%** |
| Ana Carolina Barbosa da Costa | 4001 | 0.0% | **20.5%** |
| Matheus Dias Gomes | 3046 | 0.0% | **11.7%** |
| Amanda Silva do Nascimento | 4000 | — | **8.7%** |

Laryssa, Madson e Laís atingem maturidade acima de 87% — resultado da revisão consistente desde E01. A maturidade média subiu de 5.1% (E02) para **10.7%** (E03).

---

## 7. Distribuição de dias de estudo

| Dias ativos | Alunos |
|------------:|-------:|
| 1 | 12 |
| 2 | 5 |
| 3 | 7 |
| 4 | 3 |
| 5 | 3 |
| 6 | 1 |
| 7 | 1 |
| 8 | 2 |
| 9 | 1 |
| 10 | 3 |
| 22 | 1 |

**49% dos alunos ativos (19/39) estudaram apenas 1 ou 2 dias** — padrão persistente desde E02. Laryssa destaca-se com 22 dias de estudo (76% do período), seguida por Madson e Jady (10 dias cada).

---

## 8. Comparação E01 → E02 → E03

| Métrica | E01 | E02 | E03 |
|---------|----:|----:|----:|
| Alunos no roster | 54 | 64 | 64 |
| Ativos (com revisões) | 44 | 44 | 39 |
| Taxa de participação | 81% | 69% | **61%** |
| Revisões médias | 154 | 54 | 72 |
| Retenção média | — | 89.8% | 88.8% |
| Maturidade média | ~0% | 5.1% | **10.7%** |
| Menções A | 0 | 0 | **3** |
| Menções B ou acima | 3 | 4 | **6** |

A participação caiu de 69% para 61% (5 alunos a menos), mas os que permaneceram melhoraram: revisões médias subiram de 54 para 72, maturidade dobrou, e pela primeira vez há alunos com nota A. A retenção manteve-se estável em ~89%.

---

## 9. Mapeamento de contas secundárias aplicado

O mesmo `account_map.csv` de E02 foi utilizado (15 mapeamentos). Não houve novos casos de contas duplicadas identificados em E03.

---

## 10. Reproduzindo os resultados

```bash
python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-04-19 --end 2026-05-17 \
    --label E03 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260518/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260518/user_dbs \
    --output placement_exam/planning_E03/E03_final_grades.csv
```

---

*Elaborado em: 18/05/2026*
*Dados: snapshot de produção via SSH — EC2 `54.152.109.26`, `/opt/study-amigo/server`*
