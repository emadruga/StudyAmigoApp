# E04 — Sugestões para o Próximo Semestre

*Elaborado em: 22/06/2026*

---

## 1. Limitação identificada: heurística RET100_CAP não diferencia trapaça de conhecimento prévio

### Contexto

A penalidade `RET100_CAP` foi introduzida em E03 e mantida em E04. Ela limita a nota final a 40 pontos quando o aluno tem:

- Retenção = 100% (zero erros em ≥ 30 revisões de repetição)
- Maturidade < 10% (nenhum cartão com ivl ≥ 21d)

A lógica é que 100% de acerto sem amadurecimento de cartões é estatisticamente improvável em aprendizado genuíno — o SM-2 é projetado para que o aluno erre ocasionalmente conforme os intervalos crescem e a memória decai.

### O problema

A heurística não consegue distinguir dois casos:

1. **Trapaça / resposta automática**: aluno clica "Easy" sem ler, acumula 100% sem esforço real
2. **Conhecimento prévio legítimo**: aluno já conhecia o vocabulário antes do exercício

O SM-2 não tem mecanismo anti-trapaça nativo. A heurística é externa e aceita falsos positivos.

### Por que o placement exam pode ajudar

O placement exam (Signal 1, fevereiro 2026) avalia proficiência de leitura em inglês e resultou na classificação dos alunos em tiers. Os dados confirmam que a turma tem base baixa:

- Média Path B/C: **9.66/25** (38.6%)
- 85% dos alunos Path B/C ficaram no range de Tier 1 (≤ 10/25)
- **Zero alunos** atingiram Tier 3, mesmo com threshold ajustado para 16/25

Um aluno Tier 1 (Foundation) ou Tier 2 (Developing) tem, por definição, pouca proficiência em inglês — o que torna improvável que ele já conheça *todo* o vocabulário dos baralhos antes do exercício. Como o próprio professor observou: *"eu que sou fluente em inglês me atrapalho com alguns tempos verbais"*.

Isso significa que o tier do placement pode servir como **filtro de plausibilidade** para o RET100_CAP: se o aluno é Tier 1 ou Tier 2, 100% de retenção com maturidade zero é mais suspeito do que seria para um Tier 3.

---

## 2. Opções de implementação (para análise no próximo semestre)

### Opção A — Tier como filtro binário *(mais simples)*

RET100_CAP só se aplica a Tier 1 e Tier 2. Alunos sem tier atribuído ou Tier 3 não são penalizados.

**Prós**: zero mudança na lógica de cálculo, apenas um filtro adicional.
**Contras**: não muda nada na prática em E04 — todos os penalizados já são Tier 1. Útil principalmente se houver alunos Tier 3 em semestres futuros.

---

### Opção B — Threshold de maturidade por tier *(mais refinado)*

Calibrar o threshold de maturidade mínimo para escapar da penalidade de acordo com o tier:

| Tier | Threshold de maturidade para disparar RET100_CAP |
|------|------------------------------------------------:|
| Tier 1 | < 10% (mais rigoroso) |
| Tier 2 | < 15% |
| Tier 3 | não aplicar (ou < 5% apenas) |

**Prós**: reconhece que alunos mais avançados têm maior probabilidade de conhecimento prévio legítimo.
**Contras**: os thresholds são arbitrários e precisariam de validação empírica com mais semestres de dados.

---

### Opção C — Score bruto do placement como parâmetro contínuo *(mais sofisticado)*

Usar o score numérico do placement (0–25) diretamente: quanto menor o score, maior a exigência de maturidade para escapar da penalidade.

**Exemplo de fórmula**:
```
threshold_maturidade = 10% + (1 - score/25) × 10%
```
Aluno com score 5/25 precisaria de 18% de maturidade para escapar. Aluno com 20/25 precisaria de apenas 2%.

**Prós**: granularidade máxima, usa a informação mais rica disponível.
**Contras**: requer integrar o CSV do placement ao script de avaliação; os pesos da fórmula são especulativos sem dados de validação.

---

## 3. Limitação fundamental que nenhuma opção resolve

O placement exam mede **proficiência de leitura**, não **conhecimento do vocabulário específico dos baralhos**. Um aluno Tier 1 pode conhecer a palavra "winger" se for fã de futebol. Um aluno Tier 2 pode já saber as músicas usadas no Component C de cor.

As únicas formas de distinção definitiva são:

- **Pré-teste de vocabulário** específico do baralho antes do exercício começar
- **Análise de tempo por cartão** (LOW_TIME já tenta isso, de forma grosseira)
- **Avaliação presencial**

O placement como parâmetro reduz a chance de falso positivo, mas não elimina. O julgamento pedagógico do professor continua sendo o árbitro final nos casos limítrofes.

---

## 4. Recomendação para o próximo semestre

1. **Não implementar ainda** — o impacto prático em E04 seria zero (todos os penalizados são Tier 1, não há Tier 3 na turma).
2. **Coletar mais dados**: acompanhar nos próximos exercícios se surgem casos de RET100_CAP em Tier 2, e se o professor avalia esses casos como legítimos ou suspeitos.
3. **Se a turma crescer ou mudar de perfil**: reavaliar a Opção A como primeira implementação — baixo custo, sem risco de regressão no script.
4. **Validação pós-semestre**: cruzar os scores do placement com o desempenho acumulado em E01–E04 para verificar se o tier prediz bem o comportamento de retenção (análise sugerida na seção 9.2 do `PLACEMENT_EXAM_RESULTS_ANALYSIS.md`, prevista para junho 2026).

---

*Referências: `PLAN_E04.md`, `E04_Final_Results_Analysis.md`, `PLACEMENT_EXAM_RESULTS_ANALYSIS.md`, `PLAN_FOR_PLACEMENT_EXAM_v1.2.md`*
