# E02 — Análise Final de Resultados

**Exercício**: E02 — Criando seus primeiros flashcards
**Período**: 31/03/2026 – 13/04/2026 (14 dias)
**Turma**: 64 alunos no roster (Biotecnologia, Metrologia, Segurança Cibernética)
**Dados**: snapshot de produção em 14/04/2026 (`~/.cache/studyamigo/20260414`)
**Fórmula**: `Nota = 0.25×V + 0.25×C + 0.30×Q + 0.20×E`
**Scripts**: `grade_exercise_v2.py` + `account_map.csv`

---

## 1. Sumário de participação

| Situação | Alunos |
|----------|-------:|
| **Ativos** (roster + revisões no período) | **44** |
| Sem atividade — sem conta cadastrada | 3 |
| Sem atividade — conta existe, zero revisões | 17 |
| **Total no roster** | **64** |

**Taxa de participação**: 44/64 = **69%** (vs. 44/54 = 81% em E01 sobre o roster antigo).

A turma cresceu (9 alunos novos incorporados ao roster v2) e 14 contas secundárias foram mapeadas ao aluno correto via `account_map.csv`. Sem o mapeamento, apenas 34 alunos apareceriam como ativos.

### 1.1 Alunos sem conta cadastrada (3)

| ID | Nome | Curso | Tier | Email |
|----|------|-------|------|-------|
| 3011 | Eduardo Cardoso Oliveira | Biotecnologia | Tier 2 | eduardocardosooliveira81@gmail.com |
| 5026 | Cauê da Paixão Gomes | SegCiber | Tier 1 | caue9333@gmail.com |
| 5091 | Sophia Tavares dos Santos | SegCiber | Tier 2 | sophia2sun1@gmail.com |

> Nota E02 = 0.

### 1.2 Alunos com conta mas sem revisões no período (17)

| ID | Nome | Curso | Tier |
|----|------|-------|------|
| 3001 | Ana Manuela de Carvalho Trindade | Biotecnologia | Tier 2 |
| 3019 | Emanuel Melo dos Santos | Biotecnologia | — |
| 3026 | Gabriel Bernardo Do Nascimento | Biotecnologia | Tier 2 |
| 3031 | Maria Clara Mesquita Pires | Biotecnologia | Tier 1 |
| 3036 | Maria Eduarda De Lima Abreu | Biotecnologia | Tier 1 |
| 3041 | Maria Isabel Silva dos Santos | Biotecnologia | Tier 1 |
| 3056 | Wallace Gabriel Ferreira dos Santos | Biotecnologia | Tier 2 |
| 4018 | Edson José Bernardino | Metrologia | — |
| 4021 | Eduardo da Silva Fiuza | Metrologia | Tier 2 |
| 4036 | Isabel da Silva Peixoto | Metrologia | Tier 1 🏁 |
| 4066 | Laura Martins da Silva | Metrologia | Tier 1 🏁 |
| 4088 | Manuelly Alves Batista | Metrologia | — |
| 4101 | Thiago Kaleb Figueiredo de Oliveira | Metrologia | Tier 1 |
| 5041 | José Augusto Freire | SegCiber | Tier 1 🏁 |
| 5046 | João Ricardo Rocha de Carvalho | SegCiber | Tier 1 🏁 |
| 5071 | Marcella Vasconcelos Pacheco da Cruz | SegCiber | Tier 1 |
| 5086 | Samea Soares Pacheco | SegCiber | Tier 1 |

> Nota E02 = 0.

---

## 2. Resultados dos alunos ativos

### 2.1 Estatísticas gerais

| Métrica | Valor |
|---------|------:|
| Alunos ativos | 44 |
| Nota média | **62.1** |
| Nota mediana | **62.9** |
| Nota máxima | **85.8** |
| Nota mínima | **33.9** |
| Revisões — média | **54** |
| Revisões — máx | **203** |
| Retenção média | **89.8%** |
| Maturidade média | **5.1%** |
| Alunos com cartões maduros (ivl ≥ 21d) | 10 |

### 2.2 Distribuição de menções

| Menção | Intervalo | Alunos | % ativos |
|--------|-----------|-------:|---------:|
| A | ≥ 90 | 0 | 0% |
| B | 80–89 | 4 | 9% |
| C | 70–79 | 8 | 18% |
| D | 60–69 | 13 | 30% |
| F | < 60 | 19 | 43% |

### 2.3 Resultados por curso

| Curso | Ativos | Nota média | Rev média | Dist. (B/C/D/F) |
|-------|-------:|----------:|----------:|-----------------|
| Biotecnologia | 5 | 58.6 | 59 | 0/1/1/3 |
| Metrologia | 21 | 60.7 | 45 | 0/4/8/9 |
| SegCiber | 18 | 64.7 | 62 | 4/3/4/7 |

Segurança Cibernética mantém o melhor desempenho médio, com os 4 alunos com menção B. Biotecnologia registra a média mais baixa, com 3 dos 5 alunos ativos com F.

---

## 3. Ranking completo

| # | Nome | ID | Curso | Tier | Rev | Dias | Cards | Ret% | Mat% | V | C | Q | E | Nota | L | Flags |
|---|------|----|-------|------|----:|-----:|------:|-----:|-----:|--:|--:|--:|--:|-----:|---|-------|
| 1 | Mateus Ferreira Patrício *(Mahx.vpc)* | 5081 | SegCiber | Tier 2 | 159 | 4 | 35 | 92.6 | 1.1 | 100.0 | 100.0 | 65.2 | 81.4 | **85.8** | B | |
| 2 | Ezequiel Telles Pedrosa Dos Santos | 5031 | SegCiber | Tier 1 | 108 | 1 | 40 | 98.1 | 10.2 | 82.6 | 100.0 | 71.8 | 72.7 | **81.7** | B | |
| 3 | Adriany Praia Serafim | 5001 | SegCiber | Tier 2 | 98 | 4 | 36 | 100.0 | 0.0 | 78.6 | 100.0 | 70.0 | 79.9 | **81.6** | B | RET100 |
| 4 | MADSON FERREIRA DE SOUZA | 5066 | SegCiber | Tier 1 | 181 | 6 | 10 | 100.0 | 33.9 | 71.6 | 92.3 | 80.2 | 83.1 | **81.6** | B | RET100 |
| 5 | Laís Nascimento Silva | 4071 | Metrologia | Tier 1 | 82 | 6 | 8 | 100.0 | 74.2 | 41.5 | 99.4 | 92.3 | 84.6 | **79.8** | C | RET100 |
| 6 | Laryssa Vitória Ramos da Silva | 4061 | Metrologia | Tier 1 | 105 | 11 | 15 | 84.4 | 66.7 | 58.7 | 97.1 | 79.1 | 83.3 | **79.4** | C | |
| 7 | Matheus *(theuxzvA7X)* | 3046 | Biotecnologia | Tier 2 | 203 | 3 | 5 | 100.0 | 0.0 | 65.8 | 100.0 | 70.0 | 67.0 | **75.9** | C | RET100 |
| 8 | Lucas da Silva | 5056 | SegCiber | Tier 1 | 135 | 6 | 10 | 90.1 | 10.7 | 64.9 | 99.3 | 66.3 | 74.7 | **75.9** | C | |
| 9 | Arthur do Nascimento Paiva | 5011 | SegCiber | Tier 2 | 53 | 3 | 24 | 100.0 | 0.0 | 48.4 | 100.0 | 70.0 | 77.6 | **73.6** | C | |
| 10 | Julia de Oliveira Corrêa | 4051 | Metrologia | Tier 2 | 137 | 4 | 12 | 98.3 | 2.5 | 68.0 | 100.0 | 69.6 | 53.9 | **73.6** | C | |
| 11 | Philipe Emanuel de Souza Meireles | 5083 | SegCiber | — | 86 | 7 | 12 | 90.4 | 1.7 | 47.7 | 95.3 | 63.8 | 77.9 | **70.5** | C | |
| 12 | Leandro moreira Andrade Da silva | 4076 | Metrologia | Tier 1 | 68 | 3 | 21 | 80.9 | 0.0 | 50.9 | 100.0 | 56.6 | 77.5 | **70.2** | C | |
| 13 | Luiz Antonio Inácio Pereira | 4086 | Metrologia | Tier 2 | 83 | 4 | 6 | 88.4 | 0.0 | 39.6 | 97.6 | 61.9 | 78.2 | **68.5** | D | |
| 14 | Jady Maria Rodrigues Figueiredo | 5036 | SegCiber | Tier 1 | 91 | 4 | 10 | 82.6 | 22.9 | 47.4 | 83.5 | 64.7 | 79.1 | **67.9** | D | |
| 15 | Ana Carolina Barbosa | 4001 | Metrologia | Tier 2 | 50 | 6 | 14 | 91.7 | 0.0 | 35.7 | 100.0 | 64.2 | 73.2 | **67.8** | D | |
| 16 | Ana Luiza Camilo da Silva *(Luiza.)* | 4011 | Metrologia | Tier 1 | 65 | 4 | 17 | 100.0 | 0.0 | 45.1 | 82.3 | 70.0 | 71.1 | **67.1** | D | RET100 |
| 17 | Fernando Henrique Souza Laia | 3021 | Biotecnologia | Tier 1 | 19 | 2 | 13 | 100.0 | 0.0 | 22.2 | 97.4 | 70.0 | 77.7 | **66.4** | D | |
| 18 | Isabella | 4041 | Metrologia | Tier 2 | 26 | 5 | 11 | 100.0 | 0.0 | 22.7 | 92.3 | 70.0 | 78.8 | **65.5** | D | |
| 19 | Ana Julia de Souza Oliveira *(anajulisot)* | 4006 | Metrologia | Tier 1 | 12 | 1 | 10 | 100.0 | 0.0 | 15.9 | 100.0 | 70.0 | 77.3 | **65.4** | D | |
| 20 | Anthony Lucas Muniz Dos Santos *(Anthony000)* | 5008 | SegCiber | — | 17 | 2 | 10 | 100.0 | 0.0 | 17.9 | 100.0 | 70.0 | 71.4 | **64.8** | D | |
| 21 | Bernardo Silva | 5016 | SegCiber | Tier 2 | 11 | 2 | 5 | 100.0 | 0.0 | 9.8 | 100.0 | 70.0 | 77.3 | **63.9** | D | |
| 22 | Keyrrison da Silva braga | 4060 | Metrologia | — | 20 | 3 | 8 | 100.0 | 0.0 | 16.8 | 90.0 | 70.0 | 77.7 | **63.2** | D | |
| 23 | Eloá de Oliveira Amorim *(eloaamorim)* | 4026 | Metrologia | Tier 1 | 15 | 2 | 13 | 100.0 | 0.0 | 20.6 | 86.7 | 70.0 | 73.9 | **62.6** | D | |
| 24 | Lenilson Maia Rodrigues de Lima | 5051 | SegCiber | Tier 1 | 26 | 3 | 12 | 100.0 | 0.0 | 23.8 | 100.0 | 70.0 | 48.5 | **61.7** | D | |
| 25 | Victor Anderson Reis | 4106 | Metrologia | Tier 2 | 13 | 1 | 8 | 80.0 | 0.0 | 14.0 | 100.0 | 56.0 | 77.3 | **60.8** | D | |
| 26 | Daniel André de Oliveira *(Daniel A.)* | 5028 | SegCiber | — | 25 | 3 | 10 | 80.0 | 0.0 | 21.1 | 86.0 | 56.0 | 78.3 | **59.2** | F | |
| 27 | Arthur Alves do Nascimento | 3006 | Biotecnologia | Tier 1 | 16 | 2 | 15 | 100.0 | 0.0 | 23.3 | 65.6 | 70.0 | 74.1 | **58.1** | F | |
| 28 | Bruno dos Santos Lima | 5021 | SegCiber | Tier 1 | 67 | 2 | 9 | 67.4 | 0.0 | 36.7 | 79.9 | 47.2 | 73.5 | **58.0** | F | |
| 29 | Jhonatan Brandão da Silva | 4046 | Metrologia | Tier 1 | 74 | 2 | 0 | 96.3 | 0.0 | 29.0 | 58.8 | 67.4 | 78.1 | **57.8** | F | CRAM |
| 30 | Márcio da Silva Bertucio | 5076 | SegCiber | Tier 1 | 11 | 2 | 11 | 100.0 | 0.0 | 16.7 | 59.1 | 70.0 | 77.3 | **55.4** | F | |
| 31 | Rogério Gabriel B. dos Santos Simões *(Rogério g)* | 4098 | Metrologia | — | 141 | 3 | 0 | 38.6 | 0.0 | 55.7 | 73.8 | 27.0 | 73.9 | **55.3** | F | |
| 32 | Miguel Monteiro Cunha de Araujo *(MIguel)* | 5082 | SegCiber | Tier 1 | 26 | 2 | 7 | 77.8 | 0.0 | 18.0 | 76.9 | 54.4 | 71.5 | **54.4** | F | |
| 33 | Luiz Henrique Silva de Carvalho | 5061 | SegCiber | Tier 1 🏁 | 3 | 2 | 2 | 100.0 | 0.0 | 3.1 | 66.7 | 70.0 | 77.3 | **53.9** | F | |
| 34 | Amanda Silva do Nascimento *(Flores)* | 4000 | Metrologia | — | 18 | 3 | 3 | 73.3 | 0.0 | 10.2 | 80.6 | 51.3 | 75.8 | **53.3** | F | |
| 35 | Kauã Alves da Silva de França | 4056 | Metrologia | Tier 1 | 10 | 1 | 10 | 100.0 | 0.0 | 15.1 | 50.0 | 70.0 | 77.3 | **52.7** | F | |
| 36 | Lucas Pandini Pinheiro | 4081 | Metrologia | Tier 2 | 2 | 1 | 0 | 100.0 | 0.0 | 0.4 | 100.0 | 70.0 | 27.3 | **51.6** | F | |
| 37 | ricardo rodrigues | 4096 | Metrologia | Tier 1 | 1 | 1 | 34 | 0.0 | 0.0 | 39.3 | 100.0 | 0.0 | 77.3 | **50.3** | F | |
| 38 | Samuel Martins Da Conceição | 3051 | Biotecnologia | Tier 1 | 4 | 1 | 3 | 100.0 | 0.0 | 4.7 | 50.0 | 70.0 | 77.3 | **50.1** | F | |
| 39 | Cauã Jorge de Nazareth Marins *(Cauã Nzth)* | 4016 | Metrologia | Tier 1 | 1 | 1 | 12 | 0.0 | 0.0 | 13.9 | 100.0 | 0.0 | 77.3 | **43.9** | F | |
| 40 | Marcelo Ygor S. de Sá Cordeiro | 4091 | Metrologia | Tier 1 | 4 | 1 | 10 | 0.0 | 0.0 | 12.8 | 100.0 | 0.0 | 77.3 | **43.6** | F | |
| 41 | ELIAS SOARES DUTRA DA CONCEICAO | 3016 | Biotecnologia | Tier 1 | 52 | 2 | 12 | 65.0 | 2.2 | 34.2 | 52.9 | 46.2 | 34.4 | **42.5** | F | LOW_TIME CRAM |
| 42 | Emanuelly Almeida da Silva | 4031 | Metrologia | Tier 1 | 26 | 3 | 10 | 25.0 | 0.0 | 21.5 | 63.5 | 17.5 | 75.0 | **41.5** | F | |
| 43 | Tainá Avelino Barbosa da Silva *(Tata)* | 5096 | SegCiber | Tier 2 | 4 | 1 | 0 | 0.0 | 0.0 | 1.2 | 100.0 | 0.0 | 77.3 | **40.8** | F | |
| 44 | Ana Beatriz Pontes de Almeida *(beatnik)* | 5006 | SegCiber | Tier 2 | 20 | 1 | 21 | 0.0 | 0.0 | 31.8 | 50.0 | 0.0 | 67.3 | **33.9** | F | CRAM |

> *Nomes em itálico entre parênteses = username da conta secundária mapeada via `account_map.csv`.*

---

## 4. Alertas e comportamentos suspeitos

| Aluno | ID | Flag | Detalhe |
|-------|----|------|---------|
| Adriany Praia Serafim | 5001 | RET100 | 62/62 revisões agendadas certas com 98 revisões totais |
| MADSON FERREIRA DE SOUZA | 5066 | RET100 | 158/158 acertos em 181 revisões totais; mas maturidade real de 33.9% atenua a suspeita |
| Laís Nascimento Silva | 4071 | RET100 | 74/74 acertos; maturidade de 74.2% sugere aprendizado genuíno |
| Matheus (theuxzvA7X) | 3046 | RET100 | 143/143 acertos em 203 revisões; maturidade 0% |
| Ana Luiza (Luiza.) | 4011 | RET100 | 48/48 acertos em 65 revisões; maturidade 0% |
| Jhonatan Brandão da Silva | 4046 | CRAM | 82.4% das revisões no último dia do período; 0 cards criados |
| ELIAS SOARES DUTRA DA CONCEICAO | 3016 | LOW_TIME + CRAM | 94.2% das revisões no último dia e `time_sub` = 15.4% |
| Ana Beatriz (beatnik) | 5006 | CRAM | 100% das revisões no último dia; 0% de retenção |

**Nota sobre RET100 com maturidade baixa**: Laís e Madson têm maturidade real elevada, o que corrobora o desempenho. Os demais casos de RET100 com maturidade 0% (Adriany, Matheus, Ana Luiza) merecem atenção.

---

## 5. Criação de cartões

E02 foi o primeiro exercício com criação de cartões. 40 dos 44 alunos ativos criaram pelo menos um cartão.

| Métrica | Valor |
|---------|------:|
| Alunos que criaram cartões | 40/44 (91%) |
| Média de cartões criados por aluno ativo | 12.1 |
| Máximo | 40 (Ezequiel Telles) |
| Mínimo (entre criadores) | 2 |

Os 4 alunos que não criaram cartões (Jhonatan, Lucas Pandini, Rogério Gabriel, Tainá) focaram apenas em revisar o baralho Verbal Tenses.

**Caso Rogério Gabriel [4098]**: 141 revisões com 0 cards criados e retenção de apenas 38.6% — padrão de aluno que revisou muito mas sem estrutura de aprendizado.

---

## 6. Maturidade — primeiro sinal real do SM-2 corrigido

Em E01 a maturidade foi praticamente zero para todos. Em E02, 10 alunos já apresentam cartões maduros (ivl ≥ 21d):

| Aluno | ID | Maturidade |
|-------|----|----------:|
| Laís Nascimento Silva | 4071 | **74.2%** |
| Laryssa Vitória Ramos da Silva | 4061 | **66.7%** |
| MADSON FERREIRA DE SOUZA | 5066 | 33.9% |
| Jady Maria Rodrigues Figueiredo | 5036 | 22.9% |
| Lucas da Silva | 5056 | 10.7% |
| Ezequiel Telles Pedrosa Dos Santos | 5031 | 10.2% |
| Julia de Oliveira Corrêa | 4051 | 2.5% |
| ELIAS SOARES DUTRA DA CONCEICAO | 3016 | 2.2% |
| Philipe Emanuel de Souza Meireles | 5083 | 1.7% |
| Mateus Ferreira Patrício (Mahx.vpc) | 5081 | 1.1% |

Laís e Laryssa destacam-se com maturidade acima de 65% — cartões herdados de E01 que continuaram sendo revisados com sucesso após a correção do SM-2.

---

## 7. Distribuição de dias de estudo

| Dias ativos | Alunos |
|------------:|-------:|
| 1 | 11 |
| 2 | 11 |
| 3 | 9 |
| 4 | 6 |
| 5 | 1 |
| 6 | 4 |
| 7 | 1 |
| 11 | 1 |

**50% dos alunos ativos estudaram 1 ou 2 dias** — concentração ainda elevada, porém ligeiramente melhor que a versão sem mapeamento (52%). O aluno mais consistente foi Laryssa com 11 dias ativos.

---

## 8. Comparação E01 → E02

| Métrica | E01 | E02 |
|---------|----:|----:|
| Alunos no roster | 54 | 64 |
| Ativos (com revisões) | 44 | 44 |
| Taxa de participação (sobre roster) | 81% | 69% |
| Revisões médias | 154 | 54 |
| Retenção média | — | 89.8% |
| Maturidade média | ~0% | 5.1% |
| Menções B ou acima | 3 | 4 |

A queda em revisões era esperada: E02 exige criação de cartões, dividindo o tempo do aluno. Os 44 ativos em E02 correspondem exatamente ao mesmo número de E01, porém sobre uma turma 18% maior.

---

## 9. Mapeamento de contas secundárias aplicado

O arquivo `account_map.csv` associou 14 usernames de contas secundárias aos seus alunos no roster. Sem esse mapeamento, esses alunos apareceriam como "fora do roster" na seção 6 do relatório anterior.

| Username secundário | Aluno real | ID |
|--------------------|------------|----|
| Mahx.vpc | Mateus Ferreira Patrício | 5081 |
| theuxzvA7X | Matheus Dias Gomes | 3046 |
| Rogério g | Rogério Gabriel B. dos Santos Simões | 4098 |
| Luiza. | Ana Luiza Camilo da Silva | 4011 |
| Daniel A. | Daniel André de Oliveira | 5028 |
| MIguel | Miguel Monteiro Cunha de Araujo | 5082 |
| beatnik | Ana Beatriz Pontes de Almeida | 5006 |
| Flores | Amanda Silva do Nascimento | 4000 |
| eloaamorim | Eloá de Oliveira Amorim | 4026 |
| Anthony000 | Anthony Lucas Muniz Dos Santos | 5008 |
| José augus | José Augusto Freire | 5041 |
| anajulisot | Ana Julia de Souza Oliveira | 4006 |
| Tata | Tainá Avelino Barbosa da Silva | 5096 |
| Cauã Nzth | Cauã Jorge de Nazareth Marins | 4016 |

> O aluno **Miguel Monteiro Cunha de Araujo** [5082] é novo e foi adicionado ao roster v2 manualmente. Não constava no placement exam original.

---

## 10. Reproduzindo os resultados

```bash
placement_exam/.venv/bin/python placement_exam/planning_E02/scripts/grade_exercise_v2.py \
    --interval custom --start 2026-03-31 --end 2026-04-13 \
    --label E02 \
    --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \
    --account-map placement_exam/planning_E02/account_map.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260414/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260414/user_dbs \
    --output placement_exam/planning_E02/E02_final_grades.csv
```

---

*Elaborado em: 14/04/2026*
*Dados: snapshot de produção via SSH — EC2 `54.152.109.26`, `/opt/study-amigo/server`*
