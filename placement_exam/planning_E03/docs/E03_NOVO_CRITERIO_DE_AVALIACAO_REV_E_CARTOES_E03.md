# E03 — Novo Critério de Avaliação: Revisões e Cartões

## 1. Contexto

O Exercício 03 (E03) orienta os alunos a criarem cartões de vocabulário seguindo o método Tier 1 ou Tier 2:

- **Tier 1**: Frente com frase em inglês contendo cloze `[MAIÚSCULO]`; verso com `palavra = tradução`.
- **Tier 2**: Frente com frase + cloze + classe gramatical `(n.)/(v.)/(adj.)`; verso com classe gramatical, marcador de colocação e tradução.

Nem todos os alunos seguem essas convenções à risca. Este documento registra os ajustes de critério adotados para avaliar de forma justa esses casos.

---

## 2. Marcador de colocação: aceitação de variantes

O modelo de instrução usa o símbolo ☞ (dedinho) para indicar colocações no verso do cartão. Porém, **qualquer marcador visual** que destaque a colocação é aceito sem desconto de pontos:

| Marcador | Exemplo | Aceito? |
|----------|---------|---------|
| `☞`      | ☞ play football | Sim |
| `-->`    | --> play football | Sim |
| `->`     | -> play football | Sim |
| `--->`   | ---> play football | Sim |
| `•`      | • play football | Sim |

O importante é que o aluno sinalize de alguma forma a colocação — o símbolo específico não importa.

---

## 3. Caso especial: cartões sem formatação Tier 1/Tier 2

### Situação observada

Alguns alunos (ex.: Mateus Ferreira Patrício, Tier 2) criam cartões que **não** seguem a formatação do método, mas que demonstram aprendizado válido:

- **Frente**: frase ou expressão em inglês (sem cloze, sem classe gramatical)
- **Verso**: tradução em português

Exemplo típico:

```
Frente: "The game looks more like an art form than a sport"
Verso:  "O jogo parece mais uma forma de arte do que um esporte"
```

### Critério aplicado

O objetivo principal da avaliação é **medir aprendizado** (Objetivo 1), não apenas aderência rígida ao formato. Portanto:

- Cartões com inglês na frente e tradução válida em português no verso recebem **crédito parcial** no critério de formato do verso (1/2 pontos ao invés de 0/2).
- O aluno ainda perde 1 ponto por não incluir classe gramatical e/ou marcador de colocação, mas **não é zerado**.
- Isso garante que um aluno que demonstra esforço real de tradução e estudo atinja no mínimo ~60% no score de qualidade de cartões.

### Justificativa

- O aluno criou cartões, revisou-os e demonstrou compreensão do conteúdo.
- A ausência de formatação T2 indica falta de aderência ao método, mas não ausência de aprendizado.
- Zerar o verso (0/2) por falta de formatação penaliza excessivamente quem de fato estudou.

---

## 4. Resumo das regras de pontuação (verso — Tier 2)

| Conteúdo do verso | Pontuação | Justificativa |
|---|---|---|
| Classe gramatical + marcador de colocação | 2/2 | Formatação T2 completa |
| Apenas classe gramatical | 1/2 | Parcial — falta colocação |
| Apenas marcador de colocação (qualquer variante) | 1/2 | Parcial — falta classe |
| Tradução válida sem formatação T2 | 1/2 | Crédito parcial por aprendizado |
| Verso vazio | 0/2 | Nenhum esforço |

---

## 5. Penalidade RET100_CAP: retenção perfeita sem amadurecimento

### Situação observada

Alguns alunos apresentam **100% de retenção** (zero erros em ≥ 30 revisões) mas **0% de maturidade** — nenhum cartão atingiu intervalo ≥ 21 dias. Isso é estatisticamente improvável no SM-2: com revisões espaçadas reais, alguns cartões deveriam amadurecer ao longo de 29 dias. O padrão sugere resposta automática sem leitura efetiva do cartão.

### Critério aplicado

Quando um aluno apresenta **simultaneamente**:
- Retenção = 100% (com ≥ 30 revisões)
- Maturidade < 10%

A nota final é **limitada a 40 pontos** (máximo). O flag `RET100_CAP` é registrado.

### Não penalizados

Alunos com RET100 mas maturidade ≥ 10% **não são afetados** — a maturidade alta evidencia aprendizado genuíno consolidado ao longo do tempo:

| Aluno | Retenção | Maturidade | Penalizado? |
|-------|----------|------------|-------------|
| Madson Ferreira de Souza | 100% | 100.0% | Não |
| Laís Nascimento Silva | 100% | 87.2% | Não |
| Matheus Dias Gomes | 100% | 11.7% | Não |
| Ana Luiza Camilo da Silva | 100% | 0% | **Sim — nota 40** |
| Philipe Emanuel de Souza Meireles | 100% | 0% | **Sim — nota 40** |
| Lenilson Maia Rodrigues de Lima | 100% | 0% | **Sim — nota 40** |

### Justificativa

- O SM-2 aumenta progressivamente o intervalo a cada acerto: 1d → 3d → 7d → 15d → 33d (maduro). Com 29 dias de exercício e acerto consistente, cartões criados nas primeiras semanas deveriam amadurecer.
- Maturidade 0% com 100% acerto indica que o aluno não deu tempo para o espaçamento funcionar (ex.: criou tudo no final) ou respondeu sem engajamento real.
- O cap em 40 (F) reflete que, embora tenha havido atividade, não há evidência de aprendizado espaçado efetivo.

---

## 6. Impacto nos resultados

Após aplicação de todos os critérios ao snapshot de 18/05/2026:

**Qualidade de cartões** (`assess_card_quality.py`):
- Score médio geral de aderência: **89.0%**
- Mateus Ferreira Patrício: **64.8%** (antes: 48.1%)
- Zero cartões classificados como "baixa qualidade" (<33%)

**Penalidade RET100_CAP** (`grade_exercise_v2.py`):
- Ana Luiza Camilo da Silva: 80.5 → **40.0** (B → F)
- Philipe Emanuel de Souza Meireles: 69.8 → **40.0** (D → F)
- Lenilson Maia Rodrigues de Lima: 59.1 → **40.0** (F → F)
- Nota média da turma: 64.2 → **61.9**
- Distribuição: A=3, B=2, C=3, D=13, F=18
