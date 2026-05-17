# E03 — Análise Final de Resultados

**Exercício**: E03 — Consolidando seus flashcards
**Período**: 19/04/2026 – 17/05/2026 (29 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Dados**: snapshot de produção em 17/05/2026 (`~/.cache/studyamigo/20260517`)
**Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E`
**Scripts**: `grade_exercise_v2.py` + `account_map.csv`

---

## 1. Sumário de participação

| Situação | Alunos |
|----------|-------:|
| **Ativos** (roster + revisões no período) | **33** |
| Sem atividade — sem conta cadastrada | 1 |
| Sem atividade — conta existe, zero revisões | 30 |
| **Total no roster** | **64** |

**Taxa de participação**: 33/64 = **52%** (vs. 44/64 = 69% em E02).

Queda significativa de participação: 11 alunos que estavam ativos em E02 não registraram nenhuma atividade em E03. O `account_map.csv` manteve os mesmos 15 mapeamentos de E02.

### 1.1 Alunos sem conta cadastrada (1)

| ID | Nome | Curso | Tier | Email |
|----|------|-------|------|-------|
| 5091 | Sophia Tavares dos Santos | SegCiber | Tier 2 | sophia2sun1@gmail.com |

> Nota E03 = 0.

### 1.2 Alunos com conta mas sem revisões no período (30)

| ID | Nome | Curso | Tier |
|----|------|-------|------|
| 3006 | Arthur Alves do Nascimento | Biotecnologia | Tier 1 |
| 3011 | Eduardo Cardoso Oliveira | Biotecnologia | Tier 2 |
| 3016 | Elias Soares Dutra da Conceição | Biotecnologia | Tier 1 |
| 3021 | Fernando Henrique Souza Laia | Biotecnologia | Tier 1 |
| 3026 | Gabriel Bernardo Do Nascimento | Biotecnologia | Tier 2 |
| 3041 | Maria Isabel Silva dos Santos | Biotecnologia | Tier 1 |
| 3051 | Samuel Martins Da Conceição | Biotecnologia | Tier 1 |
| 3056 | Wallace Gabriel Ferreira dos Santos | Biotecnologia | Tier 2 |
| 4006 | Ana Julia de Souza Oliveira | Metrologia | Tier 1 |
| 4016 | Cauã Jorge de Nazareth Marins | Metrologia | Tier 1 |
| 4018 | Edson José Bernardino | Metrologia | — |
| 4026 | Eloá de Oliveira Amorim | Metrologia | Tier 1 |
| 4036 | Isabel da Silva Peixoto | Metrologia | Tier 1 🏁 |
| 4046 | Jhonatan Brandão da Silva | Metrologia | Tier 1 |
| 4051 | Julia de Oliveira Corrêa | Metrologia | Tier 2 |
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
| 5086 | Samea Soares Pacheco | SegCiber | Tier 1 |

> Nota E03 = 0.

---

## 2. Resultados dos alunos ativos

### 2.1 Estatísticas gerais

| Métrica | Valor |
|---------|------:|
| Alunos ativos | 33 |
| Nota média | **66.8** |
| Nota mediana | **64.1** |
| Nota máxima | **93.9** |
| Nota mínima | **47.5** |
| Revisões — média | **73** |
| Revisões — máx | **239** |
| Retenção média | **89.8%** |
| Maturidade média | **12.1%** |
| Alunos com cartões maduros (ivl ≥ 21d) | 7 |

### 2.2 Distribuição de menções

| Menção | Intervalo | Alunos | % ativos |
|--------|-----------|-------:|---------:|
| A | ≥ 90 | 3 | 9% |
| B | 80–89 | 3 | 9% |
| C | 70–79 | 4 | 12% |
| D | 60–69 | 13 | 39% |
| F | < 60 | 10 | 30% |

### 2.3 Resultados por curso

| Curso | Ativos | Nota média | Rev média | Dist. (A/B/C/D/F) |
|-------|-------:|----------:|----------:|-----------------|
| Biotecnologia | 5 | 57.6 | 60 | 0/0/0/1/4 |
| Metrologia | 14 | 70.1 | 83 | 1/2/2/5/4 |
| SegCiber | 14 | 66.8 | 69 | 2/1/2/7/2 |

Metrologia supera SegCiber pela primeira vez — puxada pela consistência de Laryssa (93.9) e pelo progresso de Ana Carolina e Ana Luiza. Biotecnologia mantém a média mais baixa com 4 dos 5 ativos com F.

---

## 3. Ranking completo

| # | Nome | ID | Curso | Tier | Rev | Dias | Cards | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|------|----|-------|------|----:|-----:|------:|-----:|-----:|--:|--:|--:|--:|-----:|---|-------|
| 1 | Laryssa Vitória Ramos da Silva | 4061 | Metrologia | Tier 1 | 239 | 22 | 25 | 89.3 | 92.1 | 98.2 | 100.0 | 90.1 | 86.8 | **93.9** | A | |
| 2 | Madson Ferreira de Souza | 5066 | SegCiber | Tier 1 | 209 | 10 | 15 | 100.0 | 100.0 | 82.9 | 100.0 | 100.0 | 87.2 | **93.2** | A | RET100 |
| 3 | Laís Nascimento Silva | 4071 | Metrologia | Tier 1 | 177 | 8 | 18 | 100.0 | 86.3 | 79.6 | 100.0 | 95.9 | 85.5 | **90.8** | A | RET100 |
| 4 | Mateus Ferreira Patrício | 5081 | SegCiber | Tier 2 | 200 | 8 | 18 | 95.4 | 65.6 | 86.4 | 100.0 | 86.5 | 55.4 | **83.6** | B | |
| 5 | Ana Carolina Barbosa da Costa | 4001 | Metrologia | Tier 2 | 180 | 6 | 20 | 88.1 | 21.1 | 83.5 | 100.0 | 68.0 | 76.4 | **81.6** | B | |
| 6 | Ana Luiza Camilo da Silva | 4011 | Metrologia | Tier 1 | 123 | 5 | 28 | 100.0 | 0.0 | 76.1 | 100.0 | 70.0 | 76.9 | **80.4** | B | RET100 |
| 7 | Adriany Praia Serafim | 5001 | SegCiber | Tier 2 | 66 | 3 | 36 | 83.9 | 0.0 | 59.2 | 100.0 | 58.7 | 77.4 | **72.9** | C | |
| 8 | Jady Maria Rodrigues Figueiredo | 5036 | SegCiber | Tier 1 | 75 | 9 | 15 | 90.0 | 13.3 | 44.8 | 100.0 | 67.0 | 80.7 | **72.4** | C | |
| 9 | Ricardo de Souza Rodrigues | 4096 | Metrologia | Tier 1 | 33 | 4 | 18 | 100.0 | 0.0 | 37.0 | 100.0 | 70.0 | 77.8 | **70.8** | C | |
| 10 | Keyrrison da Silva Braga | 4060 | Metrologia | — | 38 | 5 | 16 | 100.0 | 0.0 | 35.4 | 100.0 | 70.0 | 77.3 | **70.3** | C | |
| 11 | Philipe Emanuel de Souza Meireles | 5083 | SegCiber | — | 50 | 4 | 17 | 100.0 | 0.0 | 40.5 | 91.0 | 70.0 | 80.3 | **69.9** | D | RET100 |
| 12 | Ana Manuela de Carvalho Trindade | 3001 | Biotecnologia | Tier 2 | 57 | 5 | 14 | 87.5 | 0.0 | 38.0 | 100.0 | 61.2 | 78.9 | **68.6** | D | |
| 13 | Isabella Queres | 4041 | Metrologia | Tier 2 | 26 | 4 | 14 | 100.0 | 0.0 | 28.8 | 100.0 | 70.0 | 76.1 | **68.4** | D | |
| 14 | Marcelo Ygor de Sá Cordeiro | 4091 | Metrologia | Tier 1 | 20 | 4 | 10 | 100.0 | 0.0 | 20.9 | 100.0 | 70.0 | 77.6 | **66.7** | D | |
| 15 | Leandro Moreira Andrade da Silva | 4076 | Metrologia | Tier 1 | 88 | 5 | 15 | 64.4 | 0.0 | 48.7 | 100.0 | 45.1 | 77.7 | **66.2** | D | |
| 16 | Matheus Dias Gomes *(theuxzvA7X)* | 3046 | Biotecnologia | Tier 2 | 111 | 2 | 11 | 100.0 | 11.7 | 49.4 | 98.6 | 73.5 | 33.8 | **65.8** | D | RET100 LOW_TIME |
| 17 | Eduardo da Silva Fiuza | 4021 | Metrologia | Tier 2 | 108 | 1 | 0 | 99.1 | 34.3 | 31.7 | 100.0 | 79.6 | 36.2 | **64.1** | D | LOW_TIME |
| 18 | Amanda Silva do Nascimento *(Flores)* | 4000 | Metrologia | — | 38 | 8 | 8 | 86.7 | 0.0 | 23.2 | 100.0 | 60.7 | 74.6 | **63.9** | D | |
| 19 | Ezequiel Telles Pedrosa dos Santos | 5031 | SegCiber | Tier 1 | 14 | 2 | 16 | 100.0 | 0.0 | 28.3 | 100.0 | 70.0 | 52.3 | **63.5** | D | |
| 20 | Marcio da Silva Bertucio | 5076 | SegCiber | Tier 1 | 112 | 3 | 13 | 70.8 | 0.0 | 52.7 | 100.0 | 49.6 | 51.1 | **63.3** | D | |
| 21 | Lenilson Maia Rodrigues de Lima | 5051 | SegCiber | Tier 1 | 30 | 2 | 15 | 100.0 | 0.0 | 31.5 | 100.0 | 70.0 | 47.0 | **63.3** | D | |
| 22 | José Augusto Freire | 5041 | SegCiber | Tier 1 🏁 | 25 | 1 | 10 | 73.3 | 0.0 | 22.4 | 100.0 | 51.3 | 77.3 | **61.4** | D | |
| 23 | Bernardo Da Silva Lucas | 5016 | SegCiber | Tier 2 | 26 | 1 | 0 | 84.6 | 0.0 | 7.4 | 100.0 | 59.2 | 78.9 | **60.4** | D | |
| 24 | Laura Martins da Silva | 4066 | Metrologia | Tier 1 🏁 | 75 | 1 | 0 | 65.5 | 0.0 | 21.9 | 100.0 | 45.8 | 77.4 | **59.7** | F | |
| 25 | Ana Beatriz Pontes de Almeida *(beatnik)* | 5006 | SegCiber | Tier 2 | 67 | 1 | 0 | 85.7 | 0.0 | 19.5 | 100.0 | 60.0 | 56.4 | **59.2** | F | |
| 26 | Lucas da Silva Santos | 5056 | SegCiber | Tier 1 | 20 | 2 | 15 | 70.0 | 0.0 | 28.5 | 100.0 | 49.0 | 60.6 | **59.0** | F | |
| 27 | Bruno dos Santos Lima | 5021 | SegCiber | Tier 1 | 9 | 1 | 0 | 100.0 | 0.0 | 2.4 | 100.0 | 70.0 | 61.4 | **58.9** | F | |
| 28 | Lucas Pandini Pinheiro | 4081 | Metrologia | Tier 2 | 9 | 2 | 6 | 100.0 | 0.0 | 11.5 | 100.0 | 70.0 | 38.4 | **56.6** | F | |
| 29 | Tainá Avelino Barbosa da Silva *(Tata)* | 5096 | SegCiber | Tier 2 | 61 | 3 | 3 | 75.0 | 0.0 | 22.3 | 87.7 | 52.5 | 56.8 | **54.6** | F | |
| 30 | Emanuel Melo dos Santos | 3019 | Biotecnologia | — | 110 | 3 | 0 | 67.7 | 1.2 | 32.3 | 71.8 | 47.8 | 61.7 | **52.7** | F | |
| 31 | Maria Clara Mesquita Pires | 3031 | Biotecnologia | Tier 1 | 1 | 1 | 1 | 100.0 | 0.0 | 1.5 | 100.0 | 70.0 | 27.3 | **51.8** | F | |
| 32 | Maria Eduarda De Lima Abreu | 3036 | Biotecnologia | Tier 1 | 19 | 1 | 18 | 100.0 | 0.0 | 32.8 | 50.0 | 70.0 | 37.8 | **49.3** | F | |
| 33 | Emanuelly Almeida da Silva | 4031 | Metrologia | Tier 1 | 4 | 1 | 18 | 0.0 | 0.0 | 28.4 | 100.0 | 0.0 | 77.3 | **47.5** | F | |

> *Nomes em itálico entre parênteses = username da conta secundária mapeada via `account_map.csv`.*

---

## 4. Alertas e comportamentos suspeitos

| Aluno | ID | Flag | Detalhe |
|-------|----|------|---------|
| Madson Ferreira de Souza | 5066 | RET100 | 194/194 acertos; maturidade 100% atenua suspeita — aprendizado consolidado |
| Laís Nascimento Silva | 4071 | RET100 | 159/159 acertos; maturidade 86.3% — consistente com aprendizado genuíno |
| Ana Luiza Camilo da Silva | 4011 | RET100 | 95/95 acertos; maturidade 0% — padrão suspeito mantido de E02 |
| Philipe Emanuel de Souza Meireles | 5083 | RET100 | 33/33 acertos; maturidade 0% |
| Matheus Dias Gomes (theuxzvA7X) | 3046 | RET100 + LOW_TIME | 103/103 acertos; maturidade 11.7%; tempo engajado = 7.2% |
| Eduardo da Silva Fiuza | 4021 | LOW_TIME | 108 revisões em 1 dia; tempo engajado = 8.3%; 0 cards criados |

**Nota sobre RET100 com maturidade alta**: Madson (100%) e Laís (86.3%) demonstram domínio real do conteúdo — padrão coerente com revisão prolongada de cartões que já atingiram intervalos longos. Os demais RET100 com maturidade 0% (Ana Luiza, Philipe) continuam merecendo atenção.

**LOW_TIME**: Eduardo da Silva Fiuza revisou 108 cartões herdados de E02 em um único dia com apenas 8.3% de tempo engajado — sugere resposta automática sem leitura.

---

## 5. Criação de cartões

| Métrica | Valor |
|---------|------:|
| Alunos que criaram cartões | 27/33 (82%) |
| Média de cartões criados por aluno ativo | 13.8 |
| Máximo | 36 (Adriany Praia Serafim) |
| Mínimo (entre criadores) | 1 |

Os 6 alunos que não criaram cartões: Eduardo da Silva Fiuza, Bernardo Da Silva Lucas, Laura Martins, Ana Beatriz, Bruno dos Santos Lima, Emanuel Melo dos Santos.

**Caso Eduardo da Silva Fiuza [4021]**: 108 revisões em 1 dia, 0 cards criados, 34.3% maturidade — revisou apenas cartões herdados de E02 sem nenhuma criação nova.

---

## 6. Maturidade — consolidação do SM-2

Em E03, 7 alunos apresentam cartões maduros (ivl ≥ 21d), com destaque para a progressão dos top performers:

| Aluno | ID | Maturidade E02 | Maturidade E03 |
|-------|----|---------------:|---------------:|
| Madson Ferreira de Souza | 5066 | 33.9% | **100.0%** |
| Laryssa Vitória Ramos da Silva | 4061 | 66.7% | **92.1%** |
| Laís Nascimento Silva | 4071 | 74.2% | **86.3%** |
| Mateus Ferreira Patrício | 5081 | 1.1% | **65.6%** |
| Eduardo da Silva Fiuza | 4021 | — | **34.3%** |
| Ana Carolina Barbosa da Costa | 4001 | 0.0% | **21.1%** |
| Jady Maria Rodrigues Figueiredo | 5036 | 22.9% | **13.3%** |
| Matheus Dias Gomes | 3046 | 0.0% | **11.7%** |

Laryssa, Madson e Laís atingem maturidade acima de 86% — resultado da revisão consistente desde E01. A maturidade média subiu de 5.1% (E02) para **12.1%** (E03).

---

## 7. Distribuição de dias de estudo

| Dias ativos | Alunos |
|------------:|-------:|
| 1 | 8 |
| 2 | 6 |
| 3 | 5 |
| 4 | 4 |
| 5 | 4 |
| 6 | 1 |
| 8 | 3 |
| 9 | 1 |
| 10 | 1 |
| 22 | 1 |

**42% dos alunos ativos estudaram 1 ou 2 dias** — melhoria modesta em relação aos 50% de E02. Laryssa destaca-se com 22 dias de estudo (76% do período), seguida por Madson (10 dias) e Jady (9 dias).

---

## 8. Comparação E01 → E02 → E03

| Métrica | E01 | E02 | E03 |
|---------|----:|----:|----:|
| Alunos no roster | 54 | 64 | 64 |
| Ativos (com revisões) | 44 | 44 | 33 |
| Taxa de participação | 81% | 69% | **52%** |
| Revisões médias | 154 | 54 | 73 |
| Retenção média | — | 89.8% | 89.8% |
| Maturidade média | ~0% | 5.1% | **12.1%** |
| Menções A | 0 | 0 | **3** |
| Menções B ou acima | 3 | 4 | **6** |

A participação caiu de 69% para 52% (11 alunos abandonaram), mas os que permaneceram melhoraram: revisões médias subiram de 54 para 73, maturidade mais que dobrou, e pela primeira vez há alunos com nota A. A retenção manteve-se estável em ~90%.

---

## 9. Mapeamento de contas secundárias aplicado

O mesmo `account_map.csv` de E02 foi utilizado (15 mapeamentos). Não houve novos casos de contas duplicadas identificados em E03.

---

## 10. Reproduzindo os resultados

```bash
placement_exam/.venv/bin/python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-04-19 --end 2026-05-17 \
    --label E03 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/bases/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260517/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260517/user_dbs \
    --output placement_exam/planning_E03/E03_final_grades.csv
```

---

*Elaborado em: 17/05/2026*
*Dados: snapshot de produção via SSH — EC2 `54.152.109.26`, `/opt/study-amigo/server`*
